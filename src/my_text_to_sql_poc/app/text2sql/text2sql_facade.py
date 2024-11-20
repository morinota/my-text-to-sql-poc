import json
from pathlib import Path

import duckdb
import typer
from langchain_community.docstore.document import Document
from langchain_community.vectorstores import DuckDB
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway

app = typer.Typer(pretty_exceptions_enable=False)  # Typerアプリケーションのインスタンスを作成

MODEL_NAME = "text-embedding-3-small"
VECTOR_DB_PATH = "sample_vectorstore.duckdb"
TABLE_METADATA_DIR = Path("data/table_metadata/")
SAMPLE_QUERY_DIR = Path("data/sample_queries/")
PROMPT_CONFIG = OmegaConf.load("prompts/generate_sql_prompt_ver2_jp.yaml")


# 出力データのフォーマットを設定
class OutputFormat(BaseModel):
    query: str = Field(description="生成されたSQLクエリ")
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


class Text2SQLFacade:
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

    def process_query(self, question: str, dialect: str) -> tuple[str, str]:
        """
        自然言語の質問からSQLクエリと説明文を生成します。
        """
        # Retrieve relevant tables
        retrieved_table_names = [
            Path(doc.metadata["source"]).stem
            for doc in self._retrieve_relevant_docs(question, table_name="table_embeddings", k=20)
        ]
        print(retrieved_table_names)
        table_schemas = self._load_selected_table_metadata(retrieved_table_names)

        # Retrieve related sample queries
        retrieved_sample_queries = [
            Path(doc.metadata["source"]).stem
            for doc in self._retrieve_relevant_docs(question, table_name="query_embeddings", k=5)
        ]
        related_sample_queries = self._load_selected_sample_queries(retrieved_sample_queries)

        # Generate SQL query and explanation
        return self._generate_sql_query(dialect, question, table_schemas, related_sample_queries)

    def _retrieve_relevant_docs(self, question: str, table_name: str, k: int = 5) -> list[Document]:
        """ベクトルストアを読み込み、質問に関連するドキュメントをretrieveする"""
        embeddings = OpenAIEmbeddings(model=self.model_name)
        conn = duckdb.connect(database=self.vector_db_path)
        vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
        return vectorstore.similarity_search(question, k=k)

    def _load_selected_table_metadata(self, table_names: list[str]) -> str:
        """テーブルスメタデータを読み込んで、まとめて返す"""
        table_schemas = []
        available_tables = [file.stem for file in self.table_metadata_dir.glob("*.txt")]

        for table_name in table_names:
            file_path = self.table_metadata_dir / f"{table_name}.txt"
            if table_name not in available_tables or not file_path.exists():
                raise FileNotFoundError(
                    f"Schema file not found for table: {table_name}\n Available tables: {available_tables}"
                )
            with file_path.open("r") as file:
                table_data = file.read()
                table_schemas.append(table_data)
        return "\n\n".join(table_schemas)

    def _load_selected_sample_queries(self, query_names: list[str]) -> str:
        """サンプルクエリを読み込んで、まとめて返す"""
        sample_queries = []
        available_queries = [file.stem for file in self.sample_query_dir.glob("*.sql")]

        for query_name in query_names:
            file_path = self.sample_query_dir / f"{query_name}.sql"
            if query_name not in available_queries or not file_path.exists():
                raise FileNotFoundError(
                    f"Sample query file not found for query: {query_name}\n Available queries: {available_queries}"
                )
            with file_path.open("r") as file:
                query_data = file.read()
                sample_queries.append(query_data)
        return "\n\n".join(sample_queries)

    def _generate_sql_query(
        self, dialect: str, question: str, tables_metadata: str, related_sample_queries: str
    ) -> tuple[str, str]:
        prompt_template_str = Path("prompts/generate_sql_prompt_ver2_jp.txt").read_text()
        output_parser = JsonOutputParser(pydantic_object=OutputFormat)

        prompt_template = PromptTemplate(
            template=prompt_template_str + "\n\n{format_instructions}\n",
            input_variables=["dialect", "table_schemas", "original_query", "question", "related_sample_queries"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()},
        )
        prompt = prompt_template.format(
            dialect=dialect,
            table_schemas=tables_metadata,
            original_query=question,
            question=question,
            related_sample_queries=related_sample_queries,
        )
        response_text = self.model_gateway.generate_response(prompt)

        # レスポンスの本文からqueryフィールドとexplanationフィールドを取得
        ## 不要なバッククォートと「json」記法を削除(レスポンスにmarkdown記法のコードブロックが含まれることがあるため)
        cleaned_response_text = response_text.strip("```json").strip("```").strip()
        response_data = json.loads(cleaned_response_text)
        return response_data["query"], response_data.get("explanation", "")


# @app.command()
# def main(
#     question: str = typer.Option(..., help="The user's question (natural language)"),
#     dialect: str = typer.Option("SQLite", help="The SQL dialect to use (default is SQLite)"),
#     log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
# ) -> None:
#     """
#     自然言語の質問からSQLクエリを生成します。

#     Args:
#         question (str): ユーザーの質問（自然言語）
#         dialect (str): 使用するSQLの方言（デフォルトはSQLite）
#     """
#     # ログレベルを設定
#     logger.remove()  # デフォルトのログ設定を削除
#     logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

#     # ユーザクエリに関連するテーブル達をretrieve
#     retrieved_tables = [
#         _extract_document_name(doc)
#         for doc in retrieve_relevant_docs(question, VECTOR_DB_PATH, table_name="table_embeddings", k=20)
#     ]
#     logger.info(f"Retrieved tables: {retrieved_tables}")
#     table_schemas = load_selected_table_metadata(retrieved_tables)

#     # ユーザクエリに関連するサンプルクエリをretrieve
#     retrieved_sample_queries = [
#         _extract_document_name(doc)
#         for doc in retrieve_relevant_docs(question, VECTOR_DB_PATH, table_name="query_embeddings", k=5)
#     ]
#     logger.info(f"Retrieved sample queries: {retrieved_sample_queries}")
#     related_sample_queries = load_selected_sample_queries(retrieved_sample_queries)

#     sql_query, explanation = generate_sql_query(dialect, question, table_schemas, related_sample_queries)

#     logger.info(f"\nGenerated SQL Query:\n {sql_query}")
#     if explanation:
#         logger.info(f"\nExplanation:\n {explanation}")

#     logger.info("SQL query generation process completed")


# if __name__ == "__main__":
#     app()
