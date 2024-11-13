from pathlib import Path

import duckdb
import typer
from langchain_community.docstore.document import Document
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import DuckDB
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from loguru import logger
from tiktoken import encoding_for_model

app = typer.Typer()

# 定数設定
EMBEDDING_MODEL_NAME = "text-embedding-3-small"
PRICE_DOLLAR_PER_1K_TOKENS = 0.00002

# OpenAIの埋め込みモデルを設定
embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)


def _calculate_cost(documents: list[Document]) -> float:
    """トークン数と予想料金を計算"""
    encoding = encoding_for_model(EMBEDDING_MODEL_NAME)
    total_tokens = sum(len(encoding.encode(doc.page_content)) for doc in documents)
    cost_dollar = (total_tokens / 1000) * PRICE_DOLLAR_PER_1K_TOKENS
    logger.info(f"Total tokens: {total_tokens}")
    logger.info(f"Estimated cost: ${cost_dollar:.4f}")
    return cost_dollar


def _load_and_split_documents(directory_path: Path) -> list[Document]:
    documents = []
    for file_path in directory_path.glob("*.txt"):
        documents.extend(TextLoader(file_path).load())

    return CharacterTextSplitter().split_documents(documents)


def _process_and_store_embeddings(
    documents: list[Document],
    connection: duckdb.DuckDBPyConnection,
) -> DuckDB:
    """テキストを読み込み、埋め込みを生成し、DuckDBに保存"""
    docsearch = DuckDB.from_documents(documents, embeddings_model, connection=connection)
    return docsearch


@app.command()
def main(
    table_summary_dir: Path = typer.Option("data/summarized_schema/", help="テーブル要約ディレクトリ"),
    query_summary_dir: Path = typer.Option("data/summarized_queries/", help="クエリ要約ディレクトリ"),
    vectorstore_file: Path = typer.Option("sample_vectorstore.duckdb", help="ベクトルストアファイル"),
):
    if vectorstore_file.exists():
        vectorstore_file.unlink()  # すでに存在していたら一旦削除

    # データベース接続の設定
    conn = duckdb.connect(database=str(vectorstore_file))

    # documentsをロード
    documents = _load_and_split_documents(table_summary_dir)
    # コスト計算
    _calculate_cost(documents)

    # テーブルとクエリの埋め込み生成と保存
    _process_and_store_embeddings(documents, conn)

    # ベクトルデータベースの中身を確認
    logger.debug(conn.execute("SELECT count(*) FROM embeddings").df())
    logger.debug(conn.execute("SELECT * FROM embeddings LIMIT 5").df())


if __name__ == "__main__":
    app()
