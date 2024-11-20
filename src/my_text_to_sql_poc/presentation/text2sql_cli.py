import os

import typer
from loguru import logger

from my_text_to_sql_poc.app.generate_sql_query.text2sql_facade import Text2SQLFacade

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def main(
    question: str = typer.Option(..., help="The user's question (natural language)"),
    dialect: str = typer.Option("SQLite", help="The SQL dialect to use (default is SQLite)"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
) -> None:
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    facade = Text2SQLFacade()
    sql_query, explanation = facade.process_query(question, dialect)

    logger.info(f"\nGenerated SQL Query:\n {sql_query}")
    if explanation:
        logger.info(f"\nExplanation:\n {explanation}")
    logger.info("SQL query generation process completed")


if __name__ == "__main__":
    app()
