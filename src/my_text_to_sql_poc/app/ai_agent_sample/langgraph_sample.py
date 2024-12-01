import json
from typing import Annotated

import networkx as nx
from IPython.display import Image, display
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")


class State(TypedDict):
    # messagesは型「list」型を持ちます。`add_messages`アノテーションは、このステートキーがどのように更新されるかを定義します
    # （この場合、それらを上書きするのではなく、メッセージをリストに追加します）
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)


def chatbot(state: State) -> State:
    """chatbotノードは、メッセージを受け取り、OpenAIの言語モデルを使用して応答を生成します。"""
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)  # グラフにノードを追加


class BasicToolNode:
    """
    最後のAIMessageでリクエストされたツールを実行するノード。
    基本的には自作せず、build-inのToolNodeクラスを使えばOK!
    """

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict) -> State:
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])  # ツールノードをインスタンス化
graph_builder.add_node("tools", tool_node)  # グラフにノードを追加


def route_tools(state: State):
    """ルーティング関数。現在のグラフ状態を受け取り、次に呼び出すノードを示す文字列or文字列のlistを返す。
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


# 条件付きエッジを、グラフに追加 (意味: チャットボットノードが実行されるたびに、ツールを呼び出す場合は'tools'に行き、直接応答する場合はループを終了する)
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # 以下のdictionaryを使用して、条件の出力を特定のノードとして解釈するようにグラフに指示できる
    # デフォルトでは恒等関数(i.e. key=valueのmap!)になりますが、"tools"以外の名前のノードを使用したい場合は、辞書の値を他のものに更新できる。
    # あなたは、"tools": "my_tools"のようなものに辞書の値を更新することができる
    path_map={"tools": "tools", END: END},
)


graph_builder.add_edge(
    START, "chatbot"
)  # グラフにエントリーポイントを定義(グラフが実行される度に作業を開始するノードを指定する)(STARTノードからchatbotノードへのエッジを追加)
graph_builder.add_edge(
    "tools", "chatbot"
)  # toolsからchatbotへのエッジを追加(chatbotノードからtoolsノードへのエッジはすでにconditional_edgesで追加されている)

# 最後に、グラフを実行可能にする (CompiledGraphが作成される)
graph = graph_builder.compile()

print(graph.get_graph().draw_mermaid())


def stream_graph_updates(user_input: str) -> None:
    """ユーザー入力を受け取り、グラフを実行して応答を生成します。"""
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
