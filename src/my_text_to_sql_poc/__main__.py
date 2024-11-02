import os
import json
import typer
from loguru import logger

app = typer.Typer()  # Typerアプリケーションのインスタンスを作成


# プロンプトをファイルから読み込む関数
def load_prompt(file_path="prompts/generate_sql_prompt.txt"):
    try:
        with open(file_path, "r") as file:
            prompt = file.read()
            logger.debug(f"Prompt loaded from {file_path}")
            return prompt
    except Exception as e:
        logger.error(f"Failed to load prompt from {file_path}: {e}")
        raise


# テーブルスキーマをJSONファイルから読み込む関数
def load_table_schemas(file_path="schema/tables_schema.json"):
    try:
        with open(file_path, "r") as file:
            schema_data = json.load(file)
            logger.debug(f"Loaded table schemas from {file_path}")
            return schema_data
    except Exception as e:
        logger.error(f"Failed to load table schemas from {file_path}: {e}")
        raise


# スキーマ情報をフォーマットする関数
def format_table_schemas(schema_data):
    formatted_schemas = ""
    for table in schema_data["tables"]:
        formatted_schemas += f"Table: {table['name']}\nColumns: "
        formatted_schemas += (
            ", ".join([col["name"] for col in table["columns"]]) + "\n\n"
        )
    return formatted_schemas


# ダミーのSQLクエリ生成関数
def generate_sql_query(dialect: str, question: str, table_schemas: str):
    prompt_template = load_prompt("prompts/generate_sql_prompt.txt")
    prompt = prompt_template.format(
        dialect=dialect,
        table_schemas=table_schemas,
        original_query=question,
        question=question,
    )
    logger.debug(f"Generated prompt: {prompt}")
    # ダミーのSQLクエリを返す
    sql_query = f"-- Generated query based on question: {question}\nSELECT * FROM sales WHERE amount > 100;"
    logger.info("SQL query generated successfully")
    return sql_query


@app.command()
def main(
    question: str = typer.Option(..., help="The user's question (natural language)"),
    dialect: str = typer.Option(
        "SQLite", help="The SQL dialect to use (default is SQLite)"
    ),
    log_level: str = typer.Option(
        "INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
):
    """
    自然言語の質問からSQLクエリを生成します。

    Args:
        question (str): ユーザーの質問（自然言語）
        dialect (str): 使用するSQLの方言（デフォルトはSQLite）
    """
    logger.info(
        f"Starting SQL query generation for question: '{question}' with dialect: '{dialect}'"
    )
    # ログレベルの設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # テーブルスキーマをロードしてフォーマット
    schema_data = load_table_schemas()
    table_schemas = format_table_schemas(schema_data)

    sql_query = generate_sql_query(dialect, question, table_schemas)
    typer.echo("\nGenerated SQL Query:\n")
    typer.echo(sql_query)
    logger.info("SQL query generation process completed")


if __name__ == "__main__":
    app()  # Typerアプリケーションを実行
