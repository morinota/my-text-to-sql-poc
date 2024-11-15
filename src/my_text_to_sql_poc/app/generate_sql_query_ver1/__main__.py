import json
import os
from pathlib import Path

import typer
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from loguru import logger
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway
from my_text_to_sql_poc.service.sql_formatter import format_sql_query

app = typer.Typer(pretty_exceptions_enable=False)  # Typerアプリケーションのインスタンスを作成


# 出力データのフォーマットを設定
class OutputFormat(BaseModel):
    query: str = Field(description="生成されたSQLクエリ")
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


# プロンプトをファイルから読み込む関数
def load_prompt(file_path: str) -> str:
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
                formatted_schemas += ", ".join([str(col) for col in table_data["columns"]]) + "\n\n"
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
    output_parser = JsonOutputParser(pydantic_object=OutputFormat)

    prompt_template_str = load_prompt("prompts/generate_sql_prompt_ver1_jp.txt")
    prompt_template = PromptTemplate(
        template=prompt_template_str + "\n\n{format_instructions}\n",
        input_variables=["dialect", "table_schemas", "question"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    prompt = prompt_template.format(
        dialect=dialect,
        table_schemas=table_schemas,
        original_query=question,
        question=question,
    )
    logger.debug(f"Generated prompt: {prompt}")

    # OpenAI APIの呼び出し
    model_gateway = ModelGateway()
    response_text = model_gateway.generate_response(prompt)

    # レスポンスの本文からqueryフィールドとexplanationフィールドを取得
    response_data = json.loads(response_text)
    sql_query = response_data["query"]
    explanation = response_data.get("explanation", "")

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

    logger.info(f"\nGenerated SQL Query:\n {formatted_sql}")
    if explanation:
        logger.info(f"\nExplanation:\n {explanation}")

    logger.info("SQL query generation process completed")


if __name__ == "__main__":
    app()
