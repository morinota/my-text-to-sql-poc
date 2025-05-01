from pathlib import Path

import typer
from loguru import logger

from my_text_to_sql_poc.app.generate_table_metadata_batch.table_metadata_generator import generate_table_metadata
from my_text_to_sql_poc.service.repository import (
    DuckDBSampleQueryRepository,
    DuckDBTableMetadataRepository,
    SampleQueryRepositoryInterface,
    TableMetadataRepositoryInterface,
)

app = typer.Typer(pretty_exceptions_enable=False)


class TableMetadataGenerator:
    def __init__(
        self,
        table_metadata_repo: TableMetadataRepositoryInterface = DuckDBTableMetadataRepository(),
        sample_query_repo: SampleQueryRepositoryInterface = DuckDBSampleQueryRepository(),
    ):
        self.table_metadata_repo = table_metadata_repo
        self.sample_query_repo = sample_query_repo

    def generate(self, table_name: str) -> None:
        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        if not full_refresh and output_path.exists():
            logger.info(f"Table Metadata for {table_name} already exists, skipping")
            return

        # サンプルクエリを取得
        related_queries = self.sample_query_repo.get_related_queries(table_name, sample_queries_dir)
        logger.info(f"Found {len(related_queries)} related queries for {table_name}")

        # メタデータ生成
        table_metadata = generate_table_metadata(
            table_name,
            related_queries[0:100],  # input tokenのサイズ制限のため、100件までにしておく
            reffered_doc,
            self.table_metadata_repo,
        )

        output_path.write_text(table_metadata.model_dump_json(indent=2))


@app.command()
def main(
    target_tables: list[str] = typer.Option(
        ...,
        help="""
        LLMにSQLクエリ履歴からメタデータを生成させたいテーブル名を指定する。
        指定方法: --target-tables table_name1 --target-tables table_name2 --target-tables table_name3
        """,
    ),
):
    table_metadata_generator = TableMetadataGenerator()
    for table_name in target_tables:
        logger.info(f"Processing table: {table_name}")
        table_metadata_generator.generate(table_name)


if __name__ == "__main__":
    app()
