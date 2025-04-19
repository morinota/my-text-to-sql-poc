from abc import ABC, abstractmethod
from pathlib import Path

from loguru import logger


class TableMetadataRepositoryInterface(ABC):
    @abstractmethod
    def get(self, table_names: list[str]) -> dict[str, str]:
        pass

    @abstractmethod
    def put(self, table_name: str, metadata: str) -> None:
        pass


class SampleQueryRepositoryInterface(ABC):
    @abstractmethod
    def get(self, query_names: list[str]) -> dict[str, str]:
        pass

    @abstractmethod
    def put(self, query_name: str, query: str) -> None:
        pass


class TableMetadataRepository(TableMetadataRepositoryInterface):
    def __init__(self, metadata_dir: Path):
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


class SampleQueryRepository(SampleQueryRepositoryInterface):
    def __init__(self, query_dir: Path):
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
