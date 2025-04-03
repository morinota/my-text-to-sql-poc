from typing import Annotated, Any, Literal

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableWithFallbacks
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# 接続したいDBを定義する(ここが実務では、DWHになる?)
# duckdb_path = "sample_database.duckdb"
duckdb_path = "duckdb:///sample_vectorstore.duckdb"
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
# print(db.dialect)
# print(db.get_usable_table_names())


class InputState(BaseModel):
    # add_messages reducer関数を指定しているので、必ずappendされていく(上書きされない)
    messages: Annotated[list[AnyMessage], add_messages]


class OutputState(BaseModel):
    retrieved_tables: dict[str, str] = Field(description="ユーザの質問への関連テーブル")
    retrieved_sample_queries: dict[str, str] = Field(description="ユーザの質問への関連サンプルクエリ")
    sql_query: str = Field(description="生成されたSQLクエリ")
    explanation: str = Field(description="生成されたSQLクエリに関する説明文")


# グラフのstateを定義
class OverallState(InputState, OutputState):
    # add_messages reducer関数を指定しているので、上書きされずに追加される
    pass


def node_1(state: InputState, config: RunnableConfig) -> OutputState:
    """
    ユーザの質問に関連するテーブルを取得します。
    """
    # ここで、ユーザの質問に関連するテーブルを取得する処理を実装
    # 例えば、DBから関連するテーブルを取得するなど
    # ここでは、ダミーのデータを返す
    related_tables = {
        "albums": "アルバム情報",
        "artists": "アーティスト情報",
    }
    related_sample_queries = {
        "query1": "SELECT * FROM albums WHERE artist_id = 1",
        "query2": "SELECT * FROM artists WHERE name LIKE '%Smith%'",
    }
    return OutputState(
        retrieved_tables=related_tables,
        retrieved_sample_queries=related_sample_queries,
        sql_query="",
        explanation="",
    )


def node_2(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    ユーザの質問に対してSQLクエリを生成します。
    """
    user_query = state.messages[-1].content
    related_tables = state.retrieved_tables
    related_sample_queries = state.retrieved_sample_queries
    prompt = (
        f"SQL作るプロンプト! 質問: {user_query} テーブル: {related_tables} サンプルクエリ: {related_sample_queries}"
    )

    # ここで、SQLクエリを生成する処理を実装
    generated_query = "SELECT * FROM hoge"
    generated_explanation = "ダミーの説明文です!"

    return OverallState(
        retrieved_tables=state.retrieved_tables,
        retrieved_sample_queries=state.retrieved_sample_queries,
        sql_query=generated_query,
        explanation=generated_explanation,
        messages=[
            SystemMessage(f"{prompt}"),
            AIMessage(f"generated query: {generated_query}, explanation: {generated_explanation}"),
        ],
    )


graph_builder = StateGraph(OverallState)
graph_builder.add_node(node_1)
graph_builder.add_node(node_2)
graph_builder.set_entry_point("node_1")
graph_builder.add_edge("node_1", "node_2")

memory = MemorySaver()
# グラフを実行
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
print(
    graph.invoke(
        InputState(messages=[HumanMessage("アルバムの収益ランキングは?")]),
        config=config,
    )
)


class Text2SQLGraphFacade:
    def __init__(self) -> None:
        graph_builder = StateGraph(OverallState)

        # グラフビルダーに、定義したノード達を追加していく


# # pre-buildのtool関数達を取得
# sql_toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o-mini"))
# tools = sql_toolkit.get_tools()
# list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
# get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

# print(list_tables_tool.invoke(""))
# print(get_schema_tool.invoke("albums"))


# # dbに対してクエリを実行するtoolを定義する
# @tool
# def db_query_tool(query: str) -> str:
#     """
#     データベースに対してSQLクエリを実行し、結果を取得します。
#     もしクエリが正しくない場合、エラーメッセージが返されます。
#     もしエラーが返された場合、クエリを書き直し、クエリをチェックして、もう一度試してください。
#     """
#     result = db.run_no_throw(query)
#     if not result:
#         return "Error: Query failed. Please rewrite your query and try again."
#     return result


# @tool
# def explain_query_tool(query: str) -> str:
#     """
#     渡されたsqlクエリに関して、explainコマンドを実行し、結果を取得します。
#     もしクエリが正しくない場合、エラーメッセージが返されます。
#     もしエラーが返された場合、クエリを書き直し、クエリをチェックして、もう一度試してください。
#     """
#     result = db.run_no_throw(f"EXPLAIN {query}")
#     if not result:
#         return "Error: Query failed. Please rewrite your query and try again."
#     return result


# # print(db_query_tool.invoke("SELECT * FROM query_embeddings limit 2;"))
# print(explain_query_tool.invoke("SELECT * FROM query_embeddings limit 2;"))
# print("hoge")


# # エントリーポイントにつながる、最初に必ず呼び出されるノード関数を定義
# def first_tool_call(state: OverallState) -> OverallState:
#     return {
#         "messages": [
#             AIMessage(
#                 content="",
#                 tool_calls=[{"name": "sql_db_list_tables", "args": {}, "id": "tool_abcd123"}],
#             )
#         ]
#     }


# query_check_system = """
# あなたはSQLの専門家であり、注意深くSQLiteクエリを再確認する役割を持っています。以下の一般的なミスがないか確認してください：

# - NULL値を含むNOT INの使用
# - UNION ALLを使用すべき場面でUNIONを使用している
# - 排他的範囲に対してBETWEENを使用している
# - 条件式におけるデータ型の不一致
# - 識別子を適切に引用符で囲んでいるか
# - 関数に正しい数の引数を使用しているか
# - 正しいデータ型にキャストしているか
# - 結合に適切なカラムを使用しているか

# 上記のいずれかのミスがあった場合は、クエリを修正してください。ミスがなければ、元のクエリをそのまま出力してください。
# """
# query_check_prompt = ChatPromptTemplate.from_messages([("system", query_check_system), ("placeholder", "{messages}")])
# query_check_pipeline = query_check_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(
#     [db_query_tool], tool_choice="required"
# )
# query_check_pipeline.invoke({"messages": [("user", "SELECT * FROM query_embeddings limit 2;")]})


# # クエリが正しいかどうかを実行するノードを定義
# def model_check_query(state: OverallState) -> OverallState:
#     """Use this tool to double-check if your query is correct before executing it."""

#     return {"messages": [query_check_pipeline.invoke({"messages": [state["messages"][-1]]})]}


# # 質問と利用可能なテーブル一覧をもとに、関連テーブルを選ぶノードを定義
# model_get_schema = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([get_schema_tool])


# def select_related_tables(state: OverallState) -> OverallState:
#     return {"messages": [model_get_schema.invoke(state["messages"])]}


# # 終了状態を表すツールを記述
# class SubmitFinalAnswer(BaseModel):
#     final_answer: str = Field(..., description="The final answer to the user")


# # 質問と、関連テーブルのスキーマを元にクエリを生成するモデルのノードを追加
# query_gen_system = """あなたはSQLの専門家であり、正確かつ詳細にSQLクエリを生成する役割を持っています。入力された質問に基づいて、質問に答えるための構文的に正しいSQLiteのクエリを生成してください。生成したクエリそのものが最終的な出力となります。クエリを生成する際の注意点は以下の通りです。

# - 質問に答えるためのSQLクエリを出力してください。クエリの実行結果やその内容については考慮せず、質問を解決するために必要なクエリのみを正確に生成してください。
# - ユーザーが特定の件数を指定しない限り、結果は最大で5件に制限してください。
# - データベース内の興味深い例を返すために、関連する列で結果を並べ替えてください。
# - 特定のテーブルから全てのカラムを取得することは避け、質問に関連するカラムのみを選択してください。
# - クエリの構文エラーや実行エラーを避けるため、正しいSQL文を生成するよう心掛けてください。
# - 情報が不足していて質問に答えられない場合、「質問に答えるための情報が不足しています」とだけ回答してください。
# - データベースに対してDML文（INSERT、UPDATE、DELETE、DROPなど）を生成しないでください。

# 入力された質問に対する適切なSQLクエリを作成し、それを最終的な回答としてユーザーに提供してください。"""
# query_gen_prompt = ChatPromptTemplate.from_messages([("system", query_gen_system), ("placeholder", "{messages}")])
# query_gen = query_gen_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([SubmitFinalAnswer])


# def query_generate_node(state: OverallState) -> OverallState:
#     message = query_gen.invoke(state)

#     tool_messages = []
#     if message.tool_calls:
#         for tool_call in message.tool_calls:
#             if tool_call["name"] != "SubmitFinalAnswer":
#                 tool_messages.append(
#                     ToolMessage(
#                         content=f"Error: The wrong tool was called: {tool_call['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
#                         tool_call_id=tool_call["id"],
#                     )
#                 )
#     else:
#         tool_messages = []
#     return {"messages": [message] + tool_messages}


if __name__ == "__main__":
    pass
    # # グラフビルダーに、定義したノード達を追加していく
    # ## 最初に必ず呼び出されるノード
    # graph_builder.add_node("first_tool_call", first_tool_call)
    # ## 利用可能なテーブル一覧を取得するノード
    # graph_builder.add_node("list_tables_tool", create_tool_node_with_fallback([list_tables_tool]))
    # ## 指定したテーブルのスキーマを取得するノード
    # graph_builder.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))
    # ## 関連テーブルを選ぶノード
    # graph_builder.add_node("select_related_tables", select_related_tables)
    # ## クエリを生成するノード
    # graph_builder.add_node("query_gen", query_generate_node)
    # # クエリを実行する前に、モデルがクエリをチェックするノード
    # graph_builder.add_node("correct_query", model_check_query)
    # ## クエリを実際にDBに投げるノード
    # # graph_builder.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))

    # ## グラフビルダーにエッジ達を登録
    # graph_builder.add_edge(START, "first_tool_call")
    # graph_builder.add_edge("first_tool_call", "list_tables_tool")
    # graph_builder.add_edge("list_tables_tool", "select_related_tables")
    # graph_builder.add_edge("select_related_tables", "get_schema_tool")
    # graph_builder.add_edge("get_schema_tool", "query_gen")
    # graph_builder.add_conditional_edges(
    #     "query_gen",
    #     should_continue,
    #     path_map={"correct_query": "correct_query", "query_gen": "query_gen", END: END},
    # )
    # # graph_builder.add_edge("correct_query", "execute_query")
    # # graph_builder.add_edge("execute_query", "query_gen")
    # graph_builder.add_edge("correct_query", "query_gen")

    # # グラフのstateを保存するためのcheckpointerの定義
    # memory = MemorySaver()
    # config = {"configurable": {"thread_id": "1"}}

    # # グラフを実行できるようにコンパイル
    # graph = graph_builder.compile(checkpointer=memory)
    # print(graph.get_graph().draw_mermaid())

    # # 実行してみる
    # messages = graph.invoke(
    #     {"messages": [("user", "アルバムの収益ランキングは?")]},
    #     config,
    # )
    # # 最後のメッセージのツールコールから、最終的な回答を取得
    # json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
    # print(f"最終的な回答: {json_str}")

    # # 実行
    # user_input = "2009年に最も売上を上げた営業担当者は誰ですか？"
    # events = graph.stream(
    #     {"messages": [("user", user_input)]},
    #     config,
    #     stream_mode="values",
    # )
    # for event in events:
    #     event["messages"][-1].pretty_print()

    # 再び質問してみる
    # user_input = "じゃあ、何年のものなら分かりますか??"
    # messages = graph.invoke(
    #     {"messages": [("user", user_input)]},
    #     config,
    # )
    # json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
    # print(f"最終的な回答: {json_str}")
