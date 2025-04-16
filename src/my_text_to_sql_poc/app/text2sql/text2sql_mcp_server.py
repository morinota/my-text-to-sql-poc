from mcp.server.fastmcp import FastMCP

from my_text_to_sql_poc.app.text2sql.text2sql_facade import Text2SQLFacade

# FastMCPサーバーを初期化
mcp = FastMCP("My Text2SQL Server")
text2sql_facade = Text2SQLFacade()


@mcp.tool("retrieve_related_tables_and_queries_for_text2sql")
async def retrieve_related_tables_and_queries(
    user_query: str,
    related_table_cnt: int,
    related_query_cnt: int,
) -> dict[str, dict[str, str]]:
    """
    ユーザ質問に関連しそうなコンテキスト(テーブルメタデータとサンプルクエリ)をretrieveして返す
    Args:
        user_query (str): ユーザの質問
        related_table_cnt (int): 関連テーブルの数
        related_query_cnt (int): 関連サンプルクエリの数
    Returns:
        dict[str, dict[str, str]]: テーブルメタデータとサンプルクエリの辞書。
        {
            "related_metadata_by_table": {テーブル名: スキーマ},
            "related_sql_by_query_name": {サンプルクエリ名: サンプルクエリ}
        }
    """
    related_metadata_by_table = text2sql_facade.retrieve_related_tables(user_query, related_table_cnt)
    related_sql_by_query_name = text2sql_facade.retrieve_related_sample_queries(user_query, related_query_cnt)
    return {
        "related_metadata_by_table": related_metadata_by_table,
        "related_sql_by_query_name": related_sql_by_query_name,
    }


@mcp.prompt()
async def text2sql_prompt(
    user_query: str,
    dialect: str,
    tables_metadata: str,
    related_sample_queries: str,
) -> str:
    """
    SQLクエリを生成するためのプロンプト
    """
    # ダミーのSQLクエリと説明文を返す
    dummy_prompt = f"""
    ユーザ質問: {user_query}
    関連テーブルメタデータ: {tables_metadata}
    関連サンプルクエリ: {related_sample_queries}
    その他注意事項: hogehoge
    """
    return dummy_prompt


if __name__ == "__main__":
    # サーバーを初期化して実行
    mcp.run(transport="stdio")
