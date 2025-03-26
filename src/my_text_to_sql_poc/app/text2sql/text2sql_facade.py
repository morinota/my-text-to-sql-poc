from pathlib import Path

import duckdb
from langchain_community.docstore.document import Document
from langchain_community.vectorstores import DuckDB
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway

PROMPT_CONFIG = OmegaConf.load("prompts/generate_sql_prompt_ver2_jp.yaml")


# 出力データのフォーマットを設定
class OutputFormat(BaseModel):
    query: str = Field(
        description="生成されたSQLクエリ。コマンドは大文字ではなく小文字で書くこと。可読性を重視して改行すること。CTEの名前はアンダースコアから始めること。可読性を重視して細かくコメントによる説明を挟むこと。"
    )
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


class Text2SQLFacade:
    GENERATER_PROMPT_TEMPLATE = Path("prompts/generate_sql_prompt_ver2_jp.txt")
    REVIEWER_PROMPT_TEMPLATE = Path("prompts/generate_sql_prompt_ver2_jp.yaml")

    def __init__(
        self,
        vector_db_path: str = "sample_vectorstore.duckdb",
        model_name: str = "text-embedding-3-small",
        table_metadata_dir: Path = Path("data/table_metadata/"),
        sample_query_dir: Path = Path("data/sample_queries/"),
    ):
        self.vector_db_path = vector_db_path
        self.model_name = model_name
        self.table_metadata_dir = table_metadata_dir
        self.sample_query_dir = sample_query_dir
        self.model_gateway = ModelGateway()

        prompt_config = OmegaConf.load(self.REVIEWER_PROMPT_TEMPLATE)
        self.reviewer_prompt_template = ChatPromptTemplate(
            messages=[(message.role, message.content) for message in prompt_config.reviewer_prompt.messages]
        )

    def all_process(self, question: str, dialect: str) -> tuple[str, str]:
        """
        自然言語の質問からSQLクエリと説明文を生成する、一連の処理を実行します
        """
        # Retrieve relevant tables
        related_metadata_by_table = self.retrieve_related_tables(question, k=20)
        tables_metadata = "\n\n".join(related_metadata_by_table.values())
        logger.info(f"Retrieved tables: {related_metadata_by_table.keys()}")

        # Retrieve related sample queries
        related_sql_by_query_name = self.retrieve_related_sample_queries(question, k=10)
        related_sample_queries = "\n\n".join(related_sql_by_query_name.values())
        logger.info(f"Retrieved sample queries: {related_sql_by_query_name.keys()}")

        # Generate SQL query and explanation
        sql_query = self.text2sql(question, dialect, tables_metadata, related_sample_queries)
        return sql_query, ""

    def retrieve_related_tables(self, question: str, k: int = 20) -> dict[str, str]:
        """質問に関連するテーブルをretrieveして返す
        返り値dictの key はテーブル名、value はテーブルのスキーマ
        """
        retrieved_table_names = [
            Path(doc.metadata["source"]).stem
            for doc in self._retrieve_relevant_docs(question, table_name="table_embeddings", k=k)
        ]

        metadata_by_table = self._load_selected_table_metadata(retrieved_table_names)
        return metadata_by_table

    def retrieve_related_sample_queries(self, question: str, k: int = 20) -> dict[str, str]:
        """質問に関連するサンプルクエリをretrieveして返す
        返り値dictの key はサンプルクエリ名、value はサンプルクエリの内容
        """
        retrieved_query_names = [
            Path(doc.metadata["source"]).stem
            for doc in self._retrieve_relevant_docs(question, table_name="query_embeddings", k=k)
        ]

        related_sample_queries = self._load_selected_sample_queries(retrieved_query_names)
        return related_sample_queries

    def text2sql(
        self,
        question: str,
        dialect: str,
        tables_metadata: str,
        related_sample_queries: str,
    ) -> tuple[str, str]:
        """質問文からSQLクエリを生成する"""
        text2sql_output = self._generate_sql_query(
            dialect=dialect,
            question=question,
            tables_metadata=tables_metadata,
            related_sample_queries=related_sample_queries,
        )
        return text2sql_output.query, text2sql_output.explanation

    def _retrieve_relevant_docs(self, question: str, table_name: str, k: int = 5) -> list[Document]:
        """ベクトルストアを読み込み、質問に関連するドキュメントをretrieveする"""
        embeddings = OpenAIEmbeddings(model=self.model_name)
        conn = duckdb.connect(database=self.vector_db_path)
        vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
        return vectorstore.similarity_search(question, k=k)

    def _load_selected_table_metadata(self, table_names: list[str]) -> dict[str, str]:
        """テーブルスメタデータを読み込んで、dict形式で返す"""
        metadata_by_table = {}
        available_tables = [file.stem for file in self.table_metadata_dir.glob("*.txt")]

        for table_name in table_names:
            file_path = self.table_metadata_dir / f"{table_name}.txt"
            if table_name not in available_tables or not file_path.exists():
                # raise FileNotFoundError(
                #     f"Schema file not found for table: {table_name}\n Available tables: {available_tables}"
                # )
                logger.warning(f"Schema file not found for table: {table_name}\n Available tables: {available_tables}")
                continue
            with file_path.open("r") as file:
                table_data = file.read()
                metadata_by_table[table_name] = table_data
        return metadata_by_table

    def _load_selected_sample_queries(self, query_names: list[str]) -> dict[str, str]:
        """サンプルクエリを読み込んで、dict形式で返す"""
        sql_by_query_name = {}
        available_queries = [file.stem for file in self.sample_query_dir.glob("*.sql")]

        for query_name in query_names:
            file_path = self.sample_query_dir / f"{query_name}.sql"
            if query_name not in available_queries or not file_path.exists():
                raise FileNotFoundError(
                    f"Sample query file not found for query: {query_name}\n Available queries: {available_queries}"
                )
            with file_path.open("r") as file:
                query_data = file.read()
                sql_by_query_name[query_name] = query_data
        return sql_by_query_name

    def _generate_sql_query(
        self, dialect: str, question: str, tables_metadata: str, related_sample_queries: str
    ) -> OutputFormat:
        """質問文からSQLクエリを生成する"""
        prompt_template_str = self.GENERATER_PROMPT_TEMPLATE.read_text()

        prompt_template = PromptTemplate(
            template=prompt_template_str,
            input_variables=["dialect", "table_schemas", "original_query", "question", "related_sample_queries"],
        )
        prompt = prompt_template.format(
            dialect=dialect,
            table_schemas=tables_metadata,
            original_query=question,
            question=question,
            related_sample_queries=related_sample_queries,
        )
        return self.model_gateway.generate_response_with_structured_output(
            prompt,
            OutputFormat,
        )

    def _output_guardrails(
        self,
        question: str,
        dialect: str,
        tables_metadata: str,
        related_sample_queries: str,
        generated_sql_query: str,
        explanation: str,
    ) -> str:
        """生成されたSQLクエリに対するガードレールを適用して返す"""
        reviewer_prompt = self.reviewer_prompt_template.format(
            question=question,
            dialect=dialect,
            tables_metadata=tables_metadata,
            related_sample_queries=related_sample_queries,
            sql_query=generated_sql_query,
            explanation=explanation,
        )

        # reviewが生成したクエリをレビューして、問題があれば修正する
        reviewed_output = self.model_gateway.generate_response_with_structured_output(reviewer_prompt, OutputFormat)

        return reviewed_output.query
