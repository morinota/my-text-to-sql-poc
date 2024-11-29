<https://langchain-ai.github.io/langgraph/>

### Home ホーム

Skip to content コンテンツをスキップ

Home ホーム

### Initializing search 検索の初期化

GitHub

Home ホーム

### Table of contents 目次

Overview 概要

Key Features 主要機能

LangGraph Platform LangGraphプラットフォーム

Installation インストール

Example 例

Step-by-step Breakdown ステップバイステップの内訳

Documentation ドキュメンテーション

Contributing 貢献

### LangGraph

⚡ Building language agents as graphs ⚡ 言語エージェントをグラフとして構築する

Note 注意
Looking for the JS version? Click here (JS docs). JSバージョンを探していますか？こちらをクリックしてください（JSドキュメント）。

### Overview 概要

LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows.
LangGraphは、LLMを使用して状態を持つマルチアクターアプリケーションを構築するためのライブラリで、**エージェントおよびマルチエージェントワークフローを作成**するために使用されます。
Compared to other LLM frameworks, it offers these core benefits: cycles, controllability, and persistence.
他のLLMフレームワークと比較して、サイクル、制御性、持続性というコアな利点を提供します。
LangGraph allows you to define flows that involve cycles, essential for most agentic architectures, differentiating it from DAG-based solutions.
LangGraphは、**ほとんどのエージェントアーキテクチャに不可欠なサイクルを含むフローを定義することを可能にし、DAGベースのソリューションとは異なります**。(なるほど、循環するワークフローを定義できるのか...!:thinking:)
As a very low-level framework, it provides fine-grained control over both the flow and state of your application, crucial for creating reliable agents.
非常に低レベルのフレームワークとして、アプリケーションのフローと状態の両方に対して詳細な制御を提供し、信頼性の高いエージェントを作成するために重要です。
Additionally, LangGraph includes built-in persistence, enabling advanced human-in-the-loop and memory features.
さらに、LangGraphには組み込みの持続性が含まれており、高度なヒューマンインザループおよびメモリ機能を可能にします。

LangGraph is inspired by Pregel and Apache Beam.
LangGraphはPregelとApache Beamに触発されています。
The public interface draws inspiration from NetworkX.
公開インターフェースはNetworkXからインスピレーションを得ています。
LangGraph is built by LangChain Inc, the creators of LangChain, but can be used without LangChain.
LangGraphはLangChainの創設者であるLangChain Incによって構築されていますが、LangChainなしでも使用できます。

LangGraph Platform is infrastructure for deploying LangGraph agents.
LangGraphプラットフォームは、LangGraphエージェントを展開するためのインフラストラクチャです。(Streamlit appをデプロイできるサービスがあるのと同じ感じかな...!:thinking:)
It is a commercial solution for deploying agentic applications to production, built on the open-source LangGraph framework.
これは、オープンソースのLangGraphフレームワークに基づいて、エージェントアプリケーションを本番環境に展開するための商業ソリューションです。
The LangGraph Platform consists of several components that work together to support the development, deployment, debugging, and monitoring of LangGraph applications:
LangGraphプラットフォームは、LangGraphアプリケーションの開発、展開、デバッグ、および監視をサポートするために連携して機能するいくつかのコンポーネントで構成されています：
LangGraph Server (APIs), LangGraph SDKs (clients for the APIs), LangGraph CLI (command line tool for building the server), LangGraph Studio (UI/debugger),
LangGraphサーバー（API）、LangGraph SDK（APIのクライアント）、LangGraph CLI（サーバーを構築するためのコマンドラインツール）、LangGraphスタジオ（UI/デバッガ）です。

To learn more about LangGraph, check out our first LangChain Academy course, Introduction to LangGraph, available for free here.
LangGraphについて詳しく学ぶには、こちらで無料で利用できる最初のLangChain Academyコース「LangGraphの紹介」をご覧ください。

<!-- ここまで読んだ! -->

### Key Features 主要機能

**Cycles and Branching**: Implement loops and conditionals in your apps.
サイクルと分岐：アプリにループと条件文を実装します。

**Persistence**: Automatically save state after each step in the graph.
持続性：グラフの各ステップの後に状態を自動的に保存します。
Pause and resume the graph execution at any point to support error recovery, human-in-the-loop workflows, time travel and more.
任意のポイントでグラフの実行を一時停止および再開して、エラー回復、ヒューマンインザループワークフロー、タイムトラベルなどをサポートします。

**Human-in-the-Loop**: Interrupt graph execution to approve or edit next action planned by the agent.
ヒューマンインザループ：エージェントが計画した次のアクションを承認または編集するためにグラフの実行を中断します。

**Streaming Support**: Stream outputs as they are produced by each node (including token streaming).
ストリーミングサポート：各ノードによって生成される出力をストリーミングします（トークンストリーミングを含む）。

**Integration with LangChain**: LangGraph integrates seamlessly with LangChain and LangSmith (but does not require them).
LangChainとの統合：LangGraphはLangChainおよびLangSmithとシームレスに統合されます（**ただし、それらは必要ありません**）。

<!-- ここまで読んだ! -->

### LangGraph Platform LangGraphプラットフォーム

LangGraph Platform is a commercial solution for deploying agentic applications to production, built on the open-source LangGraph framework.
LangGraphプラットフォームは、オープンソースのLangGraphフレームワークに基づいて、エージェントアプリケーションを本番環境に展開するための商業ソリューションです。
Here are some common issues that arise in complex deployments, which LangGraph Platform addresses:
ここでは、複雑な展開で発生する一般的な問題と、LangGraphプラットフォームが対処する方法を示します：

Streaming support: LangGraph Server provides multiple streaming modes optimized for various application needs
ストリーミングサポート：LangGraphサーバーは、さまざまなアプリケーションニーズに最適化された複数のストリーミングモードを提供します。
Background runs: Runs agents asynchronously in the background
バックグラウンド実行：エージェントを非同期でバックグラウンドで実行します。
Support for long running agents: Infrastructure that can handle long running processes
長時間実行されるエージェントのサポート：長時間実行されるプロセスを処理できるインフラストラクチャです。
Double texting: Handle the case where you get two messages from the user before the agent can respond
ダブルテキスト：エージェントが応答する前にユーザーから2つのメッセージを受け取る場合を処理します。
Handle burstiness: Task queue for ensuring requests are handled consistently without loss, even under heavy loads
バースト性の処理：重い負荷の下でもリクエストが一貫して処理され、損失がないことを保証するためのタスクキューです。

### Installation インストール

pip install -U langgraph

### Example 例

One of the central concepts of LangGraph is state.
**LangGraphの中心的な概念の1つはstate(状態)**です。
Each graph execution creates a state that is passed between nodes in the graph as they execute, and each node updates this internal state with its return value after it executes.
各グラフの実行は、実行中にグラフ内のノード間で渡される状態を作成し、各ノードは実行後にその戻り値でこの内部状態を更新します。
The way that the graph updates its internal state is defined by either the type of graph chosen or a custom function.
グラフが内部状態を更新する方法は、選択されたグラフのタイプまたはカスタム関数によって定義されます。
Let's take a look at a simple example of an agent that can use a search tool.
検索ツールを使用できるエージェントの簡単な例を見てみましょう。

```bash
pip install langchain-anthropic
export ANTHROPIC_API_KEY=sk-...
```

Optionally, we can set up LangSmith for best-in-class observability.
オプションで、最高の可視性を得るためにLangSmithを設定できます。

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_sk_...
```

```python
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# Define the tools for the agent to use

# エージェントが使用するツールを定義します
@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

tools = [search]

tool_node = ToolNode(tools)

model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0).bind_tools(tools)

# Define the function that determines whether to continue or not
# 続行するかどうかを決定する関数を定義します
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END

# Define the function that calls the model
# モデルを呼び出す関数を定義します
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define a new graph 新しいグラフを定義します

workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between サイクルする2つのノードを定義します
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent` エントリーポイントを`agent`として設定します
# This means that this node is the first one called これは、このノードが最初に呼び出されることを意味します
workflow.add_edge(START, "agent")

# We now add a conditional edge 条件付きエッジを追加します
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`. まず、開始ノードを定義します。`agent`を使用します。
    "agent",
    # Next, we pass in the function that will determine which node is called next. 次に、次に呼び出されるノードを決定する関数を渡します。
    should_continue,
)

# We now add a normal edge from `tools` to `agent` `tools`から`agent`への通常のエッジを追加します
workflow.add_edge("tools", 'agent')

# Initialize memory to persist state between graph runs グラフの実行間で状態を持続させるためにメモリを初期化します
checkpointer = MemorySaver()

# Finally, we compile it 最後に、コンパイルします
# This compiles it into a LangChain Runnable これはLangChain Runnableにコンパイルされます
# meaning you can use it as you would any other runnable つまり、他の実行可能なものと同様に使用できます
# Note that we're (optionally) passing the memory when compiling the graphグラフをコンパイルする際にメモリを渡すことも（オプションで）できます
app = workflow.compile(checkpointer=checkpointer)

# Use the Runnable
final_state = app.invoke(
    {"messages": [HumanMessage(content="what is the weather in sf")]},
    config={"configurable": {"thread_id": 42}}
)
final_state["messages"][-1].content

"Based on the search results, I can tell you that the current weather in San Francisco is:\n\nTemperature: 60 degrees Fahrenheit\nConditions: Foggy\n\nSan Francisco is known for its microclimates and frequent fog, especially during the summer months. The temperature of 60°F (about 15.5°C) is quite typical for the city, which tends to have mild temperatures year-round. The fog, often referred to as "Karl the Fog" by locals, is a characteristic feature of San Francisco's weather, particularly in the mornings and evenings.\n\nIs there anything else you’d like to know about the weather in San Francisco or any other location?"
```

Now when we pass the same "thread_id", the conversation context is retained via the saved state (i.e. stored list of messages)
同じ"thread_id"を渡すと、保存された状態（すなわち、保存されたメッセージのリスト）を介して会話のコンテキストが保持されます

```python
final_state = app.invoke(
    {"messages": [HumanMessage(content="what about ny")]},
    config={"configurable": {"thread_id": 42}}
)
final_state["messages"][-1].content

"Based on the search results, I can tell you that the current weather in New York City is:\n\nTemperature: 90 degrees Fahrenheit (approximately 32.2 degrees Celsius)\nConditions: Sunny\n\nThis weather is quite different from what we just saw in San Francisco. New York is experiencing much warmer temperatures right now. Here are a few points to note:\n\n1. The temperature of 90°F is quite hot, typical of summer weather in New York City.\n2. The sunny conditions suggest clear skies, which is great for outdoor activities but also means it might feel even hotter due to direct sunlight.\n3. This kind of weather in New York often comes with high humidity, which can make it feel even warmer than the actual temperature suggests.\n\nIt's interesting to see the stark contrast between San Francisco's mild, foggy weather and New York's hot, sunny conditions. This difference illustrates how varied weather can be across different parts of the United States, even on the same day.\n\nIs there anything else you'd like to know about the weather in New York or any other location?"
```

### Step-by-step Breakdown ステップバイステップの内訳

1. Initialize the model and tools.
   モデルとツールを初期化します。
   we use ChatAnthropic as our LLM.
   ChatAnthropicをLLMとして使用します。
   NOTE: we need make sure the model knows that it has these tools available to call.
   注意：モデルがこれらのツールを呼び出すことができることを知っていることを確認する必要があります。
   We can do this by converting the LangChain tools into the format for OpenAI tool calling using the .bind_tools() method.
   これは、LangChainツールをOpenAIツール呼び出し用の形式に変換することで行えます。
   we define the tools we want to use - a search tool in our case.
   使用したいツールを定義します - この場合は検索ツールです。
   It is really easy to create your own tools - see documentation here on how to do that here.
   自分のツールを作成するのは非常に簡単です - こちらのドキュメント(すでに読んだ!)でその方法を確認してください。

2. Initialize graph with state.
   状態を持つグラフを初期化します。
   we initialize graph (StateGraph) by passing state schema (in our case MessagesState)
   状態スキーマ（この場合はMessagesState）を渡してグラフ（StateGraph）を初期化します。
   MessagesState is a prebuilt state schema that has one attribute -- a list of LangChain Message objects, as well as logic for merging the updates from each node into the state
   MessagesStateは、LangChainメッセージオブジェクトのリストという1つの属性を持つ事前構築された状態スキーマであり、各ノードからの更新を状態にマージするためのロジックも含まれています。

3. Define graph nodes.
   グラフノードを定義します。
   There are two main nodes we need:
   必要な主なノードは2つです：
   The agent node: responsible for deciding what (if any) actions to take.
   **エージェントノード**：どのアクションを取るか（ある場合）を決定する責任があります。
   The tools node that invokes tools: if the agent decides to take an action, this node will then execute that action.
   **ツールを呼び出すツールノード**：エージェントがアクションを取ることを決定した場合、このノードがそのアクションを実行します。
   <!-- ここまで読んだ! -->

4. Define entry point and graph edges.
   エントリーポイントとグラフエッジを定義します。
   First, we need to set the entry point for graph execution - agent node.
   まず、グラフ実行のエントリーポイントを設定する必要があります - エージェントノードです。
   Then we define one normal and one conditional edge.
   次に、1つの通常のエッジと1つの条件付きエッジを定義します。
   Conditional edge means that the destination depends on the contents of the graph's state (MessageState).
   条件付きエッジは、宛先がグラフの状態（MessageState）の内容に依存することを意味します。
   In our case, the destination is not known until the agent (LLM) decides.
   この場合、宛先はエージェント（LLM）が決定するまで不明です。

   Conditional edge: after the agent is called, we should either:
   条件付きエッジ：エージェントが呼び出された後、次のいずれかを実行する必要があります：
   a. Run tools if the agent said to take an action, OR
   a. エージェントがアクションを取ると言った場合はツールを実行します、または
   b. Finish (respond to the user) if the agent did not ask to run tools
   b. エージェントがツールを実行するように求めなかった場合は終了します（ユーザーに応答します）。

   Normal edge: after the tools are invoked, the graph should always return to the agent to decide what to do next
   通常のエッジ：ツールが呼び出された後、グラフは常にエージェントに戻って次に何をするかを決定する必要があります。

5. Compile the graph.
   グラフをコンパイルします。
   When we compile the graph, we turn it into a LangChain Runnable, which automatically enables calling .invoke(), .stream() and .batch() with your inputs
   **グラフをコンパイルすると、それをLangChain Runnableに変換し**、.invoke()、.stream()、.batch()を入力とともに自動的に呼び出せるようになります。
   We can also optionally pass checkpointer object for persisting state between graph runs, and enabling memory, human-in-the-loop workflows, time travel and more.
   グラフの実行間で状態を持続させるためにチェックポインタオブジェクトを渡すことも（オプションで）できます。
   In our case we use MemorySaver - a simple in-memory checkpointer
   この場合、MemorySaver - シンプルなインメモリチェックポインタを使用します。

6. Execute the graph.
   グラフを実行します。
   LangGraph adds the input message to the internal state, then passes the state to the entrypoint node, "agent".
   LangGraphは入力メッセージを内部状態に追加し、その後状態をエントリーポイントノード「エージェント」に渡します。
   The "agent" node executes, invoking the chat model.
   「エージェント」ノードが実行され、チャットモデルを呼び出します。
   The chat model returns an AIMessage. LangGraph adds this to the state.
   チャットモデルはAIメッセージを返します。LangGraphはこれを状態に追加します。

   Graph cycles the following steps until there are no more tool_calls on AIMessage:
   グラフは、AIメッセージにツール呼び出しがなくなるまで次のステップを繰り返します：

   If AIMessage has tool_calls, "tools" node executes
   AIメッセージにツール呼び出しがある場合、「ツール」ノードが実行されます。
   The "agent" node executes again and returns AIMessage
   「エージェント」ノードが再度実行され、AIメッセージを返します。

   Execution progresses to the special END value and outputs the final state.
   実行は特別なEND値に進み、最終状態を出力します。
   And as a result, we get a list of all our chat messages as output.
   その結果、すべてのチャットメッセージのリストが出力されます。

<!-- ここまで読んだ! -->

### Documentation ドキュメンテーション

- Tutorials: Learn to build with LangGraph through guided examples.
チュートリアル：ガイド付きの例を通じてLangGraphを構築する方法を学びます。

- How-to Guides: Accomplish specific things within LangGraph, from streaming, to adding memory & persistence, to common design patterns (branching, subgraphs, etc.), these are the place to go if you want to copy and run a specific code snippet.
ハウツーガイド：ストリーミングからメモリと持続性の追加、一般的なデザインパターン（分岐、サブグラフなど）まで、LangGraph内で特定のことを達成します。特定のコードスニペットをコピーして実行したい場合は、ここが最適です。

- Conceptual Guides: In-depth explanations of the key concepts and principles behind LangGraph, such as nodes, edges, state and more.
概念ガイド：ノード、エッジ、状態など、LangGraphの背後にある主要な概念と原則の詳細な説明です。

- API Reference: Review important classes and methods, simple examples of how to use the graph and checkpointing APIs, higher-level prebuilt components and more.
APIリファレンス：重要なクラスとメソッド、グラフおよびチェックポイントAPIの使用方法の簡単な例、高レベルの事前構築されたコンポーネントなどを確認します。

- LangGraph Platform: LangGraph Platform is a commercial solution for deploying agentic applications in production, built on the open-source LangGraph framework.
LangGraphプラットフォーム：LangGraphプラットフォームは、オープンソースのLangGraphフレームワークに基づいて、エージェントアプリケーションを本番環境に展開するための商業ソリューションです。

### Contributing 貢献

For more information on how to contribute, see here.
貢献する方法についての詳細は、こちらをご覧ください。

<!-- ここまで読んだ -->
