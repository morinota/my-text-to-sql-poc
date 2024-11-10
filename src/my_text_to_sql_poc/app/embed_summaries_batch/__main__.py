from pathlib import Path

import faiss
import numpy as np
import typer
from loguru import logger
from sentence_transformers import SentenceTransformer

app = typer.Typer()

# モデルのロード
MODEL_NAME = "intfloat/multilingual-e5-small"
model = SentenceTransformer(MODEL_NAME)


def _encode_texts(texts: list[str]) -> list[list[float]]:
    """複数のテキストを埋め込みベクトルにエンコード"""
    return model.encode(texts).tolist()


def _process_and_store_embeddings(summary_dir: Path, index: faiss.IndexFlatL2, id_file: Path):
    """要約ファイルを読み込み、埋め込みを生成し、FAISSインデックスに保存"""
    summary_files = list(summary_dir.glob("*.txt"))
    texts = []
    file_names = []

    # バッチ対象のテキストを収集
    for summary_file in summary_files:
        with summary_file.open("r") as f:
            texts.append(f.read())
            file_names.append(summary_file.name)

    # バッチエンコード
    embeddings = _encode_texts(texts)
    embeddings_array = np.array(embeddings).astype("float32")

    # ベクトルストアに追加
    index.add(embeddings_array)

    # ファイル名とfaiss indexのIDのmappingを保存しておく(行番号がfaissのIDになる)
    # (faissは基本的にkey-valueストアではなく、単にベクトルの集合体として機能するので)
    with id_file.open("a") as f:
        for file_name in file_names:
            f.write(f"{file_name}\n")


@app.command()
def main(
    table_summary_dir: Path = typer.Option(..., help="テーブル要約ディレクトリ"),
    query_summary_dir: Path = typer.Option(..., help="クエリ要約ディレクトリ"),
    index_file: Path = typer.Option("vector_index.faiss", help="FAISSベクトルインデックスの保存先"),
    id_file: Path = typer.Option("vector_ids.txt", help="各埋め込みのIDリスト"),
):
    # FAISSのインデックス作成 (ベクトルの次元数はモデル出力に合わせる)
    embedding_dim = model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatL2(embedding_dim)
    logger.debug(f"Created FAISS index with dimension: {embedding_dim}")

    # テーブルとクエリの埋め込み生成と保存
    _process_and_store_embeddings(table_summary_dir, index, id_file)
    logger.debug("Processed and stored table embeddings to faiss index")
    _process_and_store_embeddings(query_summary_dir, index, id_file)
    logger.debug("Processed and stored query embeddings to faiss index")

    # ベクトルストアを保存
    faiss.write_index(index, str(index_file))
    logger.debug(f"persisted faiss index to {index_file}")


if __name__ == "__main__":
    app()
