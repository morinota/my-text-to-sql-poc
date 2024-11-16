import re
from pathlib import Path

import polars as pl
import typer
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from loguru import logger

from my_text_to_sql_poc.app.generate_table_metadata_batch.table_metadata_model import TableMetadataSchema
from my_text_to_sql_poc.service.model_gateway import ModelGateway

app = typer.Typer()


# プロンプトの設定
METADATA_PROMPT_PATH = Path("prompts/generate_table_metadata_jp.txt")
# 対象テーブル一覧
TARGET_TABLES = [
    "show_article_events",
    # "tap_article_events",
    # "access_latest",
    # "allocation_settings_detail",
    # "launch_events",
    # "movie_events_v2",
    # "subscription_events",
    # "user_subscription_histories",
    # "users_events",
    # "rds__newspicks.user_billing_users",
]


def _generate_table_metadata(
    table_name: str,
    related_queries: list[str],
) -> str:
    """対象テーブルのスキーマ情報と、対象テーブルを利用してるサンプルクエリ達を元に、LLMにテーブルメタデータを生成させる"""
    output_parser = JsonOutputParser(pydantic_object=TableMetadataSchema)

    prompt_template_str = METADATA_PROMPT_PATH.read_text()
    prompt_template = PromptTemplate(
        template=prompt_template_str + "\n\n{format_instructions}",
        input_variables=["table_name", "sample_queries"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    formatted_prompt = prompt_template.format(
        table_name=table_name,
        sample_queries="\n\n".join(related_queries),
    )

    response_text = ModelGateway().generate_response(formatted_prompt)

    summary = response_text.replace("\\n", "\n")

    return summary


@app.command()
def main(
    audit_log_path: Path = typer.Option(..., help="Path to the audit log CSV file"),
    table_metadata_dir: Path = typer.Option(..., help="Output directory for summarized table schemas"),
    full_refresh: bool = typer.Option(False, help="Force full refresh of all summaries"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
):
    # ログレベルを設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # 出力ディレクトリが存在しない場合は作成
    if not table_metadata_dir.exists():
        table_metadata_dir.mkdir(parents=True)

    # 洗い替えモードの場合は、サマリ生成前にdocumentsの保存先を空にしておく
    logger.info(f"mode: {full_refresh=}")
    if full_refresh:
        for file in table_metadata_dir.glob("*.txt"):
            file.unlink()

    # audit_logを読み込む
    audit_log_df = pl.read_csv(audit_log_path)

    for table_name in TARGET_TABLES:
        logger.info(f"Processing table: {table_name}")

        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        output_path = table_metadata_dir / f"{table_name}.txt"
        if not full_refresh and output_path.exists():
            logger.info(f"Table Metadata for {table_name} already exists, skipping")
            continue

        # audit_logから対象テーブルを使用してるクエリのみを抽出する (一旦setにして重複を除去)
        related_queries = list(set([query for query in audit_log_df["querytxt"] if table_name in query]))

        table_metadata = _generate_table_metadata(
            table_name,
            related_queries[0:100],  # input tokenのサイズ制限のため、100件までにしておく
        )

        output_path.write_text(table_metadata)


if __name__ == "__main__":
    app()
    # table_name = "show_article_events"
    # audit_log_df = pl.read_csv("data/redshift_audit_log.csv")

    # # audit_logから対象テーブルを使用してるクエリのみを抽出する
    # related_queries = [query for query in audit_log_df["querytxt"] if table_name in query]
    # print(len(related_queries))
    # print(len(set(related_queries)))

    # table_metadata = _generate_table_metadata(
    #     table_name,
    #     related_queries[0:100],
    # )
    # print(table_metadata)
