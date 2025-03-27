import streamlit as st

from my_text_to_sql_poc.app.text2sql.text2sql_facade import Text2SQLFacade

st.title("Text-to-SQL Generator")

sql_dialect = st.selectbox("SQL方言を選択してください:", ["Redshift", "Snowflake", "PostgreSQL", "MySQL", "SQLite"])

# streamlitのsession_stateにチャット履歴を保存する
# もしチャット履歴がなければ、空のリストを初期化
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


text2sql_facade = Text2SQLFacade()

# 💬 過去のチャット履歴を表示（新しい方は下に）
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_msg = st.chat_input("自然言語の質問や修正指示を入力してください(例: 顧客ごとの売上を取得したい)")


if user_msg:
    # ユーザの入力を会話履歴に追加
    st.session_state["chat_history"].append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.write(user_msg)

    # 関連するテーブルをretrieve
    related_metadata_by_table = text2sql_facade.retrieve_related_tables(user_msg, k=20)
    with st.chat_message("assistant"):
        st.markdown(f"関連するテーブルを取得しました! {', '.join(list(related_metadata_by_table.keys())[0:3])}, ...")
        with st.expander("取得されたテーブルの詳細を見る"):
            for table_name, metadata in related_metadata_by_table.items():
                st.write(f"テーブル名: {table_name}")
                st.text_area("テーブルメタデータ", metadata, height=200)
    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": f"関連するテーブルを取得しました: {', '.join(list(related_metadata_by_table.keys())[0:3])}, ...",
        }
    )

    # 関連するサンプルクエリをretrieve
    related_sql_by_query_name = text2sql_facade.retrieve_related_sample_queries(user_msg, k=10)
    with st.chat_message("assistant"):
        st.markdown(
            f"関連するサンプルクエリを取得しました! {', '.join(list(related_sql_by_query_name.keys())[0:3])}, ..."
        )
        with st.expander("取得されたサンプルクエリの詳細を見る"):
            for query_name, sql in related_sql_by_query_name.items():
                st.write(f"クエリ名: {query_name}")
                st.code(sql, language="sql", wrap_lines=True)

    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": f"関連するサンプルクエリが取得されました: {', '.join(list(related_sql_by_query_name.keys())[0:3])}, ...",
        }
    )

    # SQLクエリを生成
    sql_query, explanation = text2sql_facade.text2sql(
        user_msg,
        sql_dialect,
        tables_metadata="\n\n".join(related_metadata_by_table.values()),
        related_sample_queries="\n\n".join(related_sql_by_query_name.values()),
    )
    with st.chat_message("assistant"):
        st.markdown("SQLクエリを生成しました!")
        st.code(sql_query, language="sql", line_numbers=True)
        st.markdown(f"{explanation}")

    st.session_state["chat_history"].append({"role": "assistant", "content": "SQLクエリを生成中..."})

# st.subheader("オフラインバッチ実行")

# # オフラインバッチの検索インデックス登録の実行ボタン (これは表示させない方が良いかも)
# with st.container():
#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("テーブルスキーマとサンプルクエリの要約を更新"):
#             try:
#                 result = subprocess.run(
#                     [
#                         "python",
#                         "-m",
#                         "my_text_to_sql_poc.app.generate_summary_batch",
#                         "--schema-dir",
#                         "data/schema",
#                         "--sample-queries-dir",
#                         "data/sample_queries",
#                         "--output-schema-dir",
#                         "data/summarized_schema",
#                         "--output-queries-dir",
#                         "data/summarized_sample_queries",
#                     ],
#                     capture_output=True,
#                     text=True,
#                     check=True,
#                 )
#                 st.success("テーブルスキーマとサンプルクエリの要約を更新しました")
#             except subprocess.CalledProcessError as e:
#                 st.error(f"要約生成バッチの実行に失敗しました: {e.stderr}")

#     with col2:
#         if st.button("要約を埋め込み表現に変換してベクトルDBを更新"):
#             try:
#                 result = subprocess.run(
#                     [
#                         "python",
#                         "-m",
#                         "my_text_to_sql_poc.app.embed_summaries_batch",
#                         "--table-summary-dir",
#                         "data/summarized_schema",
#                         "--query-summary-dir",
#                         "data/summarized_sample_queries",
#                         "--vectorstore-file",
#                         "sample_vectorstore.duckdb",
#                     ],
#                     capture_output=True,
#                     text=True,
#                     check=True,
#                 )
#                 st.success("埋め込み生成バッチの実行が完了しました")
#             except subprocess.CalledProcessError as e:
#                 st.error(f"埋め込み生成バッチの実行に失敗しました: {e.stderr}")
