from pytest_mock import MockerFixture
from typer.testing import CliRunner

from my_text_to_sql_poc.__main__ import app

runner = CliRunner()


def test_cli_e2e() -> None:
    # Act
    result = runner.invoke(
        app,
        [
            "--question",
            "2023年の売上合計は？",
            "--dialect",
            "SQLite",
            "--log-level",
            "INFO",
        ],
    )

    # Assert
    ## コマンドが成功して終了したことを確認
    assert result.exit_code == 0
    ## 標準出力の内容を確認
    assert "Generated SQL Query:" in result.output
    assert "Explanation:" in result.output
