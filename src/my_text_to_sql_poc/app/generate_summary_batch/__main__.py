import json
import os
import re
from pathlib import Path

import openai
import typer
from loguru import logger

app = typer.Typer()

# OpenAI APIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"


# ディレクトリパス
SCHEMA_DIR = Path("data/schema")
SAMPLE_QUERIES_DIR = Path("data/sample_queries")
SUMMARIZED_SCHEMA_DIR = Path("data/summarized_schema")
SUMMARIZED_QUERIES_DIR = Path("data/summarized_sample_queries")
SUMMARIZED_SCHEMA_PROMPT_PATH = Path("prompts/summarize_table_prompt.txt")
SUMMARIZED_QUERY_PROMPT_PATH = Path("prompts/summarize_query_prompt.txt")


# プロンプトを読み込む関数
def load_prompt(file_path: Path) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Failed to load prompt from {file_path}: {e}")
        raise


def load_related_queries(table_name: str) -> set[str]:
    """
    指定されたテーブルに関連するサンプルクエリを読み込む関数。
    :param table_name: 関連クエリを検索するテーブル名
    :return: 関連するクエリのリスト
    """
    related_queries = set()
    table_pattern = re.compile(rf"\b{table_name}\b", re.IGNORECASE)

    for query_file in SAMPLE_QUERIES_DIR.glob("*.sql"):
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


# テーブルスキーマ要約の生成
def summarize_table_schema(table_name: str, sample_queries: set[str]) -> str:
    # テーブル要約プロンプトをロード
    table_prompt = load_prompt(SUMMARIZED_SCHEMA_PROMPT_PATH)
    schema_path = Path(f"data/schema/{table_name}.json")

    try:
        with schema_path.open("r") as file:
            schema_data = json.load(file)

        # プロンプトをフォーマット
        formatted_prompt = table_prompt.format(
            table_schema=json.dumps(schema_data, indent=2),
            sample_queries="\n".join(sample_queries),
        )
        logger.debug(f"Formatted table schema prompt for {table_name}: {formatted_prompt}")

        # LLM API呼び出し
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": formatted_prompt}],
        )

        summary = response.choices[0].message.content
        if not summary:
            raise Exception("Failed to generate query summary")

        formatted_summary = summary.replace("\\n", "\n")
        save_summary(SUMMARIZED_SCHEMA_DIR / f"{table_name}.txt", formatted_summary)
        return summary

    except Exception as e:
        logger.error(f"Error summarizing table schema for {table_name}: {e}")
        raise


# クエリ要約の生成
def summarize_query(query: str, file_name: str, related_tables: set[str]) -> str:
    # クエリ要約プロンプトをロード
    query_prompt = load_prompt(SUMMARIZED_QUERY_PROMPT_PATH)
    table_schemas = "\n".join([json.dumps(load_table_schema(table), indent=2) for table in related_tables])

    formatted_prompt = query_prompt.format(
        query=query,
        table_schemas=table_schemas,
    )
    logger.debug(f"Formatted query prompt: {formatted_prompt}")

    # LLM API呼び出し
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": formatted_prompt}],
    )

    summary = response.choices[0].message.content
    if not summary:
        raise Exception("Failed to generate query summary")

    formatted_summary = summary.replace("\\n", "\n")

    save_summary(SUMMARIZED_QUERIES_DIR / f"{file_name}.txt", formatted_summary)
    return summary


# スキーマをロードする補助関数
def load_table_schema(table_name: str) -> dict:
    schema_path = SCHEMA_DIR / f"{table_name}.json"
    with schema_path.open("r") as file:
        return json.load(file)


# 要約結果を保存
def save_summary(file_path: Path, summary: str) -> None:
    with open(file_path, "w") as file:
        json.dump({"summary": summary}, file, ensure_ascii=False, indent=2)
    logger.info(f"Saved summary to {file_path}")


@app.command()
def main():
    # 全テーブル要約生成
    table_names = [f.stem for f in SCHEMA_DIR.glob("*.json")]
    for table in table_names:
        sample_queries = load_related_queries(table)
        summarize_table_schema(table, sample_queries)

    # 全クエリ要約生成
    query_files = SAMPLE_QUERIES_DIR.glob("*.sql")
    for query_file in query_files:
        with query_file.open() as f:
            query = f.read()
        related_tables = extract_related_tables(query)
        summarize_query(query, query_file.stem, related_tables)


if __name__ == "__main__":
    app()
