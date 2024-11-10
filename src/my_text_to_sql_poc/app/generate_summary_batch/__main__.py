import json
import os
import re
from pathlib import Path

import openai
import typer
from loguru import logger

from my_text_to_sql_poc.service.model_gateway import ModelGateway  # ModelGatewayをインポート

app = typer.Typer()

# OpenAI APIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"


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


def extract_related_tables(query: str) -> set[str]:
    """
    SQLクエリから関連するテーブル名を抽出する関数。
    :param query: SQLクエリ文字列
    :return: 抽出されたテーブル名のリスト
    """
    table_names = set()
    # FROM、JOINキーワードの後に続くテーブル名を正規表現で取得
    table_pattern = re.compile(r"(?:FROM|JOIN)\s+(\w+)", re.IGNORECASE)

    matches = table_pattern.findall(query)
    for match in matches:
        table_names.add(match.lower())  # 重複テーブル名を避けるために小文字化

    return table_names


def summarize_table_schema(
    table_name: str,
    sample_queries: set[str],
    schema_dir: Path,
    prompt_path: Path,
) -> str:
    table_prompt = load_prompt(prompt_path)
    schema_path = schema_dir / f"{table_name}.json"

    try:
        with schema_path.open("r") as file:
            schema_data = json.load(file)

        formatted_prompt = table_prompt.format(
            table_schema=json.dumps(schema_data, indent=2),
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
    table_schemas = "\n".join([json.dumps(load_table_schema(table, schema_dir), indent=2) for table in related_tables])

    formatted_prompt = query_prompt.format(
        query=query,
        table_schemas=table_schemas,
    )
    logger.debug(f"Formatted query prompt: {formatted_prompt}")

    response_text = ModelGateway().generate_response(formatted_prompt)

    summary = response_text.replace("\\n", "\n")

    return summary


def load_table_schema(table_name: str, schema_dir: Path) -> dict:
    schema_path = schema_dir / f"{table_name}.json"
    with schema_path.open("r") as file:
        return json.load(file)


def _save_summary(file_path: Path, summary: str) -> None:
    with open(file_path, "w") as file:
        file.write(summary)
    logger.info(f"Saved summary to {file_path}")


@app.command()
def main(
    schema_dir: Path = typer.Option(..., help="Directory containing the table schemas"),
    sample_queries_dir: Path = typer.Option(..., help="Directory containing sample queries"),
    output_schema_dir: Path = typer.Option(..., help="Output directory for summarized table schemas"),
    output_queries_dir: Path = typer.Option(..., help="Output directory for summarized queries"),
    schema_prompt_path: Path = typer.Option("prompts/summarize_table_prompt.txt", help="Path to table schema prompt"),
    query_prompt_path: Path = typer.Option("prompts/summarize_query_prompt.txt", help="Path to query prompt"),
):
    table_names = [f.stem for f in schema_dir.glob("*.json")]
    for table in table_names:
        sample_queries = find_related_queries(table, sample_queries_dir)
        table_summary = summarize_table_schema(table, sample_queries, schema_dir, schema_prompt_path)
        _save_summary(output_schema_dir / f"{table}.txt", table_summary)

    query_files = sample_queries_dir.glob("*.sql")
    for query_file in query_files:
        with query_file.open() as f:
            query = f.read()
        related_tables = extract_related_tables(query)
        query_summary = summarize_query(query, related_tables, schema_dir, query_prompt_path)
        _save_summary(output_queries_dir / f"{query_file.stem}.txt", query_summary)


if __name__ == "__main__":
    app()
