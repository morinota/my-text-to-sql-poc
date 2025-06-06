import os
from abc import ABC, abstractmethod
from pathlib import Path

import boto3
import duckdb
from langchain_community.vectorstores import DuckDB
from langchain_openai import OpenAIEmbeddings
from loguru import logger


class TableMetadataRepositoryInterface(ABC):
    @abstractmethod
    def get(self, table_names: list[str]) -> dict[str, str]:
        """
        Args:
            table_names (list[str]): テーブル名のリスト
        Returns:
            dict[str, str]: テーブル名をキー、テーブルメタデータを値とする辞書
        """
        pass

    @abstractmethod
    def put(self, table_name: str, metadata: str) -> None:
        """テーブルメタデータを保存する"""
        pass

    @abstractmethod
    def get_all(self) -> dict[str, str]:
        """
        すべてのテーブルメタデータを取得する
        Returns:
            dict[str, str]: テーブル名をキー、テーブルメタデータを値とする辞書
        """
        pass

    @abstractmethod
    def put_bulk(self, items: list[tuple[str, str]]) -> None:
        """
        テーブルメタデータを一括保存する
        Args:
            items (list of (table_name, metadata)): 保存対象
        """
        pass


class SampleQueryRepositoryInterface(ABC):
    @abstractmethod
    def get(self, query_names: list[str]) -> dict[str, str]:
        """サンプルクエリを取得する
        Args:
            query_names (list[str]): サンプルクエリ名のリスト
        Returns:
            dict[str, str]: サンプルクエリ名をキー、サンプルクエリ文字列を値とする辞書
        """
        pass

    @abstractmethod
    def put(self, query_name: str, query: str, query_url: str) -> None:
        """サンプルクエリを保存する"""
        pass

    @abstractmethod
    def retrieve_by_table_name(self, table_name: str) -> dict[str, str]:
        """特定のテーブルが参照されているサンプルクエリ一覧を取得する
        Args:
            table_name (str): テーブル名
        Returns:
            dict[str, str]: サンプルクエリ名をキー、サンプルクエリ文字列を値とする辞書
        """
        pass

    @abstractmethod
    def get_all(self) -> dict[str, str]:
        """
        すべてのサンプルクエリを取得する
        Returns:
            dict[str, str]: サンプルクエリ名をキー、サンプルクエリ文字列を値とする辞書
        """
        pass

    @abstractmethod
    def put_bulk(self, items: list[tuple[str, str, str]]) -> None:
        """
        サンプルクエリを一括保存する
        Args:
            items (list of (query_name, query, query_url)): 保存対象
        """
        pass


class DuckDBTableMetadataRepository(TableMetadataRepositoryInterface):
    """一旦table_metadataテーブルを以下のようなスキーマで用意してみました。
    ```sql
    CREATE TABLE table_metadata (
        table_name TEXT PRIMARY KEY,
        metadata TEXT
    );
    ```
    """

    def __init__(
        self,
        # db_path: str = "table_metadata_store.duckdb",
        db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/table_metadata_store.duckdb",
    ) -> None:
        self._original_db_path = db_path
        if db_path.startswith("s3://"):
            self.db_path = download_duckdb_from_s3(db_path)
        else:
            self.db_path = Path(db_path)

    def get(self, table_names: list[str]) -> dict[str, str]:
        conn = duckdb.connect(self.db_path)
        metadata_by_table = {}
        for table_name in table_names:
            query = f"SELECT metadata FROM table_metadata WHERE table_name = '{table_name}'"
            result = conn.execute(query).fetchone()
            if result:
                metadata_by_table[table_name] = result[0]
        conn.close()
        return metadata_by_table

    def put(self, table_name: str, metadata: str) -> None:
        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS table_metadata (table_name TEXT, metadata TEXT)")
        conn.execute("INSERT INTO table_metadata (table_name, metadata) VALUES (?, ?)", (table_name, metadata))
        conn.close()

    def get_all(self) -> dict[str, str]:
        conn = duckdb.connect(self.db_path)
        query = "SELECT table_name, metadata FROM table_metadata"
        results = conn.execute(query).fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}

    def put_bulk(self, items: list[tuple[str, str]]) -> None:
        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS table_metadata (table_name TEXT, metadata TEXT)")
        conn.executemany("INSERT INTO table_metadata (table_name, metadata) VALUES (?, ?)", items)
        conn.close()

        if self._original_db_path.startswith("s3://"):
            upload_duckdb_to_s3(self.db_path, self._original_db_path)
            logger.info(f"Uploaded table metadata to S3: {self._original_db_path}")


class DuckDBSampleQueryRepository(SampleQueryRepositoryInterface):
    """一旦sample_queriesテーブルを以下のようなスキーマで用意してみました。
    ```sql
    CREATE TABLE sample_queries (
        query_name TEXT PRIMARY KEY,
        query TEXT,
        query_url TEXT,
    );
    ```
    """

    def __init__(
        self,
        # db_path: str = "sample_query_store.duckdb",
        db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/sample_query_store.duckdb",
    ) -> None:
        self._original_db_path = db_path
        if db_path.startswith("s3://"):
            self.db_path = download_duckdb_from_s3(db_path)
        else:
            self.db_path = db_path

    def get(self, query_names: list[str]) -> dict[str, str]:
        conn = duckdb.connect(self.db_path)
        sql_by_query_name = {}
        for query_name in query_names:
            query = f"SELECT query FROM sample_queries WHERE query_name = '{query_name}'"
            result = conn.execute(query).fetchone()
            if result:
                sql_by_query_name[query_name] = result[0]
        conn.close()
        return sql_by_query_name

    def put(self, query_name: str, query: str, query_url: str) -> None:
        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS sample_queries (query_name TEXT, query TEXT, query_url TEXT)")
        conn.execute(
            """
            INSERT INTO sample_queries (query_name, query, query_url)
            VALUES (?, ?, ?)
            ON CONFLICT (query_name) DO UPDATE SET
                query = excluded.query,
                query_url = excluded.query_url
            """,
            (query_name, query, query_url),
        )
        conn.close()

    def retrieve_by_table_name(self, table_name: str) -> dict[str, str]:
        conn = duckdb.connect(self.db_path)
        query = """
            SELECT query_name, query
            FROM sample_queries
            WHERE lower(query) LIKE '%' || lower(?) || '%'
        """
        results = conn.execute(query, (table_name,)).fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}

    def get_all(self) -> dict[str, str]:
        conn = duckdb.connect(self.db_path)
        query = "SELECT query_name, query FROM sample_queries"
        results = conn.execute(query).fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}

    def put_bulk(self, items: list[tuple[str, str, str]]) -> None:
        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS sample_queries (query_name TEXT, query TEXT, query_url TEXT)")
        conn.executemany(
            """
            INSERT INTO sample_queries (query_name, query, query_url)
            VALUES (?, ?, ?)
            ON CONFLICT (query_name) DO UPDATE SET
                query = excluded.query,
                query_url = excluded.query_url
            """,
            items,
        )
        conn.close()

        if self._original_db_path.startswith("s3://"):
            upload_duckdb_to_s3(self.db_path, self._original_db_path)
            logger.info(f"Uploaded sample queries to S3: {self._original_db_path}")


class VectorStoreRepositoryInterface(ABC):
    @abstractmethod
    def retrieve_relevant_docs(self, question: str, table_name: str, k: int = 5) -> list:
        pass

    @abstractmethod
    def put(self, doc_id: str, document: str, table_name: str) -> None:
        """
        Args:
            doc_id (str): ドキュメントの一意の識別子
            document (str): 保存するドキュメントの内容
            table_name (str): ドキュメントを保存するベクトルDBのテーブル名
        """
        pass

    @abstractmethod
    def put_bulk(self, docs: list[tuple[str, str]], table_name: str) -> None:
        """
        ベクトルストアにドキュメントを一括保存する
        Args:
            docs: list of (doc_id, document)
            table_name: str: ドキュメントを保存するベクトルDBのテーブル名
        """
        pass


class DuckDBVectorStoreRepository(VectorStoreRepositoryInterface):
    def __init__(
        self,
        vector_db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/sample_vectorstore.duckdb",
        model_name: str = "text-embedding-3-small",
    ) -> None:
        self._original_vector_db_path = vector_db_path
        if vector_db_path.startswith("s3://"):
            self.vector_db_path = download_duckdb_from_s3(vector_db_path)
        else:
            self.vector_db_path = Path(vector_db_path)
        self.model_name = model_name

    def retrieve_relevant_docs(self, question: str, table_name: str, k: int = 5) -> list:
        embeddings = OpenAIEmbeddings(model=self.model_name)
        conn = duckdb.connect(database=self.vector_db_path)
        vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
        return vectorstore.similarity_search(question, k=k)

    def put(self, doc_id: str, document: str, table_name: str) -> None:
        embeddings = OpenAIEmbeddings(model=self.model_name)
        conn = duckdb.connect(database=self.vector_db_path)
        vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
        vectorstore.add_texts([document], metadatas=[{"doc_id": doc_id}])
        conn.close()

    def put_bulk(self, docs: list[tuple[str, str]], table_name: str) -> None:
        embeddings = OpenAIEmbeddings(model=self.model_name)
        conn = duckdb.connect(database=self.vector_db_path)
        vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
        vectorstore.add_texts(
            texts=[text for _, text in docs],
            metadatas=[{"doc_id": doc_id} for doc_id, _ in docs],
        )
        conn.close()

        if self._original_vector_db_path.startswith("s3://"):
            upload_duckdb_to_s3(self.vector_db_path, self._original_vector_db_path)
            logger.info(f"Uploaded vector store to S3: {self._original_vector_db_path}")


# 以下はS3上のduckdbファイルとやりとりするための共通処理
def download_duckdb_from_s3(s3_path: str, local_dir: Path = Path("/tmp")) -> Path:
    s3 = boto3.client("s3")
    bucket, key = s3_path[5:].split("/", 1)
    local_path = local_dir / os.path.basename(key)
    logger.info(f"Downloading {s3_path} to {local_path}...")
    s3.download_file(bucket, key, local_path)
    logger.info("Download complete.")
    return local_path


def upload_duckdb_to_s3(local_path: Path, s3_uri: str) -> None:
    s3 = boto3.client("s3")
    bucket, key = s3_uri[5:].split("/", 1)
    logger.info(f"Uploading {local_path} to {s3_uri}...")
    s3.upload_file(str(local_path), bucket, key)
    logger.info("Upload complete.")
