from pathlib import Path

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from my_text_to_sql_poc.app.embed_summaries_batch.__main__ import app

runner = CliRunner()


def test_e2e_embed_summaries_batch(mocker: MockerFixture):
    with runner.isolated_filesystem():
        # Arrange
        ## テスト用ディレクトリとサンプル要約ファイルを作成
        table_summary_dir = Path("table_summaries")
        query_summary_dir = Path("query_summaries")
        table_summary_dir.mkdir(parents=True, exist_ok=True)
        query_summary_dir.mkdir(parents=True, exist_ok=True)

        with open(table_summary_dir / "table1.txt", "w") as f:
            f.write("これはtable1の要約です。")
        with open(table_summary_dir / "table2.txt", "w") as f:
            f.write("これはtable2の要約です。")
        with open(query_summary_dir / "query1.txt", "w") as f:
            f.write("これはquery1の要約です。")
        with open(query_summary_dir / "query2.txt", "w") as f:
            f.write("これはquery2の要約です。")

        # Act
        result = runner.invoke(
            app,
            [
                "--table-summary-dir",
                str(table_summary_dir),
                "--query-summary-dir",
                str(query_summary_dir),
                "--index-file",
                "vector_index.faiss",
                "--id-file",
                "vector_id_map.txt",
            ],
        )

        # Assert
        assert result.exit_code == 0, "CLIアプリケーションが正常終了すること"

        assert Path("vector_index.faiss").exists(), "FAISSインデックスファイルが生成されていること"

        # IDリストファイルの中身を確認
        assert Path("vector_id_map.txt").exists(), "IDリストファイルが生成されていること"
        with open("vector_id_map.txt", "r") as f:
            ids = f.readlines()
            print(ids)
            assert len(ids) == 4, "IDリストファイルに4つの要約ファイルの名前が記載されていること"
