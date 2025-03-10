from pathlib import Path

import typer
from loguru import logger

from my_text_to_sql_poc.app.generate_table_metadata_batch.table_metadata_generator import generate_table_metadata

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def main(
    sample_queries_dir: Path = typer.Option(..., help="Directory containing sample queries"),
    table_metadata_dir: Path = typer.Option(..., help="Output directory for summarized table schemas"),
    target_tables: list[str] = typer.Option(None, help="Target tables to generate metadata for"),
    full_refresh: bool = typer.Option(False, help="Force full refresh of all summaries"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
):
    # ログレベルを設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    if not target_tables:
        raise ValueError(
            "target_tables引数は必須です。指定方法: --target-tables table_name1 --target-tables table_name2 --target-tables table_name3"
        )

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

    for table_name in target_tables:
        logger.info(f"Processing table: {table_name}")

        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        output_path = table_metadata_dir / f"{table_name}.txt"
        if not full_refresh and output_path.exists():
            logger.info(f"Table Metadata for {table_name} already exists, skipping")
            continue

        # 対象テーブルを使用してるクエリを検索してくる (一旦setにして重複を除去)
        related_queries = list(set([query for query in sample_query_texts if table_name in query]))
        logger.info(f"Found {len(related_queries)} related queries for {table_name}")

        # 人手で作られたテーブルの説明文を取得
        reffered_doc_path = Path(f"data/table_docs/{table_name}.csv")

        if reffered_doc_path.exists():
            reffered_doc = reffered_doc_path.read_text()
            logger.info(f"Found reference doc for {table_name}")
        else:
            reffered_doc = ""
            logger.warning(f"No reference doc found for {table_name}")

        table_metadata = generate_table_metadata(
            table_name,
            related_queries[0:100],  # input tokenのサイズ制限のため、200件までにしておく
            reffered_doc,
        )

        output_path.write_text(table_metadata.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
