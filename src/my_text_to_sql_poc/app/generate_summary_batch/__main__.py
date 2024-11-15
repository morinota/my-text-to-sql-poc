import json
import os
import re
from pathlib import Path

import openai
import typer
from loguru import logger

from my_text_to_sql_poc.service.model_gateway import ModelGateway
from my_text_to_sql_poc.service.related_table_extractor import extract_related_tables  # ModelGatewayをインポート

app = typer.Typer()

# OpenAI APIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"

# プロンプトの設定
QUERY_PROMPT_PATH = Path("prompts/summarize_query_prompt_jp.txt")
SCHEMA_PROMPT_PATH = Path("prompts/summarize_table_prompt_jp.txt")


def load_prompt(file_path: Path) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to load prompt from {file_path}: {e}")
        raise


def find_related_queries(table_name: str, sample_queries_dir: Path) -> set[str]:
    """
    指定されたテーブルに関連するサンプルクエリを取得する関数。
    :param table_name: 関連クエリを検索するテーブル名
    :param sample_queries_dir: サンプルクエリのディレクトリ
    :return: 関連するクエリのリスト
    """
    related_queries = set()
    table_pattern = re.compile(rf"\b{table_name}\b", re.IGNORECASE)

    for query_file in sample_queries_dir.glob("*.sql"):
        with query_file.open() as file:
            query = file.read()
            if table_pattern.search(query):
                related_queries.add(query)

    return related_queries


def summarize_table_schema(
    table_name: str,
    sample_queries: set[str],
    schema_dir: Path,
    prompt_path: Path,
) -> str:
    table_prompt = load_prompt(prompt_path)
    schema_path = schema_dir / f"{table_name}.txt"

    try:
        with schema_path.open("r") as file:
            schema_data = file.read()

        formatted_prompt = table_prompt.format(
            table_schema=schema_data,
            sample_queries="\n".join(sample_queries),
        )
        logger.debug(f"Formatted table schema prompt for {table_name}: {formatted_prompt}")

        response_text = ModelGateway().generate_response(formatted_prompt)

        summary = response_text.replace("\\n", "\n")

        return summary

    except Exception as e:
        logger.error(f"Error summarizing table schema for {table_name}: {e}")
        raise


def summarize_query(query: str, related_tables: set[str], schema_dir: Path, prompt_path: Path) -> str:
    query_prompt = load_prompt(prompt_path)
    table_schemas = "\n\n".join(
        [table_schema for table in related_tables if (table_schema := load_table_schema(table, schema_dir))]
    )

    formatted_prompt = query_prompt.format(
        query=query,
        table_schemas=table_schemas,
    )
    logger.debug(f"Formatted query prompt: {formatted_prompt}")

    response_text = ModelGateway().generate_response(formatted_prompt)

    summary = response_text.replace("\\n", "\n")

    return summary


def load_table_schema(table_name: str, schema_dir: Path) -> str | None:
    schema_path = schema_dir / f"{table_name}.txt"
    if not schema_path.exists():
        logger.warning(f"Schema file not found for table: {table_name}")
        return None
    with schema_path.open("r") as file:
        return file.read()


def _save_summary(file_path: Path, summary: str) -> None:
    with open(file_path, "w") as file:
        file.write(summary)
    logger.info(f"Saved summary to {file_path}")


@app.command()
def main(
    table_metadata_dir: Path = typer.Option(..., help="Directory containing the table metadata"),
    sample_queries_dir: Path = typer.Option(..., help="Directory containing sample queries"),
    output_table_summary_dir: Path = typer.Option(..., help="Output directory for summarized table schemas"),
    output_query_summary_dir: Path = typer.Option(..., help="Output directory for summarized queries"),
    full_refresh: bool = typer.Option(False, help="Force full refresh of all summaries"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
):
    # ログレベルを設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # 出力ディレクトリが存在しない場合は作成
    output_table_summary_dir.mkdir(parents=True, exist_ok=True)
    output_query_summary_dir.mkdir(parents=True, exist_ok=True)

    # 洗い替えモードの場合は、サマリ生成前にdocumentsの保存先を空にしておく
    logger.info(f"mode: {full_refresh=}")
    if full_refresh:
        for file in output_table_summary_dir.glob("*.txt"):
            file.unlink()
        for file in output_query_summary_dir.glob("*.txt"):
            file.unlink()

    table_names = [f.stem for f in table_metadata_dir.glob("*.txt")]
    for table in table_names:
        output_path = output_table_summary_dir / f"{table}.txt"
        logger.debug(f"Output path: {output_path}")
        # 差分更新チェック: すでにサマリファイルが存在している場合はスキップ
        if not full_refresh and output_path.exists():
            logger.info(f"Summary for {table} already exists, skipping")
            continue

        logger.info(f"Processing table: {table}")
        related_queries = find_related_queries(table, sample_queries_dir)
        table_summary = summarize_table_schema(table, related_queries, table_metadata_dir, SCHEMA_PROMPT_PATH)
        _save_summary(output_path, table_summary)

    query_files = sample_queries_dir.glob("*.sql")
    for query_file in query_files:
        output_path = output_query_summary_dir / f"{query_file.stem}.txt"
        # 差分更新チェック：既存ファイルがある場合はスキップ
        if not full_refresh and output_path.exists():
            logger.info(f"Skipping query {query_file.stem} as summary already exists")
            continue

        logger.info(f"Processing query: {query_file}")
        with query_file.open() as f:
            query = f.read()
        related_tables = extract_related_tables(query)
        query_summary = summarize_query(query, related_tables, table_metadata_dir, QUERY_PROMPT_PATH)
        _save_summary(output_path, query_summary)


if __name__ == "__main__":
    app()
