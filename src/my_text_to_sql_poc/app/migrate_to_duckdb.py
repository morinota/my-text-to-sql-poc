from pathlib import Path

import duckdb
from loguru import logger


def migrate_table_metadata_to_duckdb(metadata_dir: Path, db_path: Path):
    """
    Migrate table metadata files to a DuckDB database.
    """
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS table_metadata (table_name TEXT, metadata TEXT)")

    for file in metadata_dir.glob("*.txt"):
        table_name = file.stem
        metadata = file.read_text()
        conn.execute("INSERT INTO table_metadata (table_name, metadata) VALUES (?, ?)", (table_name, metadata))
        logger.info(f"Migrated table metadata: {table_name}")

    conn.close()


def migrate_sample_queries_to_duckdb(query_dir: Path, db_path: Path):
    """
    Migrate sample query files to a DuckDB database.
    """
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS sample_queries (query_name TEXT, query TEXT)")

    for file in query_dir.glob("*.sql"):
        query_name = file.stem
        query = file.read_text()
        conn.execute("INSERT INTO sample_queries (query_name, query) VALUES (?, ?)", (query_name, query))
        logger.info(f"Migrated sample query: {query_name}")

    conn.close()


if __name__ == "__main__":
    table_metadata_dir = Path("data/table_metadata")
    sample_queries_dir = Path("data/sample_queries")
    table_metadata_db = Path("table_metadata_store.duckdb")
    sample_queries_db = Path("sample_query_store.duckdb")

    logger.info("Starting migration of table metadata...")
    migrate_table_metadata_to_duckdb(table_metadata_dir, table_metadata_db)

    logger.info("Starting migration of sample queries...")
    migrate_sample_queries_to_duckdb(sample_queries_dir, sample_queries_db)

    logger.info("Migration completed successfully.")
