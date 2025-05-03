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
        db_path: str = "table_metadata_store.duckdb",
        # db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/table_metadata_store.duckdb",
    ) -> None:
        if db_path.startswith("s3://"):
            s3 = boto3.client("s3")
            bucket_name, key = db_path[5:].split("/", 1)
            local_path = f"/tmp/{os.path.basename(key)}"
            logger.info(f"Fetching the latest table metadata store from {db_path} to {local_path}...")
            s3.download_file(bucket_name, key, local_path)
            logger.info(f"Successfully fetched the latest table metadata store: {local_path}")
            self.db_path = local_path
        else:
            self.db_path = db_path

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
        db_path: str = "sample_query_store.duckdb",
        # db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/sample_query_store.duckdb",
    ) -> None:
        if db_path.startswith("s3://"):
            s3 = boto3.client("s3")
            bucket_name, key = db_path[5:].split("/", 1)
            local_path = f"/tmp/{os.path.basename(key)}"
            logger.info(f"Fetching the latest sample query store from {db_path} to {local_path}...")
            s3.download_file(bucket_name, key, local_path)
            logger.info(f"Successfully fetched the latest sample query store: {local_path}")
            self.db_path = local_path
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


class DuckDBVectorStoreRepository(VectorStoreRepositoryInterface):
    def __init__(
        self,
        # vector_db_path: str = "/tmp/sample_vectorstore.duckdb",
        vector_db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/sample_vectorstore.duckdb",
        model_name: str = "text-embedding-3-small",
    ) -> None:
        if vector_db_path.startswith("s3://"):
            s3 = boto3.client("s3")
            bucket_name, key = vector_db_path[5:].split("/", 1)
            local_path = f"/tmp/{os.path.basename(key)}"
            logger.info(f"Fetching the latest vector store from {vector_db_path} to {local_path}...")
            s3.download_file(bucket_name, key, local_path)
            logger.info(f"Successfully fetched the latest vector store: {local_path}")
            self.vector_db_path = local_path
        else:
            self.vector_db_path = vector_db_path
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
