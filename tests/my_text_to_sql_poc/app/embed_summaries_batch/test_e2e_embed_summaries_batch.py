from pathlib import Path

import duckdb
from typer.testing import CliRunner

from my_text_to_sql_poc.app.embed_summaries_batch.__main__ import app

runner = CliRunner()


def test_e2e_embed_summaries_batch() -> None:
    with runner.isolated_filesystem():
        # Arrange
        ## テスト用のdocumentsディレクトリとサンプル要約ファイルを用意する
        table_summary_dir = Path("documents/table_summaries")
        query_summary_dir = Path("documents/query_summaries")
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
                "documents/table_summaries",
                "--query-summary-dir",
                "documents/query_summaries",
                "--vectorstore-file",
                "vectorstore.duckdb",
            ],
        )

        # Assert
        assert result.exit_code == 0, "CLIアプリケーションが正常終了すること"

        assert Path("vectorstore.duckdb").exists(), "DuckDBファイルが生成されていること"

        # DuckDBに想定通りに埋め込みが永続化されていることを確認
        conn = duckdb.connect("vectorstore.duckdb")
        result = conn.execute("SELECT * from embeddings").fetchall()
        assert len(result) == 4, "埋め込みが4つ永続化されていること"
