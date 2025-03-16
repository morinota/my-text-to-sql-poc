from typer.testing import CliRunner

from my_text_to_sql_poc.app.text2sql.text2sql_facade import app

runner = CliRunner()


def test_generate_sql_query_with_context_construction() -> None:
    # Act
    result = runner.invoke(
        app,
        [
            "--question",
            "2023年の売上合計は？",
            "--dialect",
            "SQLite",
        ],
    )

    # Assert
    ## コマンドが成功して終了したことを確認
    assert result.exit_code == 0
    ## 標準出力の内容を確認
    assert "Generated SQL Query:" in result.output
    assert "Explanation:" in result.output
