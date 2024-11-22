from pathlib import Path

import polars as pl
import typer
from langchain_core.prompts import PromptTemplate
from loguru import logger

from my_text_to_sql_poc.app.generate_table_metadata_batch.table_metadata_model import TableMetadataSchema
from my_text_to_sql_poc.service.model_gateway import ModelGateway

app = typer.Typer()


# プロンプトの設定
METADATA_PROMPT_PATH = Path("prompts/generate_table_metadata_jp.txt")
# 対象テーブル一覧


def generate_table_metadata(
    table_name: str,
    related_queries: list[str],
) -> TableMetadataSchema:
    """対象テーブルのスキーマ情報と、対象テーブルを利用してるサンプルクエリ達を元に、LLMにテーブルメタデータを生成させる"""
    prompt_template_str = METADATA_PROMPT_PATH.read_text()
    prompt_template = PromptTemplate(
        template=prompt_template_str,
        input_variables=["table_name", "audit_logs"],
    )

    formatted_prompt = prompt_template.format(
        table_name=table_name,
        audit_logs="\n\n".join(related_queries),
    )

    return ModelGateway().generate_response_with_structured_output(formatted_prompt, TableMetadataSchema)


@app.command()
def main(
    sample_queries_dir: Path = typer.Option(..., help="Directory containing sample queries"),
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

    # サンプルクエリ一覧を取得
    sample_query_texts = [file.read_text() for file in sample_queries_dir.glob("*.sql")]

    for table_name in TARGET_TABLES:
        logger.info(f"Processing table: {table_name}")

        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        output_path = table_metadata_dir / f"{table_name}.txt"
        if not full_refresh and output_path.exists():
            logger.info(f"Table Metadata for {table_name} already exists, skipping")
            continue

        # audit_logから対象テーブルを使用してるクエリのみを抽出する (一旦setにして重複を除去)
        related_queries = list(set([query for query in sample_query_texts if table_name in query]))

        table_metadata = generate_table_metadata(
            table_name,
            related_queries[0:100],  # input tokenのサイズ制限のため、100件までにしておく
        )

        output_path.write_text(table_metadata)


def _remove_prefix_query(query: str) -> str:
    """
    WITHまたはSELECT以前の文字列を削除
    """
    if "WITH" in query.upper():
        return query[query.upper().index("WITH") :]
    elif "SELECT" in query.upper():
        return query[query.upper().index("SELECT") :]
    return query


if __name__ == "__main__":
    # app()

    table_name = "subscription_events"
    # sample_queries_dir = Path("data/sample_queries")
    # sample_query_texts = [file.read_text() for file in sample_queries_dir.glob("*.sql")]

    sample_queries_dir = Path("data/sample_queries")
    related_queries = [file.read_text() for file in sample_queries_dir.glob("*.sql") if table_name in file.read_text()]
    table_metadata = generate_table_metadata(
        table_name,
        related_queries[0:100],  # input tokenのサイズ制限のため、100件までにしておく
    )
    metadata_json = table_metadata.model_dump_json(indent=2)
    print(metadata_json)
    Path(f"temp_table_metadata_{table_name}.json").write_text(metadata_json)
