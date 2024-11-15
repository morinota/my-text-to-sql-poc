import re
import subprocess

import streamlit as st

# ユーザクエリを入力するテキストボックス
st.title("Text to SQL Generator")
user_query = st.text_area(
    "自然言語で質問を入力してください:",
    value="例: 直近1週間のCTRの推移は??",
)

# SQL方言を選択するドロップダウン
sql_dialect = st.selectbox("SQL方言を選択してください:", ["SQLite", "PostgreSQL", "MySQL", "Redshift", "Snowflake"])

# 生成したSQLクエリを表示するテキストエリア
st.subheader("生成されたSQLクエリ")
generated_sql = st.empty()  # クエリ出力用のプレースホルダ

# 「生成」ボタンを押すとSQLクエリ生成CLIを呼び出し
if st.button("SQLクエリを生成"):
    # subprocessでCLIコマンドを呼び出す
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "my_text_to_sql_poc.app.generate_sql_query_ver2",
                "--question",
                user_query,
                "--dialect",
                sql_dialect,
                "--log-level",
                "DEBUG",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # 標準出力全体を表示
        st.subheader("CLI標準出力")
        st.text_area("標準出力", result.stdout, height=300)
        st.text_area("標準エラー", result.stderr, height=150)

        # 標準出力から生成されたSQLクエリを取得
        sql_query_match = re.search(r"Generated SQL Query:\s+([\s\S]+?)\n\n", result.stdout, re.DOTALL)
        explanation_match = re.search(r"Explanation:\s+([\s\S]+?)\n\n", result.stdout, re.DOTALL)

        # if not sql_query_match:
        #     raise ValueError("Failed to extract generated SQL")
        # generated_sql.text_area("生成されたSQLクエリ:", sql_query_match.group(1).strip())

        # if explanation_match:
        #     st.text_area("説明文:", explanation_match.group(1).strip())

    except subprocess.CalledProcessError as e:
        st.error(f"SQLクエリの生成に失敗しました: {e.stderr}")

# オフラインバッチを実行するためのボタン
st.subheader("オフラインバッチ実行")

# テーブルスキーマとサンプルクエリの要約生成ボタン
if st.button("テーブルスキーマとサンプルクエリの要約を更新"):
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "my_text_to_sql_poc.app.generate_summary_batch",
                "--schema-dir",
                "data/schema",
                "--sample-queries-dir",
                "data/sample_queries",
                "--output-schema-dir",
                "data/summarized_schema",
                "--output-queries-dir",
                "data/summarized_sample_queries",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        st.success("テーブルスキーマとサンプルクエリの要約を更新しました")
    except subprocess.CalledProcessError as e:
        st.error(f"要約生成バッチの実行に失敗しました: {e.stderr}")

# 要約を埋め込み表現に変換するバッチボタン
if st.button("要約を埋め込み表現に変換してベクトルDBを更新"):
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "my_text_to_sql_poc.app.embed_summaries_batch",
                "--table-summary-dir",
                "data/summarized_schema",
                "--query-summary-dir",
                "data/summarized_sample_queries",
                "--vectorstore-file",
                "sample_vectorstore.duckdb",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        st.success("埋め込み生成バッチの実行が完了しました")
    except subprocess.CalledProcessError as e:
        st.error(f"埋め込み生成バッチの実行に失敗しました: {e.stderr}")
