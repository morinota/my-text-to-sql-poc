import json
from pathlib import Path

import duckdb
import typer
from langchain_community.docstore.document import Document
from langchain_community.vectorstores import DuckDB
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from pydantic import BaseModel, Field

from my_text_to_sql_poc.service.model_gateway import ModelGateway

app = typer.Typer(pretty_exceptions_enable=False)  # Typerアプリケーションのインスタンスを作成

MODEL_NAME = "text-embedding-3-small"
VECTOR_DB_PATH = "sample_vectorstore.duckdb"
TABLE_METADATA_DIR = Path("data/table_metadata/")
SAMPLE_QUERY_DIR = Path("data/sample_queries/")


# 出力データのフォーマットを設定
class OutputFormat(BaseModel):
    query: str = Field(description="生成されたSQLクエリ")
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


def retrieve_relevant_docs(
    question: str,
    vectorstore_path: str,
    table_name: str,
    k: int = 5,
) -> list[Document]:
    """ベクトルストアを読み込み、質問に関連するドキュメントをretrieveする"""
    # OpenAIの埋め込みモデルを設定
    embeddings = OpenAIEmbeddings(model=MODEL_NAME)

    # DuckDBインデックスファイルを読みこむ
    conn = duckdb.connect(database=vectorstore_path)
    vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)

    # 質問に関連するドキュメントを取得
    return vectorstore.similarity_search(question, k=k)


def _extract_document_name(doc: Document) -> str:
    """ドキュメントからテーブル名を取得"""
    doc_source: str = doc.metadata["source"]
    return Path(doc_source).stem


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


def load_selected_table_metadata(table_names: list[str]) -> str:
    """テーブルスメタデータを読み込んで、まとめて返す"""
    table_schemas = []

    available_tables = [file.stem for file in TABLE_METADATA_DIR.glob("*.txt")]
    for table_name in table_names:
        file_path = TABLE_METADATA_DIR / f"{table_name}.txt"
        if table_name not in available_tables or not file_path.exists():
            raise FileNotFoundError(
                f"Schema file not found for table: {table_name}\n Available tables: {available_tables}"
            )

        # CREATE TABLE コマンドがそのままファイルに書かれていると仮定し、ファイル内容をそのまま取得
        with file_path.open("r") as file:
            table_data = file.read()
            table_schemas.append(table_data)
            logger.debug(f"Loaded schema for table: {table_name}")

    # 各テーブルのスキーマを改行で区切って返す
    return "\n\n".join(table_schemas)


def load_selected_sample_queries(querie_names: list[str]) -> str:
    """サンプルクエリを読み込んで、まとめて返す"""
    sample_queries = []

    available_queries = [file.stem for file in SAMPLE_QUERY_DIR.glob("*.sql")]
    for query_name in querie_names:
        file_path = SAMPLE_QUERY_DIR / f"{query_name}.sql"
        if query_name not in available_queries or not file_path.exists():
            raise FileNotFoundError(
                f"Sample query file not found for query: {query_name}\n Available queries: {available_queries}"
            )

        with file_path.open("r") as file:
            query_data = file.read()
            sample_queries.append(query_data)
            logger.debug(f"Loaded sample query: {query_name}")

    # 各サンプルクエリを改行で区切って返す
    return "\n\n".join(sample_queries)


def generate_sql_query(
    dialect: str,
    question: str,
    tables_metadata: str,
    related_sample_queries: str,
) -> tuple[str, str]:
    prompt_template_str = load_prompt("prompts/generate_sql_prompt_ver2_jp.txt")

    output_parser = JsonOutputParser(pydantic_object=OutputFormat)

    prompt_template = PromptTemplate(
        template=prompt_template_str + "\n\n{format_instructions}\n",
        input_variables=["dialect", "table_schemas", "original_query", "question", "related_sample_queries"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )
    prompt = prompt_template.format(
        dialect=dialect,
        table_schemas=tables_metadata,
        original_query=question,
        question=question,
        related_sample_queries=related_sample_queries,
    )
    logger.debug(f"Generated prompt: {prompt}")

    # OpenAI APIの呼び出し
    model_gateway = ModelGateway()
    response_text = model_gateway.generate_response(prompt)

    # レスポンスの本文からqueryフィールドとexplanationフィールドを取得
    ## 不要なバッククォートと「json」記法を削除(レスポンスにmarkdown記法のコードブロックが含まれることがあるため)
    cleaned_response_text = response_text.strip("```json").strip("```").strip()
    response_data = json.loads(cleaned_response_text)
    sql_query = response_data["query"]
    explanation = response_data.get("explanation", "")

    return sql_query, explanation


@app.command()
def main(
    question: str = typer.Option(..., help="The user's question (natural language)"),
    dialect: str = typer.Option("SQLite", help="The SQL dialect to use (default is SQLite)"),
    log_level: str = typer.Option("INFO", help="ログレベルを指定します (DEBUG, INFO, WARNING, ERROR)"),
) -> None:
    """
    自然言語の質問からSQLクエリを生成します。

    Args:
        question (str): ユーザーの質問（自然言語）
        dialect (str): 使用するSQLの方言（デフォルトはSQLite）
    """
    # ログレベルを設定
    logger.remove()  # デフォルトのログ設定を削除
    logger.add(lambda msg: typer.echo(msg, err=True), level=log_level.upper())

    # ユーザクエリに関連するテーブル達をretrieve
    retrieved_tables = [
        _extract_document_name(doc)
        for doc in retrieve_relevant_docs(question, VECTOR_DB_PATH, table_name="table_embeddings", k=20)
    ]
    logger.info(f"Retrieved tables: {retrieved_tables}")
    table_schemas = load_selected_table_metadata(retrieved_tables)

    # ユーザクエリに関連するサンプルクエリをretrieve
    retrieved_sample_queries = [
        _extract_document_name(doc)
        for doc in retrieve_relevant_docs(question, VECTOR_DB_PATH, table_name="query_embeddings", k=5)
    ]
    logger.info(f"Retrieved sample queries: {retrieved_sample_queries}")
    related_sample_queries = load_selected_sample_queries(retrieved_sample_queries)

    sql_query, explanation = generate_sql_query(dialect, question, table_schemas, related_sample_queries)

    logger.info(f"\nGenerated SQL Query:\n {sql_query}")
    if explanation:
        logger.info(f"\nExplanation:\n {explanation}")

    logger.info("SQL query generation process completed")


if __name__ == "__main__":
    app()