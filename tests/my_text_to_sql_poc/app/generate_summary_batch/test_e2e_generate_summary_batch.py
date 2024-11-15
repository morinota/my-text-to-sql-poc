import json
from pathlib import Path

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from my_text_to_sql_poc.app.generate_summary_batch.__main__ import app

runner = CliRunner()


def test_summarize_app_with_full_refresh(mocker: MockerFixture):
    """すべてのサマリを洗い替えするモードの実行"""
    with runner.isolated_filesystem():
        # Arrange

        # TODO: E2Eテストなのに、テストダブルで置き換えるべきかは要検討
        ## Model Gatewayのgenerate_responseメソッドをテストダブルに置き換える
        test_double_response = """
        This is sample summary!!!
        """
        mocker.patch(
            "my_text_to_sql_poc.service.model_gateway.ModelGateway.generate_response",
            return_value=test_double_response,
        )

        ## 入力データの用意
        ### ディレクトリの作成
        schema_dir = Path("schema")
        sample_queries_dir = Path("sample_queries")
        summarized_schema_dir = Path("summarized_schema")
        summarized_sample_queries_dir = Path("summarized_sample_queries")
        schema_dir.mkdir(parents=True, exist_ok=True)
        sample_queries_dir.mkdir(parents=True, exist_ok=True)
        summarized_schema_dir.mkdir(parents=True, exist_ok=True)
        summarized_sample_queries_dir.mkdir(parents=True, exist_ok=True)

        ### テーブルスキーマの用意
        hoge_table_schema = "create table hoge (id int, name text);"
        with open(schema_dir / "hoge_table.txt", "w") as f:
            f.write(hoge_table_schema)

        ### サンプルクエリの用意
        sample_query = """
        SELECT id, name FROM hoge_table WHERE id = 1;
        """
        with open(sample_queries_dir / "sample_query.sql", "w") as f:
            f.write(sample_query)

        ### プロンプトファイルの用意
        table_prompt = "Summarize the table schema: {table_schema}\nSample Queries:\n{sample_queries}"
        query_prompt = "Summarize the SQL query: {query}\nTable Schemas:\n{table_schemas}"
        with open("summarize_table_prompt.txt", "w") as f:
            f.write(table_prompt)
        with open("summarize_query_prompt.txt", "w") as f:
            f.write(query_prompt)

        # Act
        result = runner.invoke(
            app,
            [
                "--schema-dir",
                "schema",
                "--sample-queries-dir",
                "sample_queries",
                "--output-schema-dir",
                "summarized_schema",
                "--output-queries-dir",
                "summarized_sample_queries",
                "--schema-prompt-path",
                "summarize_table_prompt.txt",
                "--query-prompt-path",
                "summarize_query_prompt.txt",
            ],
        )

        # Assert
        assert result.exit_code == 0, "CLIアプリケーションが正常終了すること"

        ## 出力ファイルの内容を確認
        with open(summarized_schema_dir / "hoge_table.txt", "r") as f:
            assert (
                f.read() == test_double_response
            ), "テーブルスキーマのサマリがmodel gatewayのレスポンスに基づいて正しく出力されていること"
        with open(summarized_sample_queries_dir / "sample_query.txt", "r") as f:
            assert (
                f.read() == test_double_response
            ), "サンプルクエリのサマリがmodel gatewayのレスポンスに基づいて正しく出力されていること"
