import json
import os
from pathlib import Path

import openai
import typer
from loguru import logger

from my_text_to_sql_poc.sql_formatter import format_sql_query

app = typer.Typer(pretty_exceptions_enable=False)  # Typerアプリケーションのインスタンスを作成

# 環境変数からOpenAI APIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# プロンプトをファイルから読み込む関数
def load_prompt(file_path: str = "prompts/generate_sql_prompt.txt") -> str:
    try:
        with open(file_path, "r") as file:
            prompt = file.read()
            logger.debug(f"Prompt loaded from {file_path}")
            return prompt
    except Exception as e:
        logger.error(f"Failed to load prompt from {file_path}: {e}")
        raise


def load_selected_table_schemas(table_names: list[str] = []) -> str:
    """テーブルスキーマを読み込んでフォーマット"""
    formatted_schemas = ""
    schema_dir = Path("data/schema/")
    available_tables = [file.stem for file in schema_dir.glob("*.json")]

    # 指定されたテーブルがなければ全てのテーブルスキーマを取得
    if not table_names:
        table_names = available_tables.copy()

    for table_name in table_names:
        file_path = schema_dir / f"{table_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(
                f"Schema file not found for table: {table_name}\n Available tables: {available_tables}"
            )

        try:
            with file_path.open("r") as file:
                table_data = json.load(file)
                formatted_schemas += f"Table: {table_data['table_name']}\nColumns: "
                formatted_schemas += ", ".join([col["name"] for col in table_data["columns"]]) + "\n\n"
                logger.debug(f"Loaded schema for table: {table_name}")
        except Exception as e:
            logger.error(f"Error loading schema for table {table_name}: {e}")
            raise e
    return formatted_schemas


def generate_sql_query(
    dialect: str,
    question: str,
    table_schemas: str,
) -> tuple[str, str]:
    prompt_template = load_prompt("prompts/generate_sql_prompt.txt")
    prompt = prompt_template.format(
        dialect=dialect,
        table_schemas=table_schemas,
        original_query=question,
        question=question,
    )
    logger.debug(f"Generated prompt: {prompt}")

    # OpenAI APIの呼び出し
    model = "gpt-4o-mini"
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    # レスポンスの本文からqueryフィールドとexplanationフィールドを取得
    response_text = response.choices[0].message.content
    response_data = json.loads(response_text)
    sql_query = response_data["query"]
    explanation = response_data.get("explanation", "")

    # 利用tokens数を取得
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    # 料金計算
    input_cost = prompt_tokens * (0.15 / 1_000_000)  # $0.15 / 1M tokens
    output_cost = completion_tokens * (0.60 / 1_000_000)  # $0.60 / 1M tokens
    total_cost = input_cost + output_cost
    # ログに出力
    logger.info(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
    logger.info(f"Cost - Input: ${input_cost:.6f}, Output: ${output_cost:.6f}, Total: ${total_cost:.6f}")

    return sql_query, explanation


@app.command()
def main(
    question: str = typer.Option(..., help="The user's question (natural language)"),
    tables: list[str] = typer.Option([], "-T", "-table", help="List of tables to use", show_default=False),
    dialect: str = typer.Option("SQLite", help="The SQL dialect to use (default is SQLite)"),
    log_level: str = typer.Option("INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR)"),
) -> None:
    """
    自然言語の質問からSQLクエリを生成します。

    Args:
        question (str): ユーザーの質問（自然言語）
        dialect (str): 使用するSQLの方言（デフォルトはSQLite）
    """
    logger.info(f"Starting SQL query generation for question: '{question}' with dialect: '{dialect}'")
    # ログレベルの設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # テーブルスキーマをロードしてフォーマット
    table_schemas = load_selected_table_schemas(tables)

    sql_query, explanation = generate_sql_query(dialect, question, table_schemas)
    # SQLクエリ部分の改行コードを変換

    formatted_sql = format_sql_query(sql_query, dialect)

    typer.echo("\nGenerated SQL Query:\n")
    typer.echo(f"{formatted_sql}\n")
    typer.echo(f"Explanation: {explanation}")

    logger.info("SQL query generation process completed")


if __name__ == "__main__":
    app()
