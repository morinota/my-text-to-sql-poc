from my_text_to_sql_poc.service.related_table_extractor import extract_related_tables


def test_extract_related_tables_with_1_cte():
    """CTEが1つ含まれるSQLクエリからテーブル名を抽出するテスト"""

    # Arrange
    sql_query = """
    with
    cte_table as (
        select * from table1
    )
    
    select 
        *
    from 
        table2
    join cte_table using (id)
    """

    # Act
    related_tables = extract_related_tables(sql_query)

    # Assert
    assert related_tables == {"table1", "table2"}, "CTEテーブルが除外され、table1とtable2のみが抽出されること"


def test_extract_related_tables_with_more_2_cte():
    """CTEが2つ以上含まれるSQLクエリから、テーブル名を抽出するテスト"""
    # Arrange
    sql_query = """
    with
    cte_1 as (
        select * from table1
    )
    , cte_2 as (
        select * from table2
    )
    select 
        *
    from 
        table3
    join cte_1 using (id)
    join cte_2 using (id)
    """

    # Act
    related_tables = extract_related_tables(sql_query)

    # Assert
    assert related_tables == {
        "table1",
        "table2",
        "table3",
    }, "CTEテーブルが除外され、table1, table2, table3のみが抽出されること"
