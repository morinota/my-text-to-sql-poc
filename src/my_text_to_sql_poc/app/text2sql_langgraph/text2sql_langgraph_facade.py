from typing import Annotated, Any, Literal

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
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
print(db.dialect)
print(db.get_usable_table_names())


# グラフのstateを定義
class State(TypedDict):
    # add_messages reducer関数を指定しているので、上書きされずに追加される
    messages: Annotated[list[AnyMessage], add_messages]


class Text2SQLGraphFacade:
    def __init__(self) -> None:
        graph_builder = StateGraph(State)

        # グラフビルダーに、定義したノード達を追加していく


@tool
def retrieve_related_tables(question: str, k: int = 20) -> dict[str, str]:
    """
    ユーザの質問に関連するテーブルを取得します。
    """
    return {"albums": "アルバム情報", "artists": "アーティスト情報"}


def create_tool_node_with_fallback(tools: list) -> RunnableWithFallbacks[Any, dict]:
    """
    ツールノードを作成する関数。
    その際、エラーを処理し、エージェントにエラーを通知するためのフォールバックを追加している
    """
    return ToolNode(tools).with_fallbacks([RunnableLambda(handle_tool_error)], exception_key="error")


def handle_tool_error(state: State) -> State:
    """ツールのエラーを処理する関数
    (これも、stateを受け取り、stateを返す関数にしてる? ノード関数と同じ...!:thinking_face:)
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\nplease fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


# pre-buildのtool関数達を取得
sql_toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o-mini"))
tools = sql_toolkit.get_tools()
list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

print(list_tables_tool.invoke(""))
print(get_schema_tool.invoke("albums"))


# dbに対してクエリを実行するtoolを定義する
@tool
def db_query_tool(query: str) -> str:
    """
    データベースに対してSQLクエリを実行し、結果を取得します。
    もしクエリが正しくない場合、エラーメッセージが返されます。
    もしエラーが返された場合、クエリを書き直し、クエリをチェックして、もう一度試してください。
    """
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result


@tool
def explain_query_tool(query: str) -> str:
    """
    渡されたsqlクエリに関して、explainコマンドを実行し、結果を取得します。
    もしクエリが正しくない場合、エラーメッセージが返されます。
    もしエラーが返された場合、クエリを書き直し、クエリをチェックして、もう一度試してください。
    """
    result = db.run_no_throw(f"EXPLAIN {query}")
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result


# print(db_query_tool.invoke("SELECT * FROM query_embeddings limit 2;"))
print(explain_query_tool.invoke("SELECT * FROM query_embeddings limit 2;"))
print("hoge")


# エントリーポイントにつながる、最初に必ず呼び出されるノード関数を定義
def first_tool_call(state: State) -> State:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": "sql_db_list_tables", "args": {}, "id": "tool_abcd123"}],
            )
        ]
    }


query_check_system = """
あなたはSQLの専門家であり、注意深くSQLiteクエリを再確認する役割を持っています。以下の一般的なミスがないか確認してください：

- NULL値を含むNOT INの使用
- UNION ALLを使用すべき場面でUNIONを使用している
- 排他的範囲に対してBETWEENを使用している
- 条件式におけるデータ型の不一致
- 識別子を適切に引用符で囲んでいるか
- 関数に正しい数の引数を使用しているか
- 正しいデータ型にキャストしているか
- 結合に適切なカラムを使用しているか

上記のいずれかのミスがあった場合は、クエリを修正してください。ミスがなければ、元のクエリをそのまま出力してください。
"""
query_check_prompt = ChatPromptTemplate.from_messages([("system", query_check_system), ("placeholder", "{messages}")])
query_check_pipeline = query_check_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(
    [db_query_tool], tool_choice="required"
)
query_check_pipeline.invoke({"messages": [("user", "SELECT * FROM query_embeddings limit 2;")]})


# クエリが正しいかどうかを実行するノードを定義
def model_check_query(state: State) -> State:
    """Use this tool to double-check if your query is correct before executing it."""

    return {"messages": [query_check_pipeline.invoke({"messages": [state["messages"][-1]]})]}


# 質問と利用可能なテーブル一覧をもとに、関連テーブルを選ぶノードを定義
model_get_schema = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([get_schema_tool])


def select_related_tables(state: State) -> State:
    return {"messages": [model_get_schema.invoke(state["messages"])]}


# 終了状態を表すツールを記述
class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="The final answer to the user")


# 質問と、関連テーブルのスキーマを元にクエリを生成するモデルのノードを追加
query_gen_system = """あなたはSQLの専門家であり、正確かつ詳細にSQLクエリを生成する役割を持っています。入力された質問に基づいて、質問に答えるための構文的に正しいSQLiteのクエリを生成してください。生成したクエリそのものが最終的な出力となります。クエリを生成する際の注意点は以下の通りです。

- 質問に答えるためのSQLクエリを出力してください。クエリの実行結果やその内容については考慮せず、質問を解決するために必要なクエリのみを正確に生成してください。
- ユーザーが特定の件数を指定しない限り、結果は最大で5件に制限してください。
- データベース内の興味深い例を返すために、関連する列で結果を並べ替えてください。
- 特定のテーブルから全てのカラムを取得することは避け、質問に関連するカラムのみを選択してください。
- クエリの構文エラーや実行エラーを避けるため、正しいSQL文を生成するよう心掛けてください。
- 情報が不足していて質問に答えられない場合、「質問に答えるための情報が不足しています」とだけ回答してください。
- データベースに対してDML文（INSERT、UPDATE、DELETE、DROPなど）を生成しないでください。

入力された質問に対する適切なSQLクエリを作成し、それを最終的な回答としてユーザーに提供してください。"""
query_gen_prompt = ChatPromptTemplate.from_messages([("system", query_gen_system), ("placeholder", "{messages}")])
query_gen = query_gen_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([SubmitFinalAnswer])


def query_generate_node(state: State) -> State:
    message = query_gen.invoke(state)

    tool_messages = []
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call["name"] != "SubmitFinalAnswer":
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tool_call['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tool_call["id"],
                    )
                )
    else:
        tool_messages = []
    return {"messages": [message] + tool_messages}


# 条件付きエッジを登録するための、ルーティング関数を定義
def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]:
    messages = state["messages"]
    last_message = messages[-1]
    # If there is a tool call, then we finish
    if getattr(last_message, "tool_calls", None):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"


if __name__ == "__main__":
    graph_builder = StateGraph(State)

    # グラフビルダーに、定義したノード達を追加していく
    ## 最初に必ず呼び出されるノード
    graph_builder.add_node("first_tool_call", first_tool_call)
    ## 利用可能なテーブル一覧を取得するノード
    graph_builder.add_node("list_tables_tool", create_tool_node_with_fallback([list_tables_tool]))
    ## 指定したテーブルのスキーマを取得するノード
    graph_builder.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))
    ## 関連テーブルを選ぶノード
    graph_builder.add_node("select_related_tables", select_related_tables)
    ## クエリを生成するノード
    graph_builder.add_node("query_gen", query_generate_node)
    # クエリを実行する前に、モデルがクエリをチェックするノード
    graph_builder.add_node("correct_query", model_check_query)
    ## クエリを実際にDBに投げるノード
    # graph_builder.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))

    ## グラフビルダーにエッジ達を登録
    graph_builder.add_edge(START, "first_tool_call")
    graph_builder.add_edge("first_tool_call", "list_tables_tool")
    graph_builder.add_edge("list_tables_tool", "select_related_tables")
    graph_builder.add_edge("select_related_tables", "get_schema_tool")
    graph_builder.add_edge("get_schema_tool", "query_gen")
    graph_builder.add_conditional_edges(
        "query_gen",
        should_continue,
        path_map={"correct_query": "correct_query", "query_gen": "query_gen", END: END},
    )
    # graph_builder.add_edge("correct_query", "execute_query")
    # graph_builder.add_edge("execute_query", "query_gen")
    graph_builder.add_edge("correct_query", "query_gen")

    # グラフのstateを保存するためのcheckpointerの定義
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "1"}}

    # グラフを実行できるようにコンパイル
    graph = graph_builder.compile(checkpointer=memory)
    print(graph.get_graph().draw_mermaid())

    # 実行してみる
    messages = graph.invoke(
        {"messages": [("user", "アルバムの収益ランキングは?")]},
        config,
    )
    # 最後のメッセージのツールコールから、最終的な回答を取得
    json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
    print(f"最終的な回答: {json_str}")

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
