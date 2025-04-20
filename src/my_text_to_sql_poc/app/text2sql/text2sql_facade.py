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
from my_text_to_sql_poc.service.repository import (
    DuckDBSampleQueryRepository,
    DuckDBTableMetadataRepository,
    SampleQueryRepository,
    SampleQueryRepositoryInterface,
    TableMetadataRepository,
    TableMetadataRepositoryInterface,
    VectorStoreRepository,
    VectorStoreRepositoryInterface,
)

PROMPT_CONFIG = OmegaConf.load("src/my_text_to_sql_poc/app/text2sql/generate_sql_prompt_ver2_jp.yaml")


# 出力データのフォーマットを設定
class OutputFormat(BaseModel):
    query: str = Field(
        description="生成されたSQLクエリ。コマンドは大文字ではなく小文字で書くこと。可読性を重視して改行すること。CTEの名前はアンダースコアから始めること。可読性を重視して細かくコメントによる説明を挟むこと。"
    )
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


class Text2SQLFacade:
    GENERATER_PROMPT_TEMPLATE = Path("src/my_text_to_sql_poc/app/text2sql/generate_sql_prompt_ver2_jp.txt")
    REVIEWER_PROMPT_TEMPLATE = Path("src/my_text_to_sql_poc/app/text2sql/generate_sql_prompt_ver2_jp.yaml")

    def __init__(
        self,
        vector_store_repo: VectorStoreRepositoryInterface = VectorStoreRepository(),
        table_metadata_repo: TableMetadataRepositoryInterface = DuckDBTableMetadataRepository(),
        sample_query_repo: SampleQueryRepositoryInterface = DuckDBSampleQueryRepository(),
    ):
        self.vector_store_repo = vector_store_repo
        self.table_metadata_repo = table_metadata_repo
        self.sample_query_repo = sample_query_repo
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
        sql_query, explanation = self.text2sql(question, dialect, tables_metadata, related_sample_queries)
        return sql_query, explanation

    def retrieve_related_tables(self, question: str, k: int = 20) -> dict[str, str]:
        """質問に関連するテーブルをretrieveして返す
        返り値dictの key はテーブル名、value はテーブルのスキーマ
        """
        retrieved_table_names = [
            Path(doc.metadata["source"]).stem
            for doc in self.vector_store_repo.retrieve_relevant_docs(question, table_name="table_embeddings", k=k)
        ]
        return self.table_metadata_repo.get(retrieved_table_names)

    def retrieve_related_sample_queries(self, question: str, k: int = 20) -> dict[str, str]:
        """質問に関連するサンプルクエリをretrieveして返す
        返り値dictの key はサンプルクエリ名、value はサンプルクエリの内容
        """
        retrieved_query_names = [
            Path(doc.metadata["source"]).stem
            for doc in self.vector_store_repo.retrieve_relevant_docs(question, table_name="query_embeddings", k=k)
        ]
        return self.sample_query_repo.get(retrieved_query_names)

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
