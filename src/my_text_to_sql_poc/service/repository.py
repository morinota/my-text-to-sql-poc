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
    def put(self, query_name: str, query: str) -> None:
        """サンプルクエリを保存する"""
        pass


class FileSystemTableMetadataRepository(TableMetadataRepositoryInterface):
    def __init__(self, metadata_dir: Path = Path("data/table_metadata/")) -> None:
        self.metadata_dir = metadata_dir

    def get(self, table_names: list[str]) -> dict[str, str]:
        metadata_by_table = {}
        available_tables = [file.stem for file in self.metadata_dir.glob("*.txt")]

        for table_name in table_names:
            file_path = self.metadata_dir / f"{table_name}.txt"
            if table_name not in available_tables or not file_path.exists():
                logger.warning(f"Schema file not found for table: {table_name}\n Available tables: {available_tables}")
                continue
            with file_path.open("r") as file:
                table_data = file.read()
                metadata_by_table[table_name] = table_data
        return metadata_by_table

    def put(self, table_name: str, metadata: str) -> None:
        file_path = self.metadata_dir / f"{table_name}.txt"
        with file_path.open("w") as file:
            file.write(metadata)


class FileSystemSampleQueryRepository(SampleQueryRepositoryInterface):
    def __init__(self, query_dir: Path = Path("data/sample_queries/")) -> None:
        self.query_dir = query_dir

    def get(self, query_names: list[str]) -> dict[str, str]:
        sql_by_query_name = {}
        available_queries = [file.stem for file in self.query_dir.glob("*.sql")]

        for query_name in query_names:
            file_path = self.query_dir / f"{query_name}.sql"
            if query_name not in available_queries or not file_path.exists():
                raise FileNotFoundError(
                    f"Sample query file not found for query: {query_name}\n Available queries: {available_queries}"
                )
            with file_path.open("r") as file:
                query_data = file.read()
                sql_by_query_name[query_name] = query_data
        return sql_by_query_name

    def put(self, query_name: str, query: str) -> None:
        file_path = self.query_dir / f"{query_name}.sql"
        with file_path.open("w") as file:
            file.write(query)


class DuckDBTableMetadataRepository(TableMetadataRepositoryInterface):
    def __init__(
        self,
        # db_path: str = "table_metadata_store.duckdb",
        db_path: str = "s3://staging-newspicks-datalake-mart/tmp/text2sql_poc/table_metadata_store.duckdb",
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
        import duckdb

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
        import duckdb

        conn = duckdb.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS table_metadata (table_name TEXT, metadata TEXT)")
        conn.execute("INSERT INTO table_metadata (table_name, metadata) VALUES (?, ?)", (table_name, metadata))
        conn.close()


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
        import duckdb

        conn = duckdb.connect(self.db_path)
        sql_by_query_name = {}
        for query_name in query_names:
            query = f"SELECT query FROM sample_queries WHERE query_name = '{query_name}'"
            result = conn.execute(query).fetchone()
            if result:
                sql_by_query_name[query_name] = result[0]
        conn.close()
        return sql_by_query_name

    def put(self, query_name: str, query: str) -> None:
        import duckdb

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


class VectorStoreRepositoryInterface(ABC):
    @abstractmethod
    def retrieve_relevant_docs(self, question: str, table_name: str, k: int = 5) -> list:
        pass


class DuckDBVectorStoreRepository(VectorStoreRepositoryInterface):
    def __init__(
        self,
        # vector_db_path: str = "sample_vectorstore.duckdb",
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
