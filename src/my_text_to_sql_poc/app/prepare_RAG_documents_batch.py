import re

from loguru import logger
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway
from my_text_to_sql_poc.service.repository import (
    DuckDBSampleQueryRepository,
    DuckDBTableMetadataRepository,
    DuckDBVectorStoreRepository,
    SampleQueryRepositoryInterface,
    TableMetadataRepositoryInterface,
    VectorStoreRepositoryInterface,
)

PROMPT_SUMMARIZE_TABLE = """
あなたはSQLテーブルの要約を手助けするデータアナリストです。

以下のテーブルを、指定されたコンテキストに基づいて要約してください。

===テーブルスキーマ
{table_schema}

===サンプルクエリ
{sample_queries}

===応答ガイドライン

- 言語は日本語で記載してください
- 提供された情報に基づいて要約を記述してください。
- 上記のサンプルクエリはクエリの一部であり、すべてのテーブル利用方法を網羅しているわけではないため、一部の列のみが使用されています。
- テーブルの重要性や包括性、また誰が使用するかなど、形容詞を用いてテーブルを評価しないでください。たとえば、「テーブルには特定の種類のデータが含まれている」とは言えますが、「豊富なデータが含まれている」や「包括的なテーブルである」などの記述は避けてください。
- サンプルクエリについては触れず、テーブルが含むデータの種類とその可能な用途のみを客観的に記載してください。
- テーブルの潜在的な利用用途も記載してください（例：どのような質問に回答できるか、どのような分析が可能か、など）。
"""

PROMPT_SUMMARIZE_QUERY = """
あなたはSQLクエリのドキュメント作成を手助けするアシスタントです。

以下のSQLクエリを、指定されたテーブルスキーマに基づいてドキュメント化してください。

===SQLクエリ
{query}

===テーブルスキーマ
{table_schemas}

===応答ガイドライン

- 言語は日本語で記載してください
- 提供された情報に基づいて要約を記述してください。
- クエリの目的や意図を詳細に記載
- クエリの可能なビジネス上または機能的な目的についても記載
- 選択されている列とその説明
- クエリの入力テーブルとその結合パターン
- クエリの詳細な変換ロジックをわかりやすい日本語で説明し、なぜそれが必要なのかを記載
- クエリで行われているフィルターの種類と、なぜそれが必要なのか
"""


class TableSummary(BaseModel):
    name: str = Field(description="テーブル名")
    summary: str = Field(description="テーブルの概要")
    utilization: str = Field(
        description="テーブルの利用状況。そのテーブルがどのような質問に答えられるか、そのテーブルでどのような分析ができるか、など"
    )
    potential_usecases: str = Field(description="テーブルの潜在的な利用用途")


class SQLQuerySummary(BaseModel):
    purposes: str = Field(description="クエリの目的や意図を詳細に記載")
    selected_columns: str = Field(description="クエリ内で選択されてるカラムとその概要")
    input_tables: str = Field(description="クエリ内で使用されてるテーブルとその概要")
    detailed_transformation_logics: str = Field(description="クエリ内で行われてるデータ加工の詳細")


class RAGDocumentPreparer:
    def __init__(
        self,
        table_metadata_repository: TableMetadataRepositoryInterface = DuckDBTableMetadataRepository(),
        sample_query_repository: SampleQueryRepositoryInterface = DuckDBSampleQueryRepository(),
        vector_store_repository: VectorStoreRepositoryInterface = DuckDBVectorStoreRepository(),
    ):
        self._table_metadata_repository = table_metadata_repository
        self._sample_query_repository = sample_query_repository
        self._repository = vector_store_repository

    def register_table_metadata(self) -> None:
        """Text2SQL用のRAGのためにテーブルメタデータを要約し、それをドキュメントとしてベクトルストアに登録する"""
        table_metadata_by_name = self._table_metadata_repository.get_all()

        for table_name, metadata in table_metadata_by_name.items():
            related_sample_queries = self._sample_query_repository.retrieve_by_table_name(table_name)
            table_summary = self._generate_table_summary(
                table_name=table_name,
                table_metadata=metadata,
                sample_queries=set(related_sample_queries.values()),
            )
            self._repository.put(doc_id=table_name, document=table_summary, table_name="table_embeddings")

    def register_sample_queries(self) -> None:
        """Text2SQL用のRAGのためにサンプルクエリを要約し、それをドキュメントとしてベクトルストアに登録する"""
        sample_queries = self._sample_query_repository.get_all()

        for query_name, query in sample_queries.items():
            # サンプルクエリの要約を生成
            related_tables = self._extract_related_tables(query)
            query_summary = self._generate_query_summary(
                query=query,
                related_tables=related_tables,
            )
            self._repository.put(doc_id=query_name, document=query_summary, table_name="query_embeddings")

    def _generate_table_summary(
        self,
        table_name: str,
        table_metadata: str,
        sample_queries: set[str],
    ) -> str:
        formatted_prompt = PROMPT_SUMMARIZE_TABLE.format(
            table_schema=table_metadata,
            sample_queries="\n".join(sample_queries),
        )
        logger.debug(f"Formatted table schema prompt for {table_name}: {formatted_prompt}")

        response_obj = ModelGateway().generate_response_with_structured_output(formatted_prompt, TableSummary)
        return response_obj.model_dump_json(indent=2)

    def _generate_query_summary(self, query: str, related_tables: set[str]) -> str:
        table_schemas = "\n\n".join(
            [self._table_metadata_repository.get([table]).get(table, "") for table in related_tables]
        )

        formatted_prompt = PROMPT_SUMMARIZE_QUERY.format(
            query=query,
            table_schemas=table_schemas,
        )
        logger.debug(f"Formatted query prompt: {formatted_prompt}")

        response_obj = ModelGateway().generate_response_with_structured_output(formatted_prompt, SQLQuerySummary)
        return response_obj.model_dump_json(indent=2)

    def _extract_related_tables(self, query: str) -> set[str]:
        """SQLクエリから関連するテーブル名を抽出する"""
        # FROM、JOINキーワードの後に続くテーブル名を正規表現で取得(スキーマを含む)
        TABLE_PATTERN = re.compile(r"(?:FROM|JOIN)\s+(\w+(?:\.\w+)?)", re.IGNORECASE)
        # CTE(Common Table Expression, with句で定義される一時テーブル)を除外
        CTE_PATTERN = re.compile(r"WITH\s+(\w+)\s+AS", re.IGNORECASE)
        table_names = set()

        matche_tables = set(TABLE_PATTERN.findall(query))
        cte_tables = set(CTE_PATTERN.findall(query))
        for match_table in matche_tables:
            # CTEの場合はスキップ
            if match_table in cte_tables:
                continue
            table_names.add(match_table.lower())  # 重複テーブル名を避けるために小文字化

        return table_names
