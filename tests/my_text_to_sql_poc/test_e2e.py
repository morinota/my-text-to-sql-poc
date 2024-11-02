from typer.testing import CliRunner
from my_text_to_sql_poc.__main__ import app

runner = CliRunner()


def test_cli_e2e():
    # CLIコマンドをシミュレートして実行
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

    # コマンドが成功して終了したことを確認
    assert result.exit_code == 0, f"CLI exited with non-zero status: {result.exit_code}"

    # 標準出力の内容を確認
    assert "Generated SQL Query:" in result.output
    assert "SELECT * FROM sales WHERE amount > 100;" in result.output
