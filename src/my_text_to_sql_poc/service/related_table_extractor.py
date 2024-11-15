import re

# FROM、JOINキーワードの後に続くテーブル名を正規表現で取得(スキーマを含む)
TABLE_PATTERN = re.compile(r"(?:FROM|JOIN)\s+(\w+(?:\.\w+)?)", re.IGNORECASE)
# CTE(Common Table Expression, with句で定義される一時テーブル)を除外
CTE_PATTERN = re.compile(r"WITH\s+(\w+)\s+AS", re.IGNORECASE)


def extract_related_tables(query: str) -> set[str]:
    """
    SQLクエリから関連するテーブル名を抽出する関数。
    :param query: SQLクエリ文字列
    :return: 抽出されたテーブル名の集合
    """
    table_names = set()

    matche_tables = set(TABLE_PATTERN.findall(query))
    cte_tables = set(CTE_PATTERN.findall(query))
    print(f"{cte_tables=}")
    for match_table in matche_tables:
        # CTEの場合はスキップ
        if match_table in cte_tables:
            continue
        table_names.add(match_table.lower())  # 重複テーブル名を避けるために小文字化

    return table_names


if __name__ == "__main__":
    query = """
    with
    cte_table
    as
    (
        select * from table1
    )
    select 
        *
    from 
        table2
    join cte_table
    """
    related_tables = extract_related_tables(query)
    print(related_tables)
