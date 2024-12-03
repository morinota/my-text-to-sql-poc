import json
from typing import Annotated

import networkx as nx
from IPython.display import Image, display
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

memory = MemorySaver()  # in-memory checkpointerを定義


class State(TypedDict):
    # messagesは型「list」型を持ちます。`add_messages`アノテーションは、このステートキーがどのように更新されるかを定義します
    # （この場合、それらを上書きするのではなく、メッセージをリストに追加します）
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


tool = TavilySearchResults(max_results=2)
llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools([tool])


def chatbot(state: State) -> State:
    """chatbotノードは、メッセージを受け取り、OpenAIの言語モデルを使用して応答を生成します。"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)  # グラフにノードを追加
tool_node = ToolNode(tools=[tool])  # ツールノードをインスタンス化
graph_builder.add_node("tools", tool_node)  # グラフにノードを追加

# 条件付きエッジを、グラフに追加 (意味: チャットボットノードが実行されるたびに、ツールを呼び出す場合は'tools'に行き、直接応答する場合はループを終了する)
graph_builder.add_conditional_edges(
    source="chatbot",
    path=tools_condition,
    # 以下のdictionaryを使用して、条件の出力を特定のノードとして解釈するようにグラフに指示できる
    # デフォルトでは恒等関数(i.e. key=valueのmap!)になりますが、"tools"以外の名前のノードを使用したい場合は、辞書のvalueを他のものに更新できる。
    # あなたは、"tools": "my_tools"のようなものに辞書の値を更新することができる
    path_map={"tools": "tools", END: END},
)

graph_builder.add_edge(
    START, "chatbot"
)  # グラフにエントリーポイントを定義(グラフが実行される度に作業を開始するノードを指定する)(STARTノードからchatbotノードへのエッジを追加)
graph_builder.add_edge(
    "tools", "chatbot"
)  # toolsからchatbotへのエッジを追加(chatbotノードからtoolsノードへのエッジはすでにconditional_edgesで追加されている)


def route_tools(state: State) -> str | list[str]:
    """ルーティング関数をチュートリアル用に自作する。
    現在のグラフ状態を受け取り、次に呼び出すノードを示す 文字列or文字列のlist を返す。
    基本的には自作せず、build-inのtools_conditionnルート関数を使えばOK!
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# 最後に、グラフを実行可能にする (CompiledGraphが作成される)
graph = graph_builder.compile(
    checkpointer=memory,  # stateを保存するためのcheckpointerを指定
    interrupt_before=["tools"],  # toolsノードの通過前にグラフを中断する
)
print(graph.get_graph().draw_mermaid())

user_input = "I'm learning LangGraph. Could you do some research on it for me?"
config = {"configurable": {"thread_id": "1"}}
events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
print(f"{snapshot.next=}")

existing_message = snapshot.values["messages"][-1]
print(existing_message.tool_calls)

# Noneを指定して呼び出すと、現在の状態に何も追加されず、中断されていなかったかのように再開される
events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
