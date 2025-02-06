import polars as pl

from my_text_to_sql_poc.app.generate_table_metadata_batch.__main__ import generate_table_metadata
from my_text_to_sql_poc.app.generate_table_metadata_batch.table_metadata_model import TableMetadataSchema


def test_SQLクエリの実行ログに基づいてテーブルメタデータが推定される():
    # Arrange
    table_name = "show_article_events"
    audit_log_df = pl.read_csv("data/redshift_audit_log.csv")
    # audit_logから対象テーブルを使用してるクエリのみを抽出する
    related_queries = list(set([query for query in audit_log_df["querytxt"] if table_name in query]))

    # Act
    table_metadata = generate_table_metadata(
        table_name,
        related_queries[0:100],
    )

    # Assert
    print(table_metadata.sample)
    assert isinstance(table_metadata, TableMetadataSchema)


def test_既存書類に基づいてテーブルメタデータが推定される():
    # Arrange
    table_name = "hogehoge_user_master_data"
    doc = """
    このテーブルはユーザの詳細を表しており、一人一行になっています。
    カラム名, サンプルデータ, 説明
    user_id, 1, ユーザID
    last_access_day, 2021-01-01, 最終アクセス日
    total_access_count_days, 100, 通算アクセス日数
    """

    # Act
    table_metadata = generate_table_metadata(table_name, related_queries=[], reffered_doc=doc)

    # Assert
    print(table_metadata.sample)
    assert isinstance(table_metadata, TableMetadataSchema)


def test_SQLクエリの実行ログと既存書類に基づいてテーブルメタデータが推定される():
    # Arrange
    table_name = "hogehoge_user_master_data"
    related_queries = [
        "SELECT * FROM hogehoge_user_master_data WHERE user_id = 1",
        "SELECT * FROM hogehoge_user_master_data WHERE last_access_day between '2021-01-01' and '2021-01-31'",
    ]
    doc = """
    このテーブルはユーザの詳細を表しており、一人一行になっています。
    カラム名, サンプルデータ, 説明
    user_id, 1, ユーザID
    last_access_day, 2021-01-01, 最終アクセス日
    total_access_count_days, 100, 通算アクセス日数
    """

    # Act
    table_metadata = generate_table_metadata(table_name, related_queries, reffered_doc=doc)

    # Assert
    print(table_metadata.sample)
    assert isinstance(table_metadata, TableMetadataSchema)
