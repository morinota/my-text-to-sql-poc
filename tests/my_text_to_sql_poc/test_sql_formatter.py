from my_text_to_sql_poc.sql_formatter import format_sql_query


def test_format_sql_query():
    # ダミーSQLクエリ
    unformatted_sql = "SELECT\nSUM(amount)\nAS total_sales\nFROM sales\nWHERE strftime('%Y', sale_date) = '2023';"

    # フォーマットを実行
    formatted_sql = format_sql_query(unformatted_sql, dialect="sqlite")

    # 出力が期待通りか確認
    expected_sql = """
    select
        sum(amount) as total_sales 
    from 
        sales 
    where 
        strftime('%Y', sale_date) = '2023'
    ;
    """
    assert formatted_sql == expected_sql, f"Expected:\n{expected_sql}\nBut got:\n{formatted_sql}"
