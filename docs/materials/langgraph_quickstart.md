
# 🚀 LangGraph クイックスタート

In this tutorial, we will build a support chatbot in LangGraph that can:
このチュートリアルでは、LangGraphでサポートチャットボットを構築します。これにより、以下のことが可能になります：
✅Answer common questions by searching the web
✅ウェブを検索して一般的な質問に答える
✅Maintain conversation state across calls
✅呼び出し間で会話の状態を維持する
✅Route complex queries to a human for review
✅複雑なクエリを人間にルーティングしてレビューを受ける
✅Use custom state to control its behavior
✅カスタムステートを使用してその動作を制御する
✅Rewind and explore alternative conversation paths
✅巻き戻して代替の会話パスを探る

We'll start with a basic chatbot and progressively add more sophisticated capabilities, introducing key LangGraph concepts along the way.
基本的なチャットボットから始め、徐々により高度な機能を追加しながら、途中で重要なLangGraphの概念を紹介していきます。

Let’s dive in! 🌟
さあ、始めましょう！🌟

## Setup セットアップ

First, install the required packages and configure your environment:
まず、必要なパッケージをインストールし、環境を設定します：

```
%%capture--no-stderr%pipinstall-Ulanggraphlangsmithlangchain_anthropic
```

```
importgetpassimportosdef_set_env(var:str):ifnotos.environ.get(var):os.environ[var]=getpass.getpass(f"{var}: ")_set_env("ANTHROPIC_API_KEY")
```

```
ANTHROPIC_API_KEY:  ········
```

Set up LangSmith for LangGraph development
LangGraph開発のためにLangSmithを設定します。
Sign up for LangSmith to quickly spot issues and improve the performance of your LangGraph projects.
LangSmithにサインアップして、問題を迅速に特定し、LangGraphプロジェクトのパフォーマンスを向上させましょう。
LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph — read more about how to get started here.
LangSmithを使用すると、LangGraphで構築したLLMアプリをデバッグ、テスト、監視するためにトレースデータを利用できます — こちらで始める方法について詳しく読むことができます。

## Part 1: Build a Basic Chatbot¶ 基本的なチャットボットの構築

We'll first create a simple chatbot using LangGraph.
まず、LangGraphを使用してシンプルなチャットボットを作成します。
This chatbot will respond directly to user messages.
このチャットボットは、ユーザのメッセージに直接応答します。
Though simple, it will illustrate the core concepts of building with LangGraph.
シンプルではありますが、LangGraphを使用した構築の基本概念を示します。
By the end of this section, you will have a built rudimentary chatbot.
このセクションの終わりまでには、基本的なチャットボットが構築できるようになります。

Start by creating a StateGraph.
StateGraphを作成することから始めます。
A StateGraph object defines the structure of our chatbot as a "state machine".
StateGraphオブジェクトは、チャットボットの構造を「状態遷移機」として定義します。
We'll add nodes to represent the llm and functions our chatbot can call and edges to specify how the bot should transition between these functions.
チャットボットが呼び出すことができるllmや関数を表すノードを追加し、これらの関数間でボットがどのように遷移するかを指定するエッジを追加します。

```
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
```

Our graph can now handle two key tasks:
これで、私たちのグラフは2つの重要なタスクを処理できるようになりました。

- Each node can receive the current State as input and output an update to the state. 各ノードは、現在のStateを入力として受け取り、状態の更新を出力できます。
- Updates to messages will be appended to the existing list rather than overwriting it, thanks to the prebuilt add_messages function used with the Annotated syntax. Annotated構文を使用して事前に構築されたadd_messages関数を使用するため、メッセージの更新は既存のリストに追加され、上書きされません。

Concept
概念
When defining a graph, the first step is to define its State.
**グラフを定義する際の最初のステップは、その状態を定義すること**です。
The State includes the graph's schema and reducer functions that handle state updates.
**状態には、グラフのスキーマと状態更新を処理するリデューサ関数**が含まれます。
In our example, State is a TypedDict with one key: messages.
私たちの例では、**Stateは1つのキー（messages）を持つTypedDict**です。
The add_messages reducer function is used to append new messages to the list instead of overwriting it.
add_messagesリデューサ関数は、新しいメッセージをリストに追加するために使用され、上書きすることはありません。
Keys without a reducer annotation will overwrite previous values.
**リデューサ注釈のないキーは、以前の値を上書きします**。
Learn more about state, reducers, and related concepts in this guide.
このガイドで状態、リデューサ、および関連する概念について詳しく学びましょう。

Next, add a "chatbot" node.
次に、「チャットボット」ノードを追加します。
Nodes represent units of work.
**ノードは作業の単位を表します**。
They are typically regular python functions.
**ノードは通常、通常のPython関数**です。

```
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
```

Notice how the chatbot node function takes the current State as input and returns a dictionary containing an updated messages list under the key "messages".
chatbotノード関数が**現在のStateを入力として受け取り**、**"messages"キーの下に更新されたメッセージリストを含む辞書を返すこと**に注意してください。
This is the basic pattern for all LangGraph node functions.
これは、**すべてのLangGraphノード関数の基本的なパターン**です。

The add_messages function in our State will append the llm's response messages to whatever messages are already in the state.
私たちのState内のadd_messages関数は、llmの応答メッセージを状態に既に存在するメッセージに追加します。

Next, add an entry point.
次に、**エントリーポイントを追加**します。
This tells our graph where to start its work each time we run it.
これは、グラフが実行されるたびに作業を開始する場所を指示します。(場所ってノードってことだよね...!:thinking_face:)

```
graph_builder.add_edge(START, "chatbot")
```

Similarly, set a finish point.
同様に、フィニッシュポイントを設定します。
This instructs the graph "any time this node is run, you can exit."
これは、グラフに「**このノードが実行されるたびに、終了できます**」と指示します。

```
graph_builder.add_edge("chatbot", END)
```

Finally, we'll want to be able to run our graph.
最後に、**グラフを実行できるようにしたい**と思います。
To do so, call "compile()" on the graph builder.
そのためには、グラフビルダーで"compile()"を呼び出します。
This creates a "CompiledGraph" we can use invoke on our state.
これにより、状態で**invokeを使用できる「CompiledGraph」が作成されます**。

```
graph = graph_builder.compile()
```

You can visualize the graph using the get_graph method and one of the "draw" methods, like draw_ascii or draw_png.
get_graphメソッドとdraw_asciiやdraw_pngのいずれかの「draw」メソッドを使用して、グラフを視覚化できます。
The draw methods each require additional dependencies.
drawメソッドはそれぞれ追加の依存関係を必要とします。

```
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

Now let's run the chatbot!
さあ、チャットボットを実行してみましょう！
Tip: You can exit the chat loop at any time by typing "quit", "exit", or "q".
ヒント：いつでも「quit」、「exit」、または「q」と入力することでチャットループを終了できます。

```
def stream_graph_updates(user_input: str):
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
```

```
Assistant: LangGraph is a library designed to help build stateful multi-agent applications using language models. 
アシスタント：LangGraphは、言語モデルを使用して状態を持つマルチエージェントアプリケーションを構築するのに役立つライブラリです。 
It provides tools for creating workflows and state machines to coordinate multiple AI agents or language model interactions. 
ワークフローや状態遷移機を作成するためのツールを提供し、複数のAIエージェントや言語モデルの相互作用を調整します。 
LangGraph is built on top of LangChain, leveraging its components while adding graph-based coordination capabilities. 
LangGraphはLangChainの上に構築されており、そのコンポーネントを活用しながら、グラフベースの調整機能を追加しています。 
It's particularly useful for developing more complex, stateful AI applications that go beyond simple query-response interactions. 
これは、単純なクエリ応答の相互作用を超えた、より複雑で状態を持つAIアプリケーションの開発に特に役立ちます。 
Goodbye! 
さようなら！ 
```

Congratulations! You've built your first chatbot using LangGraph. This bot can engage in basic conversation by taking user input and generating responses using an LLM. You can inspect a LangSmith Trace for the call above at the provided link.
おめでとうございます！LangGraphを使用して最初のチャットボットを構築しました。このボットは、ユーザーの入力を受け取り、LLMを使用して応答を生成することで基本的な会話を行うことができます。上記の呼び出しに対してLangSmithトレースを検査できます。

However, you may have noticed that the bot's knowledge is limited to what's in its training data.
ただし、ボットの知識はトレーニングデータに含まれているものに限られていることに気付いたかもしれません。
In the next part, we'll add a web search tool to expand the bot's knowledge and make it more capable.
次の部分では、ボットの知識を拡張し、より能力を高めるためにウェブ検索ツールを追加します。

Below is the full code for this section for your reference:
以下は、このセクションの完全なコードです。

```
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# The first argument is the unique node name

# The second argument is the function or object that will be called whenever

# the node is used

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")
graph = graph_builder.compile()
```

<!-- ここまで読んだ! -->

## Part 2: 🛠️ Enhancing the Chatbot with Tools

To handle queries our chatbot can't answer "from memory", we'll integrate a web search tool.
私たちのチャットボットが「記憶」から答えられないクエリに対処するために、ウェブ検索ツールを統合します。

Our bot can use this tool to find relevant information and provide better responses.
私たちのボットは、このツールを使用して関連情報を見つけ、より良い応答を提供できます。

Before we start, make sure you have the necessary packages installed and API keys set up:
始める前に、必要なパッケージがインストールされ、APIキーが設定されていることを確認してください。

First, install the requirements to use the Tavily Search Engine, and set your TAVILY_API_KEY.
まず、Tavily Search Engineを使用するための要件をインストールし、TAVILY_API_KEYを設定します。

```
%%capture --no-stderr %pip install -U tavily-python langchain_community
```

```
_set_env("TAVILY_API_KEY")
```

```
TAVILY_API_KEY:  ········
```

```
from langchain_community.tools.tavily_search import TavilySearchResults
tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")
```

```
[{'url': 'https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141','content': 'Nodes: Nodes are the building blocks of your LangGraph. Each node represents a function or a computation step. You define nodes to perform specific tasks, such as processing input, making ...'},{'url': 'https://saksheepatil05.medium.com/demystifying-langgraph-a-beginner-friendly-dive-into-langgraph-concepts-5ffe890ddac0','content': 'Nodes (Tasks): Nodes are like the workstations on the assembly line. Each node performs a specific task on the product. In LangGraph, nodes are Python functions that take the current state, do some work, and return an updated state. Next, we define the nodes, each representing a task in our sandwich-making process.'}]
```

The results are page summaries our chat bot can use to answer questions.
結果は、私たちのチャットボットが質問に答えるために使用できる**ページの要約**です。

Next, we'll start defining our graph.
次に、グラフの定義を始めます。

The following is all the same as in Part 1, except we have added bind_tools on our LLM.
以下は、Part 1と同じですが、LLMにbind_toolsを追加しました。

This lets the LLM know the correct JSON format to use if it wants to use our search engine.
これにより、LLMは検索エンジンを使用したい場合に正しいJSON形式を知ることができます。

```
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# Modification: tell the LLM which tools it can call

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
```

Next we need to create a function to actually run the tools if they are called.
次に、**ツールが呼び出された場合に実際にツールを実行する関数**を作成する必要があります。
(chatbotとは別の、ツールを実行するノードを定義する感じ...!:thinking_face:)

We'll do this by adding the tools to a new node.
これを新しいノードにツールを追加することで行います。

Below, we implement a BasicToolNode that checks the most recent message in the state and calls tools if the message contains tool_calls.
以下に、**状態内の最新のメッセージをチェックし、メッセージに tool_calls が含まれている場合にツールを呼び出すBasicToolNodeを実装**します。

It relies on the LLM's tool_calling support, which is available in Anthropic, OpenAI, Google Gemini, and a number of other LLM providers.
これは、Anthropic、OpenAI、Google Gemini、および他の多くのLLMプロバイダーで利用可能な**LLMの tool_calling サポートに依存**しています。

We will later replace this with LangGraph's prebuilt ToolNode to speed things up, but building it ourselves first is instructive.
**後でこれをLangGraphのプリビルドToolNodeに置き換えて速度を上げます**が、最初に自分たちで構築することは教育的です。

```
import json
from langchain_core.messages import ToolMessage

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(ToolMessage(content=json.dumps(tool_result), name=tool_call["name"], tool_call_id=tool_call["id"],))
        
        return {"messages": outputs}

tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
```

With the tool node added, we can define the conditional_edges.
ツールノードが追加されたので、 conditional_edges を定義できます。

Recall that edges route the control flow from one node to the next.
**エッジは、1つのノードから次のノードへの制御フローをルーティングします**。(routing関数を定義する!)
Conditional edges usually contain "if" statements to route to different nodes depending on the current graph state.
**条件付きエッジは通常、「if」文を含み、現在のグラフ状態に応じて異なるノードにルーティング**します。
These functions receive the current graph state and return a string or list of strings indicating which node(s) to call next.
これらの関数は、**現在のグラフ状態を受け取り、次に呼び出すノードを示す文字列または文字列のリストを返します**。

Below, we define a router function called route_tools, that checks for tool_calls in the chatbot's output.
以下に、チャットボットの出力にtool_callsがあるかどうかをチェックする**route_toolsというルータ関数を定義**します。

Provide this function to the graph by calling add_conditional_edges, which tells the graph that whenever the chatbot node completes to check this function to see where to go next.
**この関数をadd_conditional_edgesを呼び出すことでグラフに提供**します。**これにより、チャットボットノードが完了するたびに、この関数をチェックして次にどこに行くかを確認**します。

The condition will route to tools if tool calls are present and END if not.
条件が存在する場合はツールにルーティングし、存在しない場合はENDにルーティングします。

Later, we will replace this with the prebuilt tools_condition to be more concise, but implementing it ourselves first makes things more clear.
後でこれをプリビルドのtools_conditionに置き換えてより簡潔にしますが、最初に自分たちで実装することでより明確になります。

```

from typing import Literal

def route_tools(state: State):
    """Use in the conditional_edge to route to the ToolNode if the last message has tool calls. Otherwise, route to the end."""

    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    
    return END

# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if it is fine directly responding

# This conditional routing defines the main agent loop

graph_builder.add_conditional_edges("chatbot", route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)

# Any time a tool is called, we return to the chatbot to decide the next step

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

Notice that conditional edges start from a single node.
**条件付きエッジは単一のノードから始まる**ことに注意してください。

This tells the graph "any time the 'chatbot' node runs, either go to 'tools' if it calls a tool, or end the loop if it responds directly.
**これは、グラフに「チャットボットノードが実行されるたびに、ツールを呼び出す場合は'tools'に行き、直接応答する場合はループを終了する」と伝えます**。

Like the prebuilt tools_condition, our function returns the END string if no tool calls are made.
プリビルドの tools_condition のように、私たちの関数は**ツール呼び出しが行われない場合にEND文字列を返します**。
When the graph transitions to END, it has no more tasks to complete and ceases execution.
**グラフがENDに遷移すると、完了すべきタスクがなくなり、実行を停止する**
Because the condition can return END, we don't need to explicitly set a finish_point this time.
条件がENDを返すことができるため、今回は明示的にfinish_pointを設定する必要はありません。
Our graph already has a way to finish!
私たちのグラフにはすでに終了する方法があります! (chatbotノードからENDノードへの条件付きエッジがすでに定義されているからね...!:thinking_face:)

Let's visualize the graph we've built.
私たちが構築したグラフを視覚化してみましょう。
The following function has some additional dependencies to run that are unimportant for this tutorial.
以下の関数には、このチュートリアルには重要でない追加の依存関係があります。

```
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

Now we can ask the bot questions outside its training data.
これで、ボットにトレーニングデータ外の質問をすることができます。

```

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

```

```
Assistant: [{'text': "To provide you with accurate and up-to-date information about LangGraph, I'll need to search for the latest details. Let me do that for you.", 'type': 'text'}, {'id': 'toolu_01Q588CszHaSvvP2MxRq9zRD', 'input': {'query': 'LangGraph AI tool information'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Assistant: [{"url": "https://www.langchain.com/langgraph", "content": "LangGraph sets the foundation for how we can build and scale AI workloads — from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. The next chapter in building complex production-ready features with LLMs is agentic, and with LangGraph and LangSmith, LangChain delivers an out-of-the-box solution ..."}, {"url": "https://github.com/langchain-ai/langgraph", "content": "Overview. LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Compared to other LLM frameworks, it offers these core benefits: cycles, controllability, and persistence. LangGraph allows you to define flows that involve cycles, essential for most agentic architectures ..."}]
Assistant: Based on the search results, I can provide you with information about LangGraph: 1. Purpose: LangGraph is a library designed for building stateful, multi-actor applications with Large Language Models (LLMs). It's particularly useful for creating agent and multi-agent workflows. 2. Developer: LangGraph is developed by LangChain, a company known for its tools and frameworks in the AI and LLM space. 3. Key Features: - Cycles: LangGraph allows the definition of flows that involve cycles, which is essential for most agentic architectures. - Controllability: It offers enhanced control over the application flow. - Persistence: The library provides ways to maintain state and persistence in LLM-based applications. 4. Use Cases: LangGraph can be used for various applications, including: - Conversational agents - Complex task automation - Custom LLM-backed experiences 5. Integration: LangGraph works in conjunction with LangSmith, another tool by LangChain, to provide an out-of-the-box solution for building complex, production-ready features with LLMs. 6. Significance: LangGraph is described as setting the foundation for building and scaling AI workloads. It's positioned as a key tool in the next chapter of LLM-based application development, particularly in the realm of agentic AI. 7. Availability: LangGraph is open-source and available on GitHub, which suggests that developers can access and contribute to its codebase. 8. Comparison to Other Frameworks: LangGraph is noted to offer unique benefits compared to other LLM frameworks, particularly in its ability to handle cycles, provide controllability, and maintain persistence. LangGraph appears to be a significant tool in the evolving landscape of LLM-based application development, offering developers new ways to create more complex, stateful, and interactive AI systems. Goodbye!
```

Our chatbot still can't remember past interactions on its own, limiting its ability to have coherent, multi-turn conversations.
私たちの**チャットボットはまだ過去のやり取りを自分で記憶することができず**、一貫したマルチターンの会話を持つ能力が制限されています。
In the next part, we'll add memory to address this.
次の部分では、**これに対処するためにメモリを追加**します。

The full code for the graph we've created in this section is reproduced below, replacing our BasicToolNode for the prebuilt ToolNode, and our route_tools condition with the prebuilt tools_condition.
このセクションで作成したグラフの完全なコードは以下に再現されており、**BasicToolNodeをプリビルドのToolNodeに置き換え、route_tools条件関数をプリビルドのtools_conditionに置き換えています**。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)

# Any time a tool is called, we return to the chatbot to decide the next step

graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()
```

<!-- ここまで読んだ! -->

## Part 3: Adding Memory to the Chatbot¶ チャットボットにメモリを追加する

Our chatbot can now use tools to answer user questions, but it doesn't remember the context of previous interactions.
私たちのチャットボットは、ユーザーの質問に答えるためにツールを使用できるようになりましたが、以前のやり取りのコンテキストを記憶していません。
This limits its ability to have coherent, multi-turn conversations.
これにより、一貫したマルチターンの会話を行う能力が制限されます。
LangGraph solves this problem through persistent checkpointing.
LangGraphは、**永続的なチェックポイント**を通じてこの問題を解決します。
If you provide a checkpointer when compiling the graph and a thread_id when calling your graph, LangGraph automatically saves the state after each step.
**グラフをコンパイルする際にチェックポインタを提供し、グラフを呼び出す際にthread_idを指定する**と、LangGraphは各ステップの後に自動的に状態を保存します。
When you invoke the graph again using the same thread_id, the graph loads its saved state, allowing the chatbot to pick up where it left off.
同じthread_idを使用してグラフを再度呼び出すと、**グラフは保存された状態を読み込み、チャットボットは前回の続きから再開できる**。
We will see later that checkpointing is much more powerful than simple chat memory - it lets you save and resume complex state at any time for error recovery, human-in-the-loop workflows, time travel interactions, and more.
後で見ていくと、**チェックポイントは単純なチャットメモリよりもはるかに強力であり、エラー回復や人間の介入が必要なワークフロー、タイムトラベルインタラクションなどのために、いつでも複雑な状態を保存して再開できる**ことがわかります。
But before we get too ahead of ourselves, let's add checkpointing to enable multi-turn conversations.
しかし、先に進む前に、マルチターンの会話を可能にするためにチェックポイントを追加しましょう。

To get started, create a MemorySaver checkpointer.
まず、MemorySaverチェックポインタを作成します。

```
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
```

Notice we're using an in-memory checkpointer.
**私たちはインメモリチェックポインタを使用している**ことに注意してください。
This is convenient for our tutorial (it saves it all in-memory).
これは私たちのチュートリアルにとって便利です（**すべてをメモリ内に保存**します）。
In a production application, you would likely change this to use SqliteSaver or PostgresSaver and connect to your own DB.
本番アプリケーションでは、これをSqliteSaverまたはPostgresSaverを使用して自分のデータベースに接続するように変更することが考えられます。

Next define the graph.
次に、グラフを定義します。
Now that you've already built your own BasicToolNode, we'll replace it with LangGraph's prebuilt ToolNode and tools_condition, since these do some nice things like parallel API execution.
すでに**独自のBasicToolNodeを構築しているので、これをLangGraphの事前構築されたToolNodeとtools_conditionに置き換えます。これにより、並列API実行などの便利な機能が提供**されます。(あ、やっぱりprebuildの関数の方がいいんだな:thinking_face:)
Apart from that, the following is all copied from Part 2.
それ以外は、以下の内容はすべてPart 2からコピーしたものです。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)

# Any time a tool is called, we return to the chatbot to decide the next step

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
```

Finally, compile the graph with the provided checkpointer.
最後に、提供されたチェックポインタを使用してグラフをコンパイルします。

```
graph = graph_builder.compile(checkpointer=memory)
```

Notice the connectivity of the graph hasn't changed since Part 2.
**グラフの接続性はPart 2から変わっていないことに注意**してください。
All we are doing is checkpointing the State as the graph works through each node.
私たちが行っているのは、**グラフが各ノードを通過する際にStateをチェックポイントすることだけ**です。(各ノードの処理がよばれるたびに、その時点のStateをそれぞれ保存しておくってことっぽい...!! 再利用やエラー時の再開に便利ってこと??:thinking_face:)

```python
from IPython.display import Image, display
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

Now you can interact with your bot!
これで、ボットと対話できるようになります！
First, pick a thread to use as the key for this conversation.
まず、この会話のキーとして使用するスレッドを選択します。

```

config = {"configurable": {"thread_id": "1"}}

```

Next, call your chat bot.
次に、チャットボットを呼び出します。

```python
user_input = "Hi there! My name is Will."

# The config is the **second positional argument** to stream() or invoke()

events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
for event in events:
    event["messages"][-1].pretty_print()
```

```shell
================================[1m Human Message [0m=================================
Hi there! My name is Will.
==================================[1m Ai Message [0m==================================
Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?
```

Let's ask a followup: see if it remembers your name.
次に、フォローアップを尋ねてみましょう：あなたの名前を覚えているかどうかを確認します。
(続けて上のコードの下に書く! メモリ上にcheckpointingしてるので、一回アプリケーションを落とすとメモリが解放されてしまう)

```

user_input = "Remember my name?"

# The config is the **second positional argument** to stream() or invoke()

events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
for event in events:
    event["messages"][-1].pretty_print()
```

```

================================[1m Human Message [0m=================================
Remember my name?
==================================[1m Ai Message [0m==================================
Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.

```

Don't believe me? Try this using a different config.
信じられないですか？異なる設定を使用してこれを試してみてください。
(指定するthread_idを変えると、元のthread_idのメモリは読み込まれないので、名前を覚えていない状態になる...!:thinking_face:)

```python
# The only difference is we change the `thread_id` here to "2" instead of "1"

events = graph.stream({"messages": [("user", user_input)]}, {"configurable": {"thread_id": "2"}}, stream_mode="values",)
for event in events:
    event["messages"][-1].pretty_print()
```

```
================================[1m Human Message [0m=================================
Remember my name?
==================================[1m Ai Message [0m==================================
I apologize, but I don't have any previous context or memory of your name. As an AI assistant, I don't retain information from past conversations. Each interaction starts fresh. Could you please tell me your name so I can address you properly in this conversation?
```

By now, we have made a few checkpoints across two different threads.
これまでに、2つの異なるスレッドにわたっていくつかのチェックポイントを作成しました。
But what goes into a checkpoint?
しかし、**チェックポイントには何が含まれるのでしょうか？**
To inspect a graph's state for a given config at any time, call get_state(config).
**特定の設定に対するグラフの状態をいつでも確認するには、get_state(config)を呼び出し**ます。

```python
snapshot = graph.get_state(config)
snapshot
```

```
StateSnapshot(values={'messages': [HumanMessage(content='Hi there! My name is Will.', additional_kwargs={}, response_metadata={}, id='8c1ca919-c553-4ebf-95d4-b59a2d61e078'), AIMessage(content="Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?", additional_kwargs={}, response_metadata={'id': 'msg_01WTQebPhNwmMrmmWojJ9KXJ', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 405, 'output_tokens': 32}}, id='run-58587b77-8c82-41e6-8a90-d62c444a261d-0', usage_metadata={'input_tokens': 405, 'output_tokens': 32, 'total_tokens': 437}), HumanMessage(content='Remember my name?', additional_kwargs={}, response_metadata={}, id='daba7df6-ad75-4d6b-8057-745881cea1ca'), AIMessage(content="Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.", additional_kwargs={}, response_metadata={'id': 'msg_01E41KitY74HpENRgXx94vag', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 444, 'output_tokens': 58}}, id='run-ffeaae5c-4d2d-4ddb-bd59-5d5cbf2a5af8-0', usage_metadata={'input_tokens': 444, 'output_tokens': 58, 'total_tokens': 502})]}, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d06e-93e0-6acc-8004-f2ac846575d2'}}, metadata={'source': 'loop', 'writes': {'chatbot': {'messages': [AIMessage(content="Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.", additional_kwargs={}, response_metadata={'id': 'msg_01E41KitY74HpENRgXx94vag', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 444, 'output_tokens': 58}}, id='run-ffeaae5c-4d2d-4ddb-bd59-5d5cbf2a5af8-0', usage_metadata={'input_tokens': 444, 'output_tokens': 58, 'total_tokens': 502})]}}, 'step': 4, 'parents': {}}, created_at='2024-09-27T19:30:10.820758+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d06e-859f-6206-8003-e1bd3c264b8f'}}, tasks=())

```

```python
snapshot.next
# (since the graph ended this turn, `next` is empty. If you fetch a state from within a graph invocation, next tells which node will execute next)
# (このターンでグラフが終了したため、`next`は空です。グラフの実行中に状態のsnapshotを取得すると、次に実行されるノードがわかります)
```

```
()
```

The snapshot above contains the current state values, corresponding config, and the next node to process.
上記の**スナップショットには、現在のstate values、対応する設定、および次に処理するノードが含まれ**ている。
In our case, the graph has reached an END state, so next is empty.
私たちのケースでは、グラフはEND状態に達しているため、nextは空です。

Congratulations!
おめでとうございます！
Your chatbot can now maintain conversation state across sessions thanks to LangGraph's checkpointing system.
あなたのチャットボットは、LangGraphのチェックポイントシステムのおかげで、**セッションをまたいで会話の状態を維持できるようになりました**。
This opens up exciting possibilities for more natural, contextual interactions.
これにより、より自然で文脈に沿ったインタラクションのためのエキサイティングな可能性が開かれます。
LangGraph's checkpointing even handles arbitrarily complex graph states, which is much more expressive and powerful than simple chat memory.
LangGraphのチェックポイントは、**単純なチャットメモリよりもはるかに表現力豊かで強力な、任意の複雑なグラフ状態を処理**できる。

In the next part, we'll introduce human oversight to our bot to handle situations where it may need guidance or verification before proceeding.
次のパートでは、ボットに人間の監視を導入し、進行する前にガイダンスや検証が必要な状況に対処します。
Check out the code snippet below to review our graph from this section.
以下のコードスニペットを確認して、このセクションのグラフを見直してください。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)
```

<!-- ここまで読んだ! -->

## Part 4: Human-in-the-loop

Agents can be unreliable and may need human input to successfully accomplish tasks.
**エージェントは信頼できない場合があり、タスクを成功裏に達成するために人間の入力が必要な場合がある**。
Similarly, for some actions, you may want to require human approval before running to ensure that everything is running as intended.
同様に、**いくつかのアクションについては、すべてが意図した通りに実行されていることを確認するために、実行前に人間の承認を必要とする場合がある**。
LangGraph supports human-in-the-loop workflows in a number of ways.
LangGraphは、さまざまな方法で人間が介在するワークフローをサポートしています。

In this section, we will use LangGraph's interrupt_before functionality to always break the tool node.
このセクションでは、LangGraphの`interrupt_before`機能を使用して、常にツールノードを中断します。

First, start from our existing code.
まず、既存のコードから始めます。

The following is copied from Part 3.
以下は、パート3からコピーしたものです。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

memory = MemorySaver()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

```

Now, compile the graph, specifying to interrupt_before the tools node.
次に、グラフをコンパイルし、**ツールノードの前で中断するように**指定します。

```python
graph = graph_builder.compile(
    checkpointer=memory,  # This is new!
    interrupt_before=["tools"],  # Note: can also interrupt **after** tools, if desired.
    # interrupt_after=["tools"]
)
```

```python
user_input = "I'm learning LangGraph. Could you do some research on it for me?"
config = {"configurable": {"thread_id": "1"}}  # The config is the **second positional argument** to stream() or invoke()!
events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```

================================[1m Human Message [0m=================================
I'm learning LangGraph. Could you do some research on it for me?
==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and comprehensive information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01R4ZFcb5hohpiVZwr88Bxhc', 'input': {'query': 'LangGraph framework for building language model applications'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]

```

```

Tool Calls:
tavily_search_results_json (toolu_01R4ZFcb5hohpiVZwr88Bxhc)
Call ID: toolu_01R4ZFcb5hohpiVZwr88Bxhc
Args: query: LangGraph framework for building language model applications

```

```python
snapshot = graph.get_state(config)
snapshot.next
```

```
('tools',)
```

Notice that unlike last time, the "next" node is set to 'tools'.
前回とは異なり、「次」のノードが'tools'に設定されていることに注意してください。

We've interrupted here! Let's check the tool invocation.
ここで中断しました！ツールの呼び出しを確認しましょう。

```
existing_message = snapshot.values["messages"][-1]
existing_message.tool_calls
```

```
[{'name': 'tavily_search_results_json', 'args': {'query': 'LangGraph framework for building language model applications'}, 'id': 'toolu_01R4ZFcb5hohpiVZwr88Bxhc', 'type': 'tool_call'}]

```

This query seems reasonable.
このクエリは妥当なようです。

Nothing to filter here.
ここでフィルタリングする必要はありません。

The simplest thing the human can do is just let the graph continue executing.
**人間ができる最も簡単なことは、グラフの実行を続けさせること**です。

Let's do that below.
以下でそれを行いましょう。

Next, continue the graph!
次に、グラフを続行します！

Passing in None will just let the graph continue where it left off, without adding anything new to the state.
**Noneを渡すことで、グラフは新しい状態を追加することなく、元の位置から続行します**。

```

# `None` will append nothing new to the current state, letting it resume as if it had never been interrupted

events = graph.stream(None, config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

```

```

==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and comprehensive information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01R4ZFcb5hohpiVZwr88Bxhc', 'input': {'query': 'LangGraph framework for building language model applications'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]

```

```

Tool Calls:
tavily_search_results_json (toolu_01R4ZFcb5hohpiVZwr88Bxhc)
Call ID: toolu_01R4ZFcb5hohpiVZwr88Bxhc
Args: query: LangGraph framework for building language model applications

```

```
=================================[1m Tool Message [0m=================================
Name: tavily_search_results_json
[{"url": "https://towardsdatascience.com/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787", "content": "LangChain is one of the leading frameworks for building applications powered by Large Language Models. With the LangChain Expression Language (LCEL), defining and executing step-by-step action sequences — also known as chains — becomes much simpler. In more technical terms, LangChain allows us to create DAGs (directed acyclic graphs). As LLM applications, particularly LLM agents, have ..."}, {"url": "https://github.com/langchain-ai/langgraph", "content": "Overview. LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Compared to other LLM frameworks, it offers these core benefits: cycles, controllability, and persistence. LangGraph allows you to define flows that involve cycles, essential for most agentic architectures ..."}]
```

Congrats! You've used an interrupt to add human-in-the-loop execution to your chatbot, allowing for human oversight and intervention when needed.
おめでとうございます！あなたは**interruptを使用して、チャットボットに人間が介在する実行を追加し、必要に応じて人間の監視と介入を可能にした**。

This opens up the potential UIs you can create with your AI systems.
これにより、AIシステムで作成できる潜在的なUIが広がります。

Since we have already added a checkpointer, the graph can be paused indefinitely and resumed at any time as if nothing had happened.
**すでにチェックポインターを追加しているため、グラフは無期限に一時停止でき、何も起こらなかったかのようにいつでも再開できます**。

Next, we'll explore how to further customize the bot's behavior using custom state updates.
次に、カスタム状態更新を使用してボットの動作をさらにカスタマイズする方法を探ります。

Below is a copy of the code you used in this section.
以下は、このセクションで使用したコードのコピーです。

The only difference between this and the previous parts is the addition of the interrupt_before argument.
これと前の部分との唯一の違いは、interrupt_before引数の追加です。

```

from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,  # This is new!
    interrupt_before=["tools"],  # Note: can also interrupt **after** actions, if desired.
    # interrupt_after=["tools"]
)

```

<!-- ここまで読んだ! -->

## Part 5: Manually Updating the State¶

## 第5部: 状態の手動更新

In the previous section, we showed how to interrupt a graph so that a human could inspect its actions.
前のセクションでは、グラフを中断して人間がその動作を検査できる方法を示しました。

This lets the human read the state, but if they want to change their agent's course, they'll need to have write access.
これにより、人間は状態を読み取ることができますが、**エージェントの進路を変更したい場合は、書き込みアクセスが必要**です。

Thankfully, LangGraph lets you manually update state!
幸いなことに、**LangGraphでは状態を手動で更新できます**！

Updating the state lets you control the agent's trajectory by modifying its actions (even modifying the past!).
状態を更新することで、エージェントの軌道を制御し、その行動を修正することができます（過去を修正することさえ可能です！）。

This capability is particularly useful when you want to correct the agent's mistakes, explore alternative paths, or guide the agent towards a specific goal.
この機能は、**エージェントの誤りを修正したり、代替の道を探ったり、特定の目標に向かってエージェントを導いたりする際に特に便利**です。

We'll show how to update a checkpointed state below.
以下に、チェックポイント状態を更新する方法を示します。

As before, first, define your graph.
前と同様に、まずグラフを定義します。

We'll reuse the exact same graph as before.
前と全く同じグラフを再利用します。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition,)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory,  # This is new!
                               interrupt_before=["tools"],  # Note: can also interrupt **after** actions, if desired.
                               # interrupt_after=["tools"])
user_input = "I'm learning LangGraph. Could you do some research on it for me?"
config = {"configurable": {"thread_id": "1"}}  # The config is the **second positional argument** to stream() or invoke()!
events = graph.stream({"messages": [("user", user_input)]}, config)

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```python
snapshot = graph.get_state(config)
existing_message = snapshot.values["messages"][-1]
existing_message.pretty_print()

```

```

==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and comprehensive information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_018YcbFR37CG8RRXnavH5fxZ', 'input': {'query': 'LangGraph: what is it, how is it used in AI development'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_018YcbFR37CG8RRXnavH5fxZ)
Call ID: toolu_018YcbFR37CG8RRXnavH5fxZ
Args: query: LangGraph: what is it, how is it used in AI development

```

But what if the user wants to intercede?
しかし、ユーザーが介入したい場合はどうでしょうか？

What if we think the chat bot doesn't need to use the tool?
チャットボットがツールを使用する必要がないと考えた場合はどうでしょうか？

Let's directly provide the correct response!
正しい応答を直接提供しましょう！

```python
from langchain_core.messages import AIMessage, ToolMessage

answer = ("LangGraph is a library for building stateful, multi-actor applications with LLMs.")
new_messages = [
    # The LLM API expects some ToolMessage to match its tool call. We'll satisfy that here.
    ToolMessage(content=answer, tool_call_id=existing_message.tool_calls[0]["id"]),
    # And then directly "put words in the LLM's mouth" by populating its response.
    AIMessage(content=answer),
]

new_messages[-1].pretty_print()
graph.update_state(
    # Which state to update
    config,
    # The updated values to provide. The messages in our `State` are "append-only", meaning this will be appended
    # to the existing state. We will review how to update existing messages in the next section!
    {"messages": new_messages},
)

print("\n\nLast 2 messages;")
print(graph.get_state(config).values["messages"][-2:])

```

```

==================================[1m Ai Message [0m==================================
LangGraph is a library for building stateful, multi-actor applications with LLMs.
Last 2 messages;
[ToolMessage(content='LangGraph is a library for building stateful, multi-actor applications with LLMs.', id='675f7618-367f-44b7-b80e-2834afb02ac5', tool_call_id='toolu_018YcbFR37CG8RRXnavH5fxZ'), AIMessage(content='LangGraph is a library for building stateful, multi-actor applications with LLMs.', additional_kwargs={}, response_metadata={}, id='35fd5682-0c2a-4200-b192-71c59ac6d412')]

```

Now the graph is complete, since we've provided the final response message!
これでグラフは完成しました。最終的な応答メッセージを提供したからです！

Since state updates simulate a graph step, they even generate corresponding traces.
状態の更新はグラフのステップをシミュレートするため、対応するトレースも生成されます。

Inspect the LangSmith trace of the update_state call above to see what's going on.
上記のupdate_state呼び出しのLangSmithトレースを確認して、何が起こっているかを見てみましょう。

Notice that our new messages are appended to the messages already in the state.
新しいメッセージがすでに状態にあるメッセージに追加されていることに注意してください。

Remember how we defined the State type?
State型をどのように定義したかを思い出してください。

```

class State(TypedDict):
    messages: Annotated[list, add_messages]

```

We annotated messages with the pre-built add_messages function.
私たちは、**pre-builtのadd_messages関数でmessagesを注釈しました**。
This instructs the graph to always append values to the existing list, rather than overwriting the list directly.
**これにより、グラフはリストを直接上書きするのではなく、常に既存のリストに値を追加するように指示**します。

The same logic is applied here, so the messages we passed to update_state were appended in the same way!
ここでも同じ論理が適用されるため、update_stateに渡したメッセージは同じように追加されました！

The update_state function operates as if it were one of the nodes in your graph!
**update_state関数は、グラフ内のノードの1つであるかのように動作します**！

By default, the update operation uses the node that was last executed, but you can manually specify it below.
デフォルトでは、更新操作は最後に実行されたノードを使用しますが、以下で手動で指定することもできます。

Let's add an update and tell the graph to treat it as if it came from the "chatbot".
更新を追加し、グラフに「チャットボット」からのものであるかのように扱うように指示しましょう。

```

graph.update_state(config, {"messages": [AIMessage(content="I'm an AI expert!")]},  # Which node for this function to act as. It will automatically continue
                      # processing as if this node just ran.
                      as_node="chatbot",
)

```

```

{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d134-3958-6412-8002-3f4b4112062f'}}

```

Check out the LangSmith trace for this update call at the provided link.
提供されたリンクでこの更新呼び出しのLangSmithトレースを確認してください。

Notice from the trace that the graph continues into the tools_condition edge.
トレースから、グラフがtools_conditionエッジに続いていることに注意してください。

We just told the graph to treat the update as_node="chatbot".
私たちは、**グラフに更新をas_node="chatbot"として扱うように**指示しました。

If we follow the diagram below and start from the chatbot node, we naturally end up in the tools_condition edge and then **end** since our updated message lacks tool calls.
以下の図に従い、チャットボットノードから始めると、自然にtools_conditionエッジに到達し、その後__end__に至ります。更新されたメッセージにはツール呼び出しがないためです。

```

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:  # This requires some extra dependencies and is optional
    pass

```

Inspect the current state as before to confirm the checkpoint reflects our manual updates.
以前と同様に現在の状態を確認して、チェックポイントが手動更新を反映していることを確認してください。

```

snapshot = graph.get_state(config)
print(snapshot.values["messages"][-3:])
print(snapshot.next)

```

```

[ToolMessage(content='LangGraph is a library for building stateful, multi-actor applications with LLMs.', id='675f7618-367f-44b7-b80e-2834afb02ac5', tool_call_id='toolu_018YcbFR37CG8RRXnavH5fxZ'), AIMessage(content='LangGraph is a library for building stateful, multi-actor applications with LLMs.', additional_kwargs={}, response_metadata={}, id='35fd5682-0c2a-4200-b192-71c59ac6d412'), AIMessage(content="I'm an AI expert!", additional_kwargs={}, response_metadata={}, id='288e2f74-f1cb-4082-8c3c-af4695c83117')]()

```

The add_messages function we used to annotate our graph's State above controls how updates are made to the messages key.
上記で**グラフのStateを注釈するために使用したadd_messages関数は、messagesキーへの更新がどのように行われるかを制御**します。

This function looks at any message IDs in the new_messages list.
この関数は、新しいmessagesリスト内のメッセージIDを確認します。

If the ID matches a message in the existing state, add_messages overwrites the existing message with the new content.
**IDが既存の状態のメッセージと一致する場合、add_messagesは既存のメッセージを新しいコンテンツで上書き**します。

As an example, let's update the tool invocation to make sure we get good results from our search engine!
例として、ツールの呼び出しを更新して、検索エンジンから良い結果を得られるようにしましょう！

First, start a new thread:
まず、新しいスレッドを開始します。

```python
user_input = "I'm learning LangGraph. Could you do some research on it for me?"
config = {"configurable": {"thread_id": "2"}}  # we'll use thread_id = 2 here
events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

```

```

================================[1m Human Message [0m=================================
I'm learning LangGraph. Could you do some research on it for me?
==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and accurate information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01TfAeisrpx4ddgJpoAxqrVh', 'input': {'query': 'LangGraph framework for language models'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_01TfAeisrpx4ddgJpoAxqrVh)
Call ID: toolu_01TfAeisrpx4ddgJpoAxqrVh
Args: query: LangGraph framework for language models

```

```python
from langchain_core.messages import AIMessage

snapshot = graph.get_state(config)
existing_message = snapshot.values["messages"][-1]
print("Original")
print("Message ID", existing_message.id)
print(existing_message.tool_calls[0])

new_tool_call = existing_message.tool_calls[0].copy()
new_tool_call["args"]["query"] = "LangGraph human-in-the-loop workflow"

new_message = AIMessage(content=existing_message.content, tool_calls=[new_tool_call],  # Important! The ID is how LangGraph knows to REPLACE the message in the state rather than APPEND this message
                        id=existing_message.id,)

print("Updated")
print(new_message.tool_calls[0])
print("Message ID", new_message.id)

graph.update_state(config, {"messages": [new_message]})
print("\n\nTool calls")
graph.get_state(config).values["messages"][-1].tool_calls
```

```
Original
Message ID run-342f3f54-356b-4cc1-b747-573f6aa31054-0
{'name': 'tavily_search_results_json', 'args': {'query': 'LangGraph framework for language models'}, 'id': 'toolu_01TfAeisrpx4ddgJpoAxqrVh', 'type': 'tool_call'}
Updated
{'name': 'tavily_search_results_json', 'args': {'query': 'LangGraph human-in-the-loop workflow'}, 'id': 'toolu_01TfAeisrpx4ddgJpoAxqrVh', 'type': 'tool_call'}
Message ID run-342f3f54-356b-4cc1-b747-573f6aa31054-0
Tool calls

```

```

[{'name': 'tavily_search_results_json', 'args': {'query': 'LangGraph human-in-the-loop workflow'}, 'id': 'toolu_01TfAeisrpx4ddgJpoAxqrVh', 'type': 'tool_call'}]

```

Notice that we've modified the AI's tool invocation to search for "LangGraph human-in-the-loop workflow" instead of the simple "LangGraph".
AIのツール呼び出しを単純な「LangGraph」ではなく「LangGraph human-in-the-loop workflow」を検索するように変更したことに注目してください。

Check out the LangSmith trace to see the state update call - you can see our new message has successfully updated the previous AI message.
状態更新呼び出しを確認するためにLangSmithトレースをチェックしてください。新しいメッセージが以前のAIメッセージを正常に更新したことがわかります。

Resume the graph by streaming with an input of None and the existing config.
Noneの入力と既存の設定でストリーミングしてグラフを再開します。

```

events = graph.stream(None, config, stream_mode="values")

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

```

```shell
==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and accurate information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01TfAeisrpx4ddgJpoAxqrVh', 'input': {'query': 'LangGraph framework for language models'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_01TfAeisrpx4ddgJpoAxqrVh)
Call ID: toolu_01TfAeisrpx4ddgJpoAxqrVh
Args: query: LangGraph human-in-the-loop workflow
==================================[1m Tool Message [0m=================================
Name: tavily_search_results_json
[{"url": "https://www.youtube.com/watch?v=9BPCV5TYPmg", "content": "In this video, I'll show you how to handle persistence with LangGraph, enabling a unique Human-in-the-Loop workflow. This approach allows a human to grant an..."}, {"url": "https://medium.com/@kbdhunga/implementing-human-in-the-loop-with-langgraph-ccfde023385c", "content": "Implementing a Human-in-the-Loop (HIL) framework in LangGraph with the Streamlit app provides a robust mechanism for user engagement and decision-making. By incorporating breakpoints and ..."}]
==================================[1m Ai Message [0m==================================
Thank you for your patience. I've found some information about LangGraph, particularly focusing on its human-in-the-loop workflow capabilities. Let me summarize what I've learned for you:

1. LangGraph Overview: LangGraph is a framework for building stateful, multi-actor applications with Large Language Models (LLMs). It's particularly useful for creating complex, interactive AI systems.
2. Human-in-the-Loop (HIL) Workflow: One of the key features of LangGraph is its support for human-in-the-loop workflows. This means that it allows for human intervention and decision-making within AI-driven processes.
3. Persistence Handling: LangGraph offers capabilities for handling persistence, which is crucial for maintaining state across interactions in a workflow.
4. Implementation with Streamlit: There are examples of implementing LangGraph's human-in-the-loop functionality using Streamlit, a popular Python library for creating web apps. This combination allows for the creation of interactive user interfaces for AI applications.
5. Breakpoints and User Engagement: LangGraph allows the incorporation of breakpoints in the workflow. These breakpoints are points where the system can pause and wait for human input or decision-making, enhancing user engagement and control over the AI process.
6. Decision-Making Mechanism: The human-in-the-loop framework in LangGraph provides a robust mechanism for integrating user decision-making into AI workflows. This is particularly useful in scenarios where human judgment or expertise is needed to guide or validate AI actions.
7. Flexibility and Customization: From the information available, it seems that LangGraph offers flexibility in how human-in-the-loop processes are implemented, allowing developers to customize the interaction points and the nature of human involvement based on their specific use case.

LangGraph appears to be a powerful tool for developers looking to create more interactive and controllable AI applications, especially those that benefit from human oversight or input at crucial stages of the process.
LangGraphは、特にプロセスの重要な段階で人間の監視や入力が有益なAIアプリケーションをよりインタラクティブで制御可能にするために、開発者にとって強力なツールのようです。

Would you like me to research any specific aspect of LangGraph in more detail, or do you have any questions about what I've found so far?
LangGraphの特定の側面についてさらに詳しく調査してほしいですか、それとも私がこれまでに見つけたことについて質問がありますか？
```

All of this is reflected in the graph's checkpointed memory, meaning if we continue the conversation, it will recall all the modified state.
これらすべてはグラフのチェックポイントメモリに反映されており、会話を続けると、すべての変更された状態を記憶します。

```python
events = graph.stream({"messages": ("user", "Remember what I'm learning about?",)}, config, stream_mode="values",)

for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================[1m Human Message [0m=================================
Remember what I'm learning about?
==================================[1m Ai Message [0m==================================
I apologize for my oversight. You're absolutely right to remind me. You mentioned that you're learning LangGraph. Thank you for bringing that back into focus.
Since you're in the process of learning LangGraph, it would be helpful to know more about your current level of understanding and what specific aspects of LangGraph you're most interested in or finding challenging.
This way, I can provide more targeted information or explanations that align with your learning journey.
Are there any particular areas of LangGraph you'd like to explore further?
For example:

1. Basic concepts and architecture of LangGraph
2. Setting up and getting started with LangGraph
3. Implementing specific features like the human-in-the-loop workflow
4. Best practices for using LangGraph in projects
5. Comparisons with other similar frameworks
Or if you have any specific questions about what you've learned so far, I'd be happy to help clarify or expand on those topics.
Please let me know what would be most useful for your learning process.
```

The graph code for this section is identical to previous ones.
このセクションのグラフコードは、以前のものと同じです。

The key snippets to remember are to add .compile(..., interrupt_before=[...]) (or interrupt_after) if you want to explicitly pause the graph whenever it reaches a node.
**ノードに到達するたびにグラフを明示的に一時停止したい場合**は、.compile(..., interrupt_before=[...])（またはinterrupt_after）を追加することを忘れないでください。

Then you can use update_state to modify the checkpoint and control how the graph should proceed.
その後、update_stateを使用してチェックポイントを変更し、グラフがどのように進行するかを制御できます。

<!-- ここまで読んだ! -->

## Part 6: Customizing State¶ 状態のカスタマイズ

So far, we've relied on a simple state (it's just a list of messages!).
これまで、私たちは**シンプルな状態（メッセージのリストだけ）**に依存してきました。
You can go far with this simple state, but if you want to define complex behavior without relying on the message list, you can add additional fields to the state.
**このシンプルな状態で多くのことを達成できますが、メッセージリストに依存せずに複雑な動作を定義したい場合は、状態に追加のフィールドを追加できます**。
In this section, we will extend our chat bot with a new node to illustrate this.
このセクションでは、これを示すために新しいノードを使ってチャットボットを拡張します。

In the examples above, we involved a human deterministically: the graph always interrupted whenever a tool was invoked.
上記の例では、私たちは人間を決定論的に関与させました：ツールが呼び出されるたびにグラフは常に中断されました。
Suppose we wanted our chat bot to have the choice of relying on a human.
**チャットボットが人間に依存する選択肢を持つ**ようにしたいとしましょう。

One way to do this is to create a passthrough "human" node, before which the graph will always stop.
これを行う一つの方法は、**グラフが常に停止するpassthroughとして「人間」ノードを作成すること**です。
We will only execute this node if the LLM invokes a "human" tool.
このノードは、LLMが「人間」ツールを呼び出した場合にのみ実行します。
For our convenience, we will include an "ask_human" flag in our graph state that we will flip if the LLM calls this tool.
私たちの便宜のために、**LLMがこのツールを呼び出した場合に切り替える「ask_human」フラグをグラフ状態に含める**。

<!-- ここまで読んだ! -->

Below, define this new graph, with an updated State
以下に、更新された状態を持つ新しいグラフを定義します。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]  
    # This flag is new
    ask_human: bool
```

Next, define a schema to show the model to let it decide to request assistance.
次に、モデルに支援を要求するかどうかを決定させるためのスキーマを定義します。
Using Pydantic with LangChain
LangChainと共にPydanticを使用します。
This notebook uses Pydantic v2 BaseModel, which requires langchain-core >= 0.3.
このノートブックは、langchain-core >= 0.3を必要とするPydantic v2 BaseModelを使用します。
Using langchain-core < 0.3 will result in errors due to mixing of Pydantic v1 and v2 BaseModels.
langchain-core < 0.3を使用すると、Pydantic v1とv2 BaseModelsの混在によりエラーが発生します。

```python
from pydantic import BaseModel

class RequestAssistance(BaseModel):
    """
    会話を専門家にエスカレーションします。
    直接支援できない場合や、ユーザーがあなたの権限を超えた支援を必要とする場合に使用します。
    この機能を使用するには、ユーザを中継して、専門家が適切なガイダンスを提供できるようにします。
    """
    request: str
```

Next, define the chatbot node.
次に、チャットボットノードを定義します。
The primary modification here is flip the ask_human flag if we see that the chat bot has invoked the RequestAssistance flag.
ここでの主な変更は、**チャットボットがRequestAssistanceフラグを呼び出した場合にask_humanフラグを切り替えること**です。

```python
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
# We can bind the llm to a tool definition, a pydantic model, or a json schema
# 私たちはllmをツール定義、pydanticモデル、またはjsonスキーマにバインドすることができます。
llm_with_tools = llm.bind_tools(tools + [RequestAssistance])

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if (response.tool_calls and response.tool_calls[0]["name"] == RequestAssistance.__name__):
        ask_human = True
    return {
        "messages": [response],
        "ask_human": ask_human
    }
```

Next, create the graph builder and add the chatbot and tools nodes to the graph, same as before.
次に、グラフビルダーを作成し、チャットボットとツールノードをグラフに追加します。以前と同様です。

```

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=[tool]))

```

Next, create the "human" node.
次に、「人間」ノードを作成します。
This node function is mostly a placeholder in our graph that will trigger an interrupt.
このノード関数は、主に中断をトリガーするためのプレースホルダーです。
If the human does not manually update the state during the interrupt, it inserts a tool message so the LLM knows the user was requested but didn't respond.
人間が中断中に手動で状態を更新しない場合、ツールメッセージを挿入して、LLMがユーザーが要求されたが応答しなかったことを知ることができます。
This node also unsets the ask_human flag so the graph knows not to revisit the node unless further requests are made.
このノードはまた、ask_humanフラグを解除し、さらなるリクエストがない限りノードを再訪しないことをグラフに知らせます。

```python
from langchain_core.messages import AIMessage, ToolMessage

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(content=response, tool_call_id=ai_message.tool_calls[0]["id"],)

def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # 通常、ユーザーは中断中に状態を更新しているでしょう。
        # If they choose not to, we will include a placeholder ToolMessage to let the LLM continue.
        # もし更新しないことを選択した場合、LLMが続行できるようにプレースホルダーのToolMessageを含めます。
        new_messages.append(create_response("No response from human.", state["messages"][-1]))
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }

graph_builder.add_node("human", human_node)
```

Next, define the conditional logic.
次に、条件ロジックを定義します。
The select_next_node will route to the human node if the flag is set.
`select_next_node` は、フラグが設定されている場合にhumanノードにルーティングします。
Otherwise, it lets the prebuilt tools_condition function choose the next node.
そうでなければ、prebuilt tools_condition関数が次のノードを選択します。
Recall that the tools_condition function simply checks to see if the chatbot has responded with any tool_calls in its response message.
tools_condition関数は、チャットボットが応答メッセージにツールコールを含めて応答したかどうかを確認します。
If so, it routes to the action node.
そうであれば、アクションノードにルーティングします。
Otherwise, it ends the graph.
そうでなければ、グラフは終了します。

```python
def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    # Otherwise, we can route as before
    return tools_condition(state)

graph_builder.add_conditional_edges("chatbot", select_next_node, {"human": "human", "tools": "tools", END: END},)
```

Finally, add the simple directed edges and compile the graph.
最後に、シンプルな有向エッジを追加し、グラフをコンパイルします。
These edges instruct the graph to always flow from node a -> b whenever a finishes executing.
これらのエッジは、ノードaが実行を終了するたびに常にノードaからノードbに流れるようにグラフに指示します。

```python

# The rest is the same

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory,
    # We interrupt before 'human' here instead.
    interrupt_before=["human"],
)

```

If you have the visualization dependencies installed, you can see the graph structure below:
視覚化依存関係がインストールされている場合、以下にグラフ構造を表示できます。

```python
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```

The chat bot can either request help from a human (chatbot->select->human), invoke the search engine tool (chatbot->select->action), or directly respond (chatbot->select->end).
チャットボットは、人間からの支援を要求することも（chatbot->select->human）、検索エンジンツールを呼び出すことも（chatbot->select->action）、直接応答することもできます（chatbot->select->end）。
Once an action or request has been made, the graph will transition back to the chatbot node to continue operations.
アクションまたはリクエストが行われると、グラフはチャットボットノードに戻り、操作を続行します。
Let's see this graph in action.
このグラフを実際に見てみましょう。
We will request for expert assistance to illustrate our graph.
グラフを示すために専門家の支援を要求します。

```python
user_input = "I need some expert guidance for building this AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}

# The config is the **second positional argument** to stream() or invoke()

events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```shell
================================[1m Human Message [0m=================================
I need some expert guidance for building this AI agent. Could you request assistance for me?
==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I understand that you need expert guidance for building an AI agent. I'll use the RequestAssistance function to escalate your request to an expert who can provide you with the specialized knowledge and support you need. Let me do that for you right away.", 'type': 'text'}, {'id': 'toolu_01Mo3N2c1byuSZwT1vyJWRia', 'input': {'request': 'The user needs expert guidance for building an AI agent. They require specialized knowledge and support in AI development and implementation.'}, 'name': 'RequestAssistance', 'type': 'tool_use'}]
Tool Calls: RequestAssistance (toolu_01Mo3N2c1byuSZwT1vyJWRia)
Call ID: toolu_01Mo3N2c1byuSZwT1vyJWRia
Args: request: The user needs expert guidance for building an AI agent. They require specialized knowledge and support in AI development and implementation.
```

```python
snapshot = graph.get_state(config)
snapshot.next
```

```

('human',)

```

The graph state is indeed interrupted before the 'human' node.
グラフ状態は確かに「人間」ノードの前で中断されています。
We can act as the "expert" in this scenario and manually update the state by adding a new ToolMessage with our input.
このシナリオでは「専門家」として行動し、私たちの入力を含む新しいToolMessageを追加することで状態を手動で更新できます。
Next, respond to the chatbot's request by:
次に、チャットボットのリクエストに応じて：

1. Creating a ToolMessage with our response.
1. 私たちの応答を含むToolMessageを作成します。
2. Calling update_state to manually update the graph state.
2. update_stateを呼び出して、グラフ状態を手動で更新します。

```

ai_message = snapshot.values["messages"][-1]
human_response = ("We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. "
                  "It's much more reliable and extensible than simple autonomous agents.")
tool_message = create_response(human_response, ai_message)
graph.update_state(config, {"messages": [tool_message]})

```

```

{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d092-bb30-6bee-8002-015e7e1c56c0'}}

```

You can inspect the state to confirm our response was added.
状態を確認して、私たちの応答が追加されたことを確認できます。

```

graph.get_state(config).values["messages"]

```

```

[HumanMessage(content='I need some expert guidance for building this AI agent. Could you request assistance for me?', additional_kwargs={}, response_metadata={}, id='3f28f959-9ab7-489a-9c58-7ed1b49cedf3'),
 AIMessage(content=[{'text': "Certainly! I understand that you need expert guidance for building an AI agent. I'll use the RequestAssistance function to escalate your request to an expert who can provide you with the specialized knowledge and support you need. Let me do that for you right away.", 'type': 'text'}, {'id': 'toolu_01Mo3N2c1byuSZwT1vyJWRia', 'input': {'request': 'The user needs expert guidance for building an AI agent. They require specialized knowledge and support in AI development and implementation.'}, 'name': 'RequestAssistance', 'type': 'tool_use'}], additional_kwargs={}, response_metadata={'id': 'msg_01VRnZvVbgsVRbQaQuvsziDx', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'tool_use', 'stop_sequence': None, 'usage': {'input_tokens': 516, 'output_tokens': 130}}, id='run-4e3f7906-5887-40d9-9267-5beefe7b3b76-0', tool_calls=[{'name': 'RequestAssistance', 'args': {'request': 'The user needs expert guidance for building an AI agent. They require specialized knowledge and support in AI development and implementation.'}, 'id': 'toolu_01Mo3N2c1byuSZwT1vyJWRia', 'type': 'tool_call'}], usage_metadata={'input_tokens': 516, 'output_tokens': 130, 'total_tokens': 646}),
 ToolMessage(content="We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.", id='8583b899-d898-4051-9f36-f5e5d11e9a37', tool_call_id='toolu_01Mo3N2c1byuSZwT1vyJWRia')]

```

Next, resume the graph by invoking it with None as the inputs.
次に、Noneを入力として呼び出すことでグラフを再開します。

```

events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

```

```

=================================[1m Tool Message [0m=================================
We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.
=================================[1m Tool Message [0m=================================
We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.
==================================[1m Ai Message [0m==================================
Thank you for your patience. I've escalated your request to our expert team, and they have provided some initial guidance. Here's what they suggest:
The experts recommend that you check out LangGraph for building your AI agent. They mention that LangGraph is a more reliable and extensible option compared to simple autonomous agents.
LangGraph is likely a framework or tool designed specifically for creating complex AI agents. It seems to offer advantages in terms of reliability and extensibility, which are crucial factors when developing sophisticated AI systems.
To further assist you, I can provide some additional context and next steps:

1. Research LangGraph: Look up documentation, tutorials, and examples of LangGraph to understand its features and how it can help you build your AI agent.
2. Compare with other options: While the experts recommend LangGraph, it might be useful to understand how it compares to other AI agent development frameworks or tools you might have been considering.
3. Assess your requirements: Consider your specific needs for the AI agent you want to build. Think about the tasks it needs to perform, the level of complexity required, and how LangGraph's features align with these requirements.
4. Start with a small project: If you decide to use LangGraph, consider beginning with a small, manageable project to familiarize yourself with the framework.
5. Seek community support: Look for LangGraph user communities, forums, or discussion groups where you can ask questions and get additional support as you build your agent.
6. Consider additional training: Depending on your current skill level, you might want to look into courses or workshops that focus on AI agent development, particularly those that cover LangGraph.
Do you have any specific questions about LangGraph or AI agent development that you'd like me to try to answer? Or would you like me to search for more detailed information about LangGraph and its features?

```

Congratulations!
おめでとうございます！
You've now added an additional node to your assistant graph to let the chat bot decide for itself whether or not it needs to interrupt execution.
これで、**チャットボットが実行を中断する必要があるかどうかを自分で決定できるように、アシスタントグラフに追加のノードを追加**しました。
You did so by updating the graph State with a new ask_human field and modifying the interruption logic when compiling the graph.
グラフ状態を新しいask_humanフィールドで更新し、グラフをコンパイルする際に中断ロジックを修正することで実現しました。
This lets you dynamically include a human in the loop while maintaining full memory every time you execute the graph.
これにより、グラフを実行するたびに完全なメモリを維持しながら、動的に人間をループに含めることができます。
We're almost done with the tutorial, but there is one more concept we'd like to review before finishing that connects checkpointing and state updates.
チュートリアルはほぼ完了ですが、チェックポイントと状態更新を接続する前に確認したいもう一つの概念があります。
This section's code is reproduced below for your reference.
このセクションのコードは、参考のために以下に再掲します。

```python
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage

# NOTE: you must use langchain-core >= 0.3 with Pydantic v2

from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]  # This flag is new
    ask_human: bool

class RequestAssistance(BaseModel):
    """Escalate the conversation to an expert.
    会話を専門家にエスカレーションします。
    Use this if you are unable to assist directly or if the user requires support beyond your permissions.
    直接支援できない場合や、ユーザーがあなたの権限を超えた支援を必要とする場合に使用します。
    To use this function, relay the user's 'request' so the expert can provide the right guidance.
    この機能を使用するには、ユーザーの「リクエスト」を中継して、専門家が適切なガイダンスを提供できるようにします。
    """
    request: str

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# We can bind the llm to a tool definition, a pydantic model, or a json schema

llm_with_tools = llm.bind_tools(tools + [RequestAssistance])

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if (response.tool_calls and response.tool_calls[0]["name"] == RequestAssistance.**name**):
        ask_human = True
    return {
        "messages": [response],
        "ask_human": ask_human
    }

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=[tool]))

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(content=response, tool_call_id=ai_message.tool_calls[0]["id"],)

def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(create_response("No response from human.", state["messages"][-1]))
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }

graph_builder.add_node("human", human_node)

def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    # Otherwise, we can route as before
    return tools_condition(state)

graph_builder.add_conditional_edges("chatbot", select_next_node, {"human": "human", "tools": "tools", "**end**": "**end**"},)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.set_entry_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory, interrupt_before=["human"],)
```

<!-- ここまで読んだ! -->

## Part 7: Time Travel¶ 第7部: タイムトラベル

In a typical chat bot workflow, the user interacts with the bot 1 or more times to accomplish a task.
典型的なチャットボットのワークフローでは、**ユーザはタスクを達成するためにボットと1回以上対話**します。
In the previous sections, we saw how to add memory and a human-in-the-loop to be able to checkpoint our graph state and manually override the state to control future responses.
前のセクションでは、メモリを追加し、ヒューマン・イン・ザ・ループを使用してグラフの状態をチェックポイントし、将来の応答を制御するために状態を手動でオーバーライドする方法を見ました。

But what if you want to let your user start from a previous response and "branch off" to explore a separate outcome?
しかし、ユーザが以前の応答から始めて「分岐」し、別の結果を探求できるようにしたい場合はどうでしょうか？
Or what if you want users to be able to "rewind" your assistant's work to fix some mistakes or try a different strategy (common in applications like autonomous software engineers)?
あるいは、**ユーザがアシスタントの作業を「巻き戻して」、いくつかの間違いを修正したり、異なる戦略を試したりできるようにしたい**場合（自律ソフトウェアエンジニアのようなアプリケーションで一般的）にはどうでしょうか？

You can create both of these experiences and more using LangGraph's built-in "time travel" functionality.
**LangGraphの組み込み「タイムトラベル」機能**を使用することで、これらの体験やその他の体験を作成できます。

In this section, you will "rewind" your graph by fetching a checkpoint using the graph's get_state_history method.
このセクションでは、グラフの `get_state_history` メソッドを使用してチェックポイントを取得することで、グラフを「巻き戻します」。

You can then resume execution at this previous point in time.
その後、この以前の時点で実行を再開できます。

First, recall our chatbot graph.
まず、私たちのチャットボットグラフを思い出してください。

We don't need to make any changes from before:
以前から変更を加える必要はありません：

```python
from typing import Annotated, Literal
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, ToolMessage

# NOTE: you must use langchain-core >= 0.3 with Pydantic v2

from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]
    # This flag is new
    ask_human: bool

class RequestAssistance(BaseModel):
    """Escalate the conversation to an expert. Use this if you are unable to assist directly or if the user requires support beyond your permissions.
    To use this function, relay the user's 'request' so the expert can provide the right guidance."""
    request: str

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# We can bind the llm to a tool definition, a pydantic model, or a json schema

llm_with_tools = llm.bind_tools(tools + [RequestAssistance])

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if response.tool_calls and response.tool_calls[0]["name"] == RequestAssistance.**name**:
        ask_human = True
    return {"messages": [response], "ask_human": ask_human}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=[tool]))

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(content=response, tool_call_id=ai_message.tool_calls[0]["id"],)

def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(create_response("No response from human.", state["messages"][-1]))
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }

graph_builder.add_node("human", human_node)

def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    # Otherwise, we can route as before
    return tools_condition(state)

graph_builder.add_conditional_edges("chatbot", select_next_node, {"human": "human", "tools": "tools", END: END},)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory, interrupt_before=["human"],)

```

```

from IPython.display import Image, display
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

```

Let's have our graph take a couple steps.
グラフにいくつかのステップを実行させましょう。

Every step will be checkpointed in its state history:
すべてのステップは、その状態履歴にチェックポイントされます。

```python
config = {"configurable": {"thread_id": "1"}}
events = graph.stream({"messages": [("user", "I'm learning LangGraph. Could you do some research on it for me?")]}, config, stream_mode="values",)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```shell
================================[1m Human Message [0m=================================
I'm learning LangGraph. Could you do some research on it for me?
==================================[1m Ai Message [0m==================================
[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and accurate information, I'll use the Tavily search function to gather details about LangGraph. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_019HPZEw6v1eSLBXnwxk6MZm', 'input': {'query': 'LangGraph framework for language models'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_019HPZEw6v1eSLBXnwxk6MZm)
Call ID: toolu_019HPZEw6v1eSLBXnwxk6MZm
Args: query: LangGraph framework for language models
=================================[1m Tool Message [0m=================================
Name: tavily_search_results_json
[{"url": "https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141", "content": "LangGraph is a powerful tool for building stateful, multi-actor applications with Large Language Models (LLMs). It extends the LangChain library, allowing you to coordinate multiple chains (or ..."}, {"url": "https://towardsdatascience.com/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787", "content": "LangChain is one of the leading frameworks for building applications powered by Lardge Language Models. With the LangChain Expression Language (LCEL), defining and executing step-by-step action sequences — also known as chains — becomes much simpler. In more technical terms, LangChain allows us to create DAGs (directed acyclic graphs)."}]
==================================[1m Ai Message [0m==================================
Thank you for your patience. I've gathered some information about LangGraph for you. Let me summarize the key points:

1. What is LangGraph?
LangGraph is a powerful tool designed for building stateful, multi-actor applications using Large Language Models (LLMs). It's an extension of the LangChain library, which is already a popular framework for developing LLM-powered applications.
2. Purpose and Functionality:

- LangGraph allows developers to coordinate multiple chains or actors within a single application.
- It enhances the capabilities of LangChain by introducing more complex, stateful workflows.

3. Relation to LangChain:

- LangGraph builds upon LangChain, which is one of the leading frameworks for creating LLM-powered applications.
- LangChain itself uses the LangChain Expression Language (LCEL) to define and execute step-by-step action sequences, also known as chains.
- LangChain allows the creation of DAGs (Directed Acyclic Graphs), which represent the flow of operations in an application.

4. Key Features:

- Stateful Applications: Unlike simple query-response models, LangGraph allows the creation of applications that maintain state across interactions.
- Multi-Actor Systems: It supports coordinating multiple AI "actors" or components within a single application, enabling more complex interactions and workflows.

5. Use Cases:
While not explicitly mentioned in the search results, LangGraph is typically used for creating more sophisticated AI applications such as:

- Multi-turn conversational agents
- Complex task-planning systems
- Applications requiring memory and context management across multiple steps or actors
Learning LangGraph can be a valuable skill, especially if you're interested in developing advanced applications with LLMs that go beyond simple question-answering or text generation tasks. It allows for the creation of more dynamic, interactive, and stateful AI systems.
Is there any specific aspect of LangGraph you'd like to know more about, or do you have any questions about how it compares to or works with LangChain?
```

```python
# events = graph.stream({"messages": [("user", "Ya that's helpful. Maybe I'll build an autonomous agent with it!")]}, config, stream_mode="values",)
events = graph.stream({"messages": [("user", "わあ、とても助かります! それで自律エージェントを構築するかもしれません!")]}, config, stream_mode="values",)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```shell
================================[1m Human Message [0m=================================
Ya that's helpful. Maybe I'll build an autonomous agent with it!
==================================[1m Ai Message [0m==================================
[{'text': "That's an excellent idea! Building an autonomous agent with LangGraph is a great way to explore its capabilities and learn about advanced AI application development. LangGraph's features make it well-suited for creating autonomous agents. Let me provide some additional insights and encouragement for your project.", 'type': 'text'}, {'id': 'toolu_017t6BS5rNCzFWcpxRizDKjE', 'input': {'query': 'building autonomous agents with LangGraph examples and tutorials'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_017t6BS5rNCzFWcpxRizDKjE)
Call ID: toolu_017t6BS5rNCzFWcpxRizDKjE
Args: query: building autonomous agents with LangGraph examples and tutorials
=================================[1m Tool Message [0m=================================
Name: tavily_search_results_json
[{"url": "https://medium.com/@lucas.dahan/hands-on-langgraph-building-a-multi-agent-assistant-06aa68ed942f", "content": "Building the Graph. With our agents defined, we'll create a graph.py file to orchestrate their interactions. The basic graph structure in LangGraph is really simple, here we are going to use ..."}, {"url": "https://medium.com/@cplog/building-tool-calling-conversational-ai-with-langchain-and-langgraph-a-beginners-guide-8d6986cc589e", "content": "Introduction to AI Agent with LangChain and LangGraph: A Beginner’s Guide Two powerful tools revolutionizing this field are LangChain and LangGraph. In this guide, we’ll explore how these technologies can be combined to build a sophisticated AI assistant capable of handling complex conversations and tasks. Tool calling is a standout feature in agentic design, allowing the LLM to interact with external systems or perform specific tasks via the @tool decorator. While the Assistant class presented here is one approach, the flexibility of tool calling and LangGraph allows for a wide range of designs. With LangChain and LangGraph, you can build a powerful, flexible AI assistant capable of handling complex tasks and conversations. Tool calling significantly enhances the AI’s capabilities by enabling interaction with external systems."}]
==================================[1m Ai Message [0m==================================
Your enthusiasm for building an autonomous agent with LangGraph is fantastic! This project will not only help you learn more about LangGraph but also give you hands-on experience with cutting-edge AI development. Here are some insights and tips to get you started:

1. Multi-Agent Systems:
LangGraph excels at creating multi-agent systems. You could design your autonomous agent as a collection of specialized sub-agents, each handling different aspects of tasks or knowledge domains.
2. Graph Structure:
The basic graph structure in LangGraph is straightforward. You'll create a graph.py file to orchestrate the interactions between your agents or components.
3. Tool Calling:
A key feature you can incorporate is tool calling. This allows your LLM-based agent to interact with external systems or perform specific tasks. You can implement this using the @tool decorator in your code.
4. Flexibility in Design:
LangGraph offers great flexibility in designing your agent. While there are example structures like the Assistant class, you have the freedom to create a wide range of designs tailored to your specific needs.
5. Complex Conversations and Tasks:
Your autonomous agent can be designed to handle sophisticated conversations and complex tasks. This is where LangGraph's stateful nature really shines, allowing your agent to maintain context over extended interactions.
6. Integration with LangChain:
Since LangGraph builds upon LangChain, you can leverage features from both. This combination allows for powerful, flexible AI assistants capable of managing intricate workflows.
7. External System Interaction:
Consider incorporating external APIs or databases to enhance your agent's capabilities. This could include accessing real-time data, performing calculations, or interacting with other services.
8. Tutorial Resources:
There are tutorials available that walk through the process of building AI assistants with LangChain and LangGraph. These can be excellent starting points for your project.
To get started, you might want to:
1. Set up your development environment with LangChain and LangGraph.
2. Define the core functionalities you want your autonomous agent to have.
3. Design the overall structure of your agent, possibly as a multi-agent system.
4. Implement basic interactions and gradually add more complex features like tool calling and state management.
5. Test your agent thoroughly with various scenarios to ensure robust performance.
Remember, building an autonomous agent is an iterative process. Start with a basic version and progressively enhance its capabilities. This approach will help you understand the intricacies of LangGraph while creating a sophisticated AI application.
Do you have any specific ideas about what kind of tasks or domain you want your autonomous agent to specialize in? This could help guide the design and implementation process.
```

Now that we've had the agent take a couple steps, we can replay the full state history to see everything that occurred.
エージェントがいくつかのステップを踏んだので、完全な状態履歴を再生して発生したすべてを確認できます。

```python
to_replay = None
for state in graph.get_state_history(config):
    print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 6:
        # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
        to_replay = state
```

```shell
Num Messages:  8 Next:  ()
--------------------------------------------------------------------------------

Num Messages:  7 Next:  ('chatbot',)
--------------------------------------------------------------------------------

Num Messages:  6 Next:  ('tools',)
--------------------------------------------------------------------------------

Num Messages:  5 Next:  ('chatbot',)
--------------------------------------------------------------------------------

Num Messages:  4 Next:  ('**start**',)
--------------------------------------------------------------------------------

Num Messages:  4 Next:  ()
--------------------------------------------------------------------------------

Num Messages:  3 Next:  ('chatbot',)
--------------------------------------------------------------------------------

Num Messages:  2 Next:  ('tools',)
--------------------------------------------------------------------------------

Num Messages:  1 Next:  ('chatbot',)
--------------------------------------------------------------------------------

Num Messages:  0 Next:  ('**start**',)
--------------------------------------------------------------------------------
```

Notice that checkpoints are saved for every step of the graph. This spans invocations so you can rewind across a full thread's history. We've picked out to_replay as a state to resume from. This is the state after the chatbot node in the second graph invocation above.
**グラフの各ステップにチェックポイントが保存されることに注意**してください。これは呼び出しをまたいでいるため、スレッド全体の履歴を巻き戻すことができます。上記の2番目のグラフ呼び出しのチャットボットノードの後の状態として再開するために to_replay を選択しました。

Resuming from this point should call the action node next.
このポイントから再開すると、次にアクションノードが呼び出されるはずです。

```python
print(to_replay.next)
print(to_replay.config)
```

```shell
('tools',){'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d094-2634-687c-8006-49ddde5b2f1c'}}
```

Notice that the checkpoint's config (to_replay.config) contains a checkpoint_id timestamp. Providing this checkpoint_id value tells LangGraph's checkpointer to load the state from that moment in time. Let's try it below:
チェックポイントの構成（to_replay.config）には、**チェックポイントIDのタイムスタンプが含まれていることに注意**してください。このチェックポイントID値を提供すると、LangGraphのチェックポインターはその時点の状態を読み込むようになります。以下で試してみましょう：

```python
# The `checkpoint_id` in the `to_replay.config` corresponds to a state we've persisted to our checkpointer

for event in graph.stream(None, to_replay.config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()

```

```

==================================[1m Ai Message [0m==================================
[{'text': "That's an excellent idea! Building an autonomous agent with LangGraph is a great way to explore its capabilities and learn about advanced AI application development. LangGraph's features make it well-suited for creating autonomous agents. Let me provide some additional insights and encouragement for your project.", 'type': 'text'}, {'id': 'toolu_017t6BS5rNCzFWcpxRizDKjE', 'input': {'query': 'building autonomous agents with LangGraph examples and tutorials'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls: tavily_search_results_json (toolu_017t6BS5rNCzFWcpxRizDKjE)
Call ID: toolu_017t6BS5rNCzFWcpxRizDKjE
Args: query: building autonomous agents with LangGraph examples and tutorials
=================================[1m Tool Message [0m=================================
Name: tavily_search_results_json
[{"url": "https://blog.langchain.dev/how-to-build-the-ultimate-ai-automation-with-multi-agent-collaboration/", "content": "Learn how to create an autonomous research assistant using LangGraph, an extension of LangChain for agent and multi-agent flows. Follow the steps to define the graph state, initialize the graph, and run the agents for planning, research, review, writing and publishing."}, {"url": "https://medium.com/@lucas.dahan/hands-on-langgraph-building-a-multi-agent-assistant-06aa68ed942f", "content": "Building the Graph. With our agents defined, we'll create a graph.py file to orchestrate their interactions. The basic graph structure in LangGraph is really simple, here we are going to use ..."}]
==================================[1m Ai Message [0m==================================
Great choice! Building an autonomous agent with LangGraph is an excellent way to dive deep into its capabilities. Based on the additional information I've found, here are some insights and steps to help you get started:

1. LangGraph for Autonomous Agents:
LangGraph is particularly well-suited for creating autonomous agents, especially those involving multi-agent collaboration. It allows you to create complex, stateful workflows that can simulate autonomous behavior.
2. Example Project: Autonomous Research Assistant
One popular example is building an autonomous research assistant. This type of project can help you understand the core concepts of LangGraph while creating something useful.
3. Key Steps in Building an Autonomous Agent:
a. Define the Graph State: This involves setting up the structure that will hold the agent's state and context.
b. Initialize the Graph: Set up the initial conditions and parameters for your agent.
c. Create Multiple Agents: For a complex system, you might create several specialized agents, each with a specific role (e.g., planning, research, review, writing).
d. Orchestrate Interactions: Use LangGraph to manage how these agents interact and collaborate.
4. Components of an Autonomous Agent:

- Planning Agent: Determines the overall strategy and steps.
- Research Agent: Gathers necessary information.
- Review Agent: Evaluates and refines the work.
- Writing Agent: Produces the final output.
- Publishing Agent: Handles the final distribution or application of results.

5. Implementation Tips:

- Start with a simple graph structure in LangGraph.
- Define clear roles and responsibilities for each agent or component.
- Use LangGraph's features to manage state and context across the different stages of your agent's workflow.

6. Learning Resources:

- Look for tutorials and examples specifically on building multi-agent systems with LangGraph.
- The LangChain documentation and community forums can be valuable resources, as LangGraph builds upon LangChain.

7. Potential Applications:

- Autonomous research assistants
- Complex task automation systems
- Interactive storytelling agents
- Autonomous problem-solving systems
Building an autonomous agent with LangGraph is an exciting project that will give you hands-on experience with advanced concepts in AI application development. It's a great way to learn about state management, multi-agent coordination, and complex workflow design in AI systems.
As you embark on this project, remember to start small and gradually increase complexity. You might begin with a simple autonomous agent that performs a specific task, then expand its capabilities and add more agents or components as you become more comfortable with LangGraph.
Do you have a specific type of autonomous agent in mind, or would you like some suggestions for beginner-friendly autonomous agent projects to start with?
```

Congratulations! You've now used time-travel checkpoint traversal in LangGraph.
おめでとうございます！これで、LangGraphにおけるタイムトラベルチェックポイントのトラバースを使用しました。

Being able to rewind and explore alternative paths opens up a world of possibilities for debugging, experimentation, and interactive applications.
**巻き戻して代替の経路を探求できること**は、デバッグ、実験、インタラクティブなアプリケーションの可能性の世界を開きます。

## Next Steps 次のステップ

Take your journey further by exploring deployment and advanced features:
デプロイメントや高度な機能を探求することで、あなたの旅をさらに進めてください：

### Server Quickstart サーバーのクイックスタート

- LangGraph Server Quickstart: Launch a LangGraph server locally and interact with it using the REST API and LangGraph Studio Web UI.
- LangGraphサーバークイックスタート：LangGraphサーバーをローカルで起動し、REST APIとLangGraph Studio Web UIを使用して対話します。

### LangGraph Cloud

- LangGraph Cloud QuickStart: Deploy your LangGraph app using LangGraph Cloud.
- LangGraph Cloudクイックスタート：LangGraph Cloudを使用してLangGraphアプリをデプロイします。

### LangGraph Framework¶ LangGraphフレームワーク

- LangGraph Concepts: Learn the foundational concepts of LangGraph.
- LangGraphの概念：LangGraphの基本的な概念を学びます。
- LangGraph How-to Guides: Guides for common tasks with LangGraph.
- LangGraph How-toガイド：LangGraphでの一般的なタスクのガイド。

### LangGraph Platform¶ LangGraphプラットフォーム

Expand your knowledge with these resources:
これらのリソースで知識を広げましょう：

- LangGraph Platform Concepts: Understand the foundational concepts of the LangGraph Platform.
  - LangGraph Platformの概念：LangGraph Platformの基本的な概念を理解します。
- LangGraph Platform How-to Guides: Guides for common tasks with LangGraph Platform.
  - LangGraph Platform How-toガイド：LangGraph Platformでの一般的なタスクのガイド。

## Comments コメント

```  
