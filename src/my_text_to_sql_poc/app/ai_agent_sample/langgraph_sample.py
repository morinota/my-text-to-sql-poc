import json
import tempfile
from typing import Annotated

import matplotlib.image as mpimg
import networkx as nx
from IPython.display import Image, display
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from matplotlib import pyplot as plt
from pydantic import BaseModel
from typing_extensions import TypedDict

memory = MemorySaver()  # in-memory checkpointerを定義


class RequestAssistance(BaseModel):
    """
    会話を専門家にエスカレーションします。
    直接支援できない場合や、ユーザーがあなたの権限を超えた支援を必要とする場合に使用します。
    この機能を使用するには、ユーザを中継して、専門家が適切なガイダンスを提供できるようにします。
    """

    request: str


class State(TypedDict):
    messages: Annotated[list, add_messages]
    ask_human: bool


tavily_tool = TavilySearchResults(max_results=2)

repl = PythonREPL()


@tool
def python_repl(code: Annotated[str, "チャートを生成するために実行する Python コード"]):
    """
    これを使用して Python コードを実行します。
    値の出力を確認したい場合は、`print(...)` で出力する必要があります。
    これはユーザーに表示されます。
    """
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Succesfully executed:\\\\n`python\\\\\\\\n{code}\\\\\\\\n`\\\\nStdout: {result}"


tools = [tavily_tool, python_repl]


def tool_node(state: State) -> State:
    """
    これにより、グラフ内のツールが実行されます。
    エージェントのアクションを受け取り、そのツールを呼び出して結果を返します。
    """
    messages = state["messages"]
    last_message = messages[-1]
    tool_input = json.loads(
        last_message.additional_kwargs["function_call"]["arguments"],
    )


llm = ChatOpenAI(model="gpt-4o-mini")
# We can bind the llm to a tool definition, a pydantic model, or a json schema
# 私たちはllmをツール定義、pydanticモデル、またはjsonスキーマにバインドすることができる
llm_with_tools = llm.bind_tools(tools + [RequestAssistance])


def chatbot(state: State) -> State:
    """chatbotノードは、メッセージを受け取り、OpenAIの言語モデルを使用して応答を生成します。"""
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if response.tool_calls and response.tool_calls[0]["name"] == RequestAssistance.__name__:
        ask_human = True
    return {"messages": [response], "ask_human": ask_human}


# グラフビルダーを作成し、チャットボットとツールノードをグラフに追加
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))


# 人間ノードを作成する
def create_response(response: str, ai_message: AIMessage) -> ToolMessage:
    return ToolMessage(content=response, tool_call_id=ai_message.tool_calls[0]["id"])


def human_node(state: State) -> State:
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        new_messages.append(create_response("No response from human.", state["messages"][-1]))
    return {"messages": new_messages, "ask_human": False}


graph_builder.add_node("human", human_node)


# 条件ロジックを定義
def selext_next_node(state: State) -> str:
    if state["ask_human"]:
        return "human"
    return tools_condition(state)


graph_builder.add_conditional_edges(
    source="chatbot",
    path=selext_next_node,
    path_map={"tools": "tools", "human": "human", END: END},
)

# 最後に、シンプルな有向エッジを追加し、グラフをコンパイルする
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
    # humanノードの通過前にグラフを中断する
    interrupt_before=["human"],
)

try:
    png_data = graph.get_graph().draw_mermaid_png()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(png_data)
        tmp_file_path = tmp_file.name
        # matplotlibで画像ウィンドウを開く
        img = mpimg.imread(tmp_file_path)
        plt.imshow(img)
        plt.axis("off")  # 軸を非表示にする
        plt.show()

except Exception:
    # This requires some extra dependencies and is optional
    pass

# # 条件付きエッジを、グラフに追加 (意味: チャットボットノードが実行されるたびに、ツールを呼び出す場合は'tools'に行き、直接応答する場合はループを終了する)
graph_builder.add_conditional_edges(
    source="chatbot",
    path=tools_condition,
    # 以下のdictionaryを使用して、条件の出力を特定のノードとして解釈するようにグラフに指示できる
    # デフォルトでは恒等関数(i.e. key=valueのmap!)になりますが、"tools"以外の名前のノードを使用したい場合は、辞書のvalueを他のものに更新できる。
    # あなたは、"tools": "my_tools"のようなものに辞書の値を更新することができる
    path_map={"tools": "tools", END: END},
)

# graph_builder.add_edge(
#     START, "chatbot"
# )  # グラフにエントリーポイントを定義(グラフが実行される度に作業を開始するノードを指定する)(STARTノードからchatbotノードへのエッジを追加)
# graph_builder.add_edge(
#     "tools", "chatbot"
# )  # toolsからchatbotへのエッジを追加(chatbotノードからtoolsノードへのエッジはすでにconditional_edgesで追加されている)


def route_tools(state: State) -> str | list[str]:
    """ルーティング関数をチュートリアル用に自作する。
    現在のグラフ状態を受け取り、次に呼び出すノードを示す 文字列or文字列のlist を返す。
    基本的には自作せず、build-inのtools_conditionnルート関数を使えばOK!
    """
    if isinstance(state, list):
        # stateをlist形式で定義している場合は、最後尾の要素を取得
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        # stateをdict形式で定義している場合は、messagesキーの最後尾の要素を取得
        ai_message: AIMessage = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


user_input = "こんにちは! スペイン語で「おはよう」は何ですか？"
config = {"configurable": {"thread_id": "1"}}
# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
