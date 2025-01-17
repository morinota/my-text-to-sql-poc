from my_text_to_sql_poc.app.text2sql_langgraph.tools import retrieve_related_tables


def test_hoge() -> None:
    # Arrange
    user_question = "記事のCTRを知りたい"
    k = 20

    # Act
    actual = retrieve_related_tables.invoke({"question": user_question, "k": k})

    # Assert
    expected = {"albums": "アルバム情報", "artists": "アーティスト情報"}
