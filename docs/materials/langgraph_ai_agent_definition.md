### Why LangGraph? なぜLangGraphなのか？

LLMs are extremely powerful, particularly when connected to other systems such as a retriever or APIs.
LLM（大規模言語モデル）は非常に強力であり、特にリトリーバーやAPIなどの他のシステムと接続されているときにその力を発揮します。

This is why many LLM applications use a control flow of steps before and / or after LLM calls.
これが、多くのLLMアプリケーションがLLM呼び出しの前後にステップの制御フローを使用する理由です。

As an example RAG performs retrieval of relevant documents to a question, and passes those documents to an LLM in order to ground the response.
例えば、RAGは質問に関連する文書を取得し、それらの文書をLLMに渡して応答を基にします。

Often a control flow of steps before and / or after an LLM is called a "chain."
LLMの前後のステップの制御フローは「チェーン」と呼ばれることがよくあります。

Chains are a popular paradigm for programming with LLMs and offer a high degree of reliability; the same set of steps runs with each chain invocation.
チェーンはLLMを用いたプログラミングの人気のあるパラダイムであり、高い信頼性を提供します。同じステップのセットが各チェーンの呼び出しで実行されます。

However, we often want LLM systems that can pick their own control flow!
しかし、私たちはしばしば自分自身の制御フローを選択できるLLMシステムを望みます！

This is one definition of an agent: an agent is a system that uses an LLM to decide the control flow of an application.
これはエージェントの一つの定義です：エージェントは、アプリケーションの制御フローを決定するためにLLMを使用するシステムです。

Unlike a chain, an agent gives an LLM some degree of control over the sequence of steps in the application.
チェーンとは異なり、エージェントはアプリケーション内のステップの順序に対してLLMにある程度の制御を与えます。

Examples of using an LLM to decide the control of an application:
アプリケーションの制御を決定するためにLLMを使用する例：

Using an LLM to route between two potential paths
2つの潜在的なパスの間をルーティングするためにLLMを使用する

Using an LLM to decide which of many tools to call
多くのツールの中からどれを呼び出すかを決定するためにLLMを使用する

Using an LLM to decide whether the generated answer is sufficient or more work is need
生成された回答が十分か、さらなる作業が必要かを決定するためにLLMを使用する

There are many different types of agent architectures to consider, which give an LLM varying levels of control.
考慮すべきさまざまなタイプのエージェントアーキテクチャがあり、LLMに異なるレベルの制御を与えます。

On one extreme, a router allows an LLM to select a single step from a specified set of options and, on the other extreme, a fully autonomous long-running agent may have complete freedom to select any sequence of steps that it wants for a given problem.
一方の極端では、ルーターはLLMに指定されたオプションのセットから単一のステップを選択させ、もう一方の極端では、完全に自律的な長時間実行エージェントが特定の問題に対して任意のステップのシーケンスを選択する完全な自由を持つことがあります。

Several concepts are utilized in many agent architectures:
多くのエージェントアーキテクチャで利用されるいくつかの概念：

Tool calling: this is often how LLMs make decisions
ツール呼び出し：これはLLMが意思決定を行う方法です

Action taking: often times, the LLMs' outputs are used as the input to an action
アクションの実行：多くの場合、LLMの出力はアクションへの入力として使用されます

Memory: reliable systems need to have knowledge of things that occurred
メモリ：信頼性のあるシステムは、発生した事柄についての知識を持つ必要があります

Planning: planning steps (either explicit or implicit) are useful for ensuring that the LLM, when making decisions, makes them in the highest fidelity way.
計画：計画ステップ（明示的または暗黙的）は、LLMが意思決定を行う際に、最高の忠実度で行うことを保証するために役立ちます。

Challenges¶
課題

In practice, there is often a trade-off between control and reliability.
実際には、制御と信頼性の間にトレードオフが存在することがよくあります。

As we give LLMs more control, the application often become less reliable.
LLMにより多くの制御を与えると、アプリケーションはしばしば信頼性が低下します。

This can be due to factors such as LLM non-determinism and / or errors in selecting tools (or steps) that the agent uses (takes).
これは、LLMの非決定性やエージェントが使用するツール（またはステップ）を選択する際のエラーなどの要因による可能性があります。

Core Principles¶
コア原則

The motivation of LangGraph is to help bend the curve, preserving higher reliability as we give the agent more control over the application.
LangGraphの動機は、エージェントにアプリケーションに対するより多くの制御を与えながら、より高い信頼性を維持するために曲線を曲げる手助けをすることです。

We'll outline a few specific pillars of LangGraph that make it well suited for building reliable agents.
信頼性のあるエージェントを構築するのに適したLangGraphのいくつかの具体的な柱を概説します。

Controllability
制御可能性

LangGraph gives the developer a high degree of control by expressing the flow of the application as a set of nodes and edges.
LangGraphは、アプリケーションのフローをノードとエッジのセットとして表現することにより、開発者に高い制御を提供します。

All nodes can access and modify a common state (memory).
すべてのノードは共通の状態（メモリ）にアクセスし、これを変更できます。

The control flow of the application can set using edges that connect nodes, either deterministically or via conditional logic.
アプリケーションの制御フローは、ノードを接続するエッジを使用して、決定論的にまたは条件付きロジックを介して設定できます。

Persistence
永続性

LangGraph gives the developer many options for persisting graph state using short-term or long-term (e.g., via a database) memory.
LangGraphは、短期または長期（例：データベースを介して）メモリを使用してグラフ状態を永続化するための多くのオプションを開発者に提供します。

Human-in-the-Loop
人間の介在

The persistence layer enables several different human-in-the-loop interaction patterns with agents; for example, it's possible to pause an agent, review its state, edit it state, and approve a follow-up step.
永続性レイヤーは、エージェントとのさまざまな人間の介在インタラクションパターンを可能にします。例えば、エージェントを一時停止し、その状態をレビューし、状態を編集し、フォローアップステップを承認することが可能です。

Streaming
ストリーミング

LangGraph comes with first class support for streaming, which can expose state to the user (or developer) over the course of agent execution.
LangGraphは、エージェントの実行中に状態をユーザー（または開発者）に公開できる一流のストリーミングサポートを提供します。

LangGraph supports streaming of both events (like a tool call being taken) as well as of tokens that an LLM may emit.
LangGraphは、イベント（ツール呼び出しが行われるなど）とLLMが発信する可能性のあるトークンの両方のストリーミングをサポートしています。

Debugging¶
デバッグ

Once you've built a graph, you often want to test and debug it.
グラフを構築したら、テストとデバッグを行いたくなることがよくあります。

LangGraph Studio is a specialized IDE for visualization and debugging of LangGraph applications.
LangGraph Studioは、LangGraphアプリケーションの視覚化とデバッグのための専門的なIDEです。

Deployment¶
デプロイメント

Once you have confidence in your LangGraph application, many developers want an easy path to deployment.
LangGraphアプリケーションに自信を持ったら、多くの開発者はデプロイメントへの簡単な道を望みます。

LangGraph Platform offers a range of options for deploying LangGraph graphs.
LangGraphプラットフォームは、LangGraphグラフをデプロイするためのさまざまなオプションを提供します。
