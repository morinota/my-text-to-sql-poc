import json

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from my_text_to_sql_poc.__main__ import app

runner = CliRunner()


def test_cli_e2e(mocker: MockerFixture) -> None:
    # Arrange
    # TODO: E2Eテストなのに、テストダブルで置き換えるべきかは要検討
    ## OpenAI APIとのやりとりのみ、テストダブルに置き換える
    test_double_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "query": "SELECT * FROM sales",
                            "explanation": "Test explanation",
                        }
                    )
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }
    mocker.patch(
        "openai.ChatCompletion.create",
        return_value=test_double_response,
    )

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
    assert result.exit_code == 0, f"CLI exited with non-zero status: {result.exit_code}"
    ## 標準出力の内容を確認
    assert "Generated SQL Query:" in result.output
    assert "Explanation:" in result.output
