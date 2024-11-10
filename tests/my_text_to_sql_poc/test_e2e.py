from pytest_mock import MockerFixture
from typer.testing import CliRunner

from my_text_to_sql_poc.__main__ import app

runner = CliRunner()


def test_cli_e2e(mocker: MockerFixture) -> None:
    # Arrange
    # TODO: E2Eテストなのに、テストダブルで置き換えるべきかは要検討
    ## Model Gatewayのgenerate_responseメソッドをテストダブルに置き換える
    test_double_response = """
    {
        "query": "The SQL query is: SELECT SUM(sales) FROM sales_table WHERE year = 2023.",
        "explanation": "This query calculates the total sales from the sales_table where the year is 2023."
    }
    """

    mocker.patch(
        "my_text_to_sql_poc.service.model_gateway.ModelGateway.generate_response",
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
    assert result.exit_code == 0
    ## 標準出力の内容を確認
    assert "Generated SQL Query:" in result.output
    assert "Explanation:" in result.output
