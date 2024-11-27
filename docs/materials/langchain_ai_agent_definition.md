### Agentic Workflows in 2024: The ultimate guide

Participate in our State of AI Development Survey for a chance to win a MacBook M4 Pro!
私たちのAI開発調査に参加して、MacBook M4 Proを獲得するチャンスを得ましょう！

Agentic workflows powered by LLMs are all that is new and exciting when it comes to AI.
LLMによって駆動されるエージェントワークフローは、AIに関して新しくてエキサイティングなすべてです。

But since they’re so new — and quite complex to build — there's no standardized way of building them today.
しかし、彼らは非常に新しく、構築がかなり複雑であるため、今日のところ標準化された構築方法はありません。

Luckily, the field is evolving extremely fast, and we're beginning to see some design patterns emerge.
幸いなことに、この分野は非常に速く進化しており、いくつかのデザインパターンが現れ始めています。

In this article, we’ll explore these emerging design patterns and frequent architectures, along with the challenges and lessons learned from companies building LLM agents in 2024.
この記事では、これらの新たに現れるデザインパターンと頻繁に見られるアーキテクチャ、そして2024年にLLMエージェントを構築している企業から得た課題と教訓を探ります。

Given how rapidly this field evolves, we’ll be publishing more insights and resources on this topic.
この分野がどれほど急速に進化しているかを考慮して、私たちはこのトピックに関するさらなる洞察とリソースを発表する予定です。

We wrote this article based on the latest research and insights from AI consultants, founders and engineers.
私たちは、AIコンサルタント、創業者、エンジニアからの最新の研究と洞察に基づいてこの記事を書きました。

We especially appreciate the input from: Yohei Nakajima, Zac Haris, Eduardo Ordax, Armand Ruiz, Erik Wikander, Vasilie Markovic, and Anton Eremin — Thank you!
特に、Yohei Nakajima、Zac Haris、Eduardo Ordax、Armand Ruiz、Erik Wikander、Vasilie Markovic、Anton Ereminからの意見に感謝します — ありがとうございます！

What is an Agentic Workflow?
エージェントワークフローとは何ですか？

The official definition for the word agentic is the ability to take initiative, make decisions, and exert control over their actions and outcomes.
「エージェント」という言葉の公式な定義は、イニシアティブを取り、決定を下し、自らの行動と結果に対してコントロールを行使する能力です。

In that context, here's our current definition of an agentic workflow:
その文脈において、私たちの現在のエージェントワークフローの定義は次のとおりです：

🦾 An agentic workflow is a system that uses AI to take initiatives, make decisions and exert control — at various stages in the process.
🦾 エージェントワークフローは、AIを使用してイニシアティブを取り、決定を下し、さまざまなプロセスの段階でコントロールを行使するシステムです。

According to this definition, even basic AI workflows can be seen as having agentic behaviors.
この定義によれば、基本的なAIワークフローでさえエージェント的な行動を持っていると見なすことができます。

They make decisions and control the process at the model stage when generating output from given instructions.
彼らは、与えられた指示から出力を生成する際に、モデル段階で決定を下し、プロセスを制御します。

Ultimately, however, these agents should act like us but have the capacity to accomplish much more.
最終的には、これらのエージェントは私たちのように行動すべきですが、はるかに多くのことを達成する能力を持っています。

Each agent should be able to reason and decide which tasks to tackle by looking at our notes, environment, calendar, to-dos, or messages—around the clock.
各エージェントは、私たちのメモ、環境、カレンダー、やるべきこと、メッセージを見て、どのタスクに取り組むかを推論し、決定できる必要があります — 24時間体制で。

The more we allow AI to make decisions on our behalf, the more agentic their behavior becomes.
私たちがAIに私たちの代わりに決定を下すことを許可すればするほど、彼らの行動はよりエージェント的になります。

With that in mind, we decided to focus on the different stages of agentic behavior in current AI architecture rather than trying to come up with the perfect definition.
そのことを考慮して、私たちは完璧な定義を考え出そうとするのではなく、現在のAIアーキテクチャにおけるエージェント的行動の異なる段階に焦点を当てることにしました。

We explore this in more detail in the section below.
以下のセクションでこれをより詳細に探ります。

Emerging Agentic Architectures
新たに現れるエージェントアーキテクチャ

Three levels of agentic behavior: AI Workflow (Output Decisions), Router Workflow (Task Decisions), Autonomous Agent (Process decisions).
エージェント的行動の3つのレベル：AIワークフロー（出力決定）、ルーターワークフロー（タスク決定）、自律エージェント（プロセス決定）。

Level 1: AI workflows, Output Decisions
レベル1：AIワークフロー、出力決定

At this level, the models in our AI Workflows make decisions based on natural language instructions.
このレベルでは、私たちのAIワークフロー内のモデルは自然言語の指示に基づいて決定を下します。

The agentic behavior happens at the model, rather than the architecture level.
エージェント的行動は、アーキテクチャレベルではなくモデルレベルで発生します。

We can learn to prompt these models better, but we still rely on the model to decide what to generate.
私たちはこれらのモデルに対してより良いプロンプトを学ぶことができますが、生成する内容を決定するのは依然としてモデルに依存しています。

Level 2: Router workflows, Task level decisions
レベル2：ルーターワークフロー、タスクレベルの決定

This level outlines architectures where AI models can make decisions about their tools and control the execution path, all within a regulated environment.
このレベルでは、AIモデルがツールに関する決定を下し、実行パスを制御できるアーキテクチャを概説します。すべては規制された環境内で行われます。

This is where most of the innovation happens today.
ここが今日のほとんどの革新が起こる場所です。

We can classify these systems as routers; they control the execution flow, but are limited by a predefined environment of tools and tasks that they can choose to run.
これらのシステムをルーターとして分類できます。彼らは実行フローを制御しますが、実行できるツールとタスクの事前定義された環境によって制限されています。

For example, we’ve built an agentic router which replicates our internal SEO research and writing process.
例えば、私たちは内部のSEOリサーチとライティングプロセスを再現するエージェントルーターを構築しました。

This workflow can decide which tasks/tools to execute, can reflect on its writing, but is limited to the tools that we make available upfront.
このワークフローは、実行するタスク/ツールを決定し、ライティングを振り返ることができますが、私たちが事前に提供するツールに制限されています。

Can my agent decide to skip a specific task? Yes.
私のエージェントは特定のタスクをスキップすることを決定できますか？ はい。

Does it have access to tools? Yes.
ツールにアクセスできますか？ はい。

Can it modify the process itself? No.
プロセス自体を変更できますか？ いいえ。

Is the reflection grounded? No, we’re using an agentic prompting technique (Reflexion).
反省は根拠がありますか？ いいえ、私たちはエージェント的プロンプティング技術（Reflexion）を使用しています。

Zac Harris, founder @ Rankd, Ex: Copy.ai built a similar content machine at Copy AI that automates their content generation end to end.
Zac Harris（Rankdの創設者、元Copy.ai）は、Copy AIでコンテンツ生成をエンドツーエンドで自動化する類似のコンテンツマシンを構築しました。

His workflow follows basic agentic capabilities, from planning to refinement, and creates novel, high-quality content which is not achievable with LLMs out of the box.
彼のワークフローは、計画から洗練までの基本的なエージェント機能に従い、LLMでは実現できない新しい高品質のコンテンツを作成します。

At some stages human input is still needed, but he’s looking to automate the whole process.
いくつかの段階では人間の入力がまだ必要ですが、彼は全プロセスを自動化しようとしています。

You can follow his process here.
彼のプロセスをこちらでフォローできます。

Level 3: Autonomous Agents, Process level decisions
レベル3：自律エージェント、プロセスレベルの決定

Creating autonomous agents is the ultimate goal of agentic workflow development.
自律エージェントを作成することは、エージェントワークフロー開発の最終目標です。

These agents have complete control over the app flow, can write their own code to achieve different objectives, and seek feedback when necessary.
これらのエージェントはアプリのフローを完全に制御し、異なる目的を達成するために自分のコードを書くことができ、必要に応じてフィードバックを求めます。

However, we are quite a while off from using those tools in the real-world.
しかし、私たちはこれらのツールを実世界で使用するにはまだかなりの時間がかかります。

We’ve seen cool demos like the AI engineer Devin, and the first autonomous agent BabyAGI by Yohei, or MetaGPT.. but none are quite ready for production yet.
私たちはAIエンジニアDevinや、Yoheiによる最初の自律エージェントBabyAGI、MetaGPTなどのクールなデモを見てきましたが、どれもまだ生産準備が整っていません。

Fortunately, all these experiments are pushing the industry forward and are slowly defining the fundamental components of these systems.
幸いなことに、これらの実験は業界を前進させており、これらのシステムの基本的なコンポーネントを徐々に定義しています。

Agentic Workflow Components
エージェントワークフローのコンポーネント

Main Components in Agentic Workflows: Planning, Execution, Refinement, Interface.
エージェントワークフローの主なコンポーネント：計画、実行、洗練、インターフェース。

1) Planning
1) 計画

The planning stage outlines the logic of the workflow, and breaks down one big complex task into smaller tasks.
計画段階では、ワークフローの論理を概説し、大きな複雑なタスクを小さなタスクに分解します。

The goal with this stage is to enable the best path for an agent to be able to reason better, and delegate tasks if needed.
この段階の目標は、エージェントがより良く推論できる最適な道を提供し、必要に応じてタスクを委任できるようにすることです。

Depending on the type of architecture (single, or multi-agent) there are various strategies to use here; like CoT, ReAct, Self-Refine, RAISE, Reflextion.
アーキテクチャの種類（単一またはマルチエージェント）に応じて、ここで使用するさまざまな戦略があります。たとえば、CoT、ReAct、Self-Refine、RAISE、Reflextionなどです。

We cover these strategies in the next section.
次のセクションでこれらの戦略を取り上げます。

From Native RAG to Agentic RAG
ネイティブRAGからエージェントRAGへ

“Most customers I work with are in demo space, but for real production enterprise solutions, there are several gaps and a lot of opportunities.”
「私が関わっているほとんどの顧客はデモスペースにいますが、実際の生産エンタープライズソリューションにはいくつかのギャップと多くの機会があります。」

Armand Ruiz, VP of Product - AI Platform at IBM says that there are two types of agentic architectures he frequently sees working with his clients:
IBMのAIプラットフォームの製品担当副社長であるArmand Ruizは、彼がクライアントと一緒に作業する際に頻繁に見るエージェントアーキテクチャの2つのタイプがあると述べています：

- Document Agents: Each document has a dedicated agent for answering questions and summarizing within its scope.
- ドキュメントエージェント：各ドキュメントには、その範囲内で質問に答えたり要約したりするための専用エージェントがあります。

- Meta-Agent: This top-level agent manages the document agents, coordinating their interactions and combining their outputs for comprehensive responses.
- メタエージェント：このトップレベルのエージェントはドキュメントエージェントを管理し、相互作用を調整し、包括的な応答のために出力を統合します。

2) Execution
2) 実行

The execution stage contains the set of helpers like modules, tools, and data that the agent needs to do the job right.
実行段階には、エージェントが仕事を正しく行うために必要なモジュール、ツール、データなどのヘルパーが含まれています。

Access to tools/subagents
ツール/サブエージェントへのアクセス

Your agentic workflow should have access to pre-built tools relevant to your use case which can be referenced at various stages, sequentially or in parallel.
あなたのエージェントワークフローは、さまざまな段階で参照できる、あなたのユースケースに関連する事前構築されたツールにアクセスできる必要があります。これらは順次または並行して使用できます。

Examples include web search, vector stores, URL scrapers, database access, and traditional ML models.
例としては、ウェブ検索、ベクターストア、URLスクレイパー、データベースアクセス、従来のMLモデルなどがあります。

Multi-agent systems should have access to subagents who specialize in specific tasks.
マルチエージェントシステムは、特定のタスクに特化したサブエージェントにアクセスできる必要があります。

If no tool is available for a specific task, an autonomous agent should be able to write code and create its own tools.
特定のタスクに利用可能なツールがない場合、自律エージェントはコードを書いて独自のツールを作成できる必要があります。

For example, this closed-loop approach like LATM (LLMs as Tool Makers) evaluates where tools are needed, and writes custom Python functions.
たとえば、LATM（LLMs as Tool Makers）のようなこのクローズドループアプローチは、ツールが必要な場所を評価し、カスタムPython関数を書きます。

Guardrails and Error handling
ガードレールとエラーハンドリング

Use guardrails to keep your agents safe with validation checks, constraints, and fallback strategies.
ガードレールを使用して、検証チェック、制約、およびフォールバック戦略でエージェントを安全に保ちます。

Implement error handlers to quickly detect, classify, and address issues, ensuring smooth operation.
エラーハンドラーを実装して、問題を迅速に検出、分類、対処し、スムーズな操作を確保します。

Here's a basic strategy for handling non-deterministic failure.
ここに非決定論的な失敗を処理するための基本的な戦略があります。

3) Refinement
3) 洗練

At this step the agent examines the work and comes up with new ways to improve it.
このステップでは、エージェントが作業を検査し、それを改善する新しい方法を考え出します。

If fully autonomous, it can create new paths/tools to arrive to the objective if needed.
完全に自律的であれば、必要に応じて目標に到達するための新しいパス/ツールを作成できます。

LLM-based eval
LLMベースの評価

When possible provide a detailed scoring rubric and use LLMs to evaluate another's outputs.
可能な場合は、詳細なスコアリングルーブリックを提供し、LLMを使用して他者の出力を評価します。

Short-term memory
短期記憶

Long-context windows are making it easier for LLMs to handle short-term memory more effectively, but good prompting techniques should be implemented to achieve the best performance.
長いコンテキストウィンドウにより、LLMが短期記憶をより効果的に処理できるようになっていますが、最良のパフォーマンスを達成するためには良いプロンプティング技術を実装する必要があります。

Long-term memory
長期記憶

When it comes to agents, long-term memory is the biggest unlock, but the biggest challenge as well.
エージェントに関しては、長期記憶が最大の解放ですが、最大の課題でもあります。

For long-term memory between workflows, it's about saving information and then recalling it through tool calls or by injecting memories into prompts.
ワークフロー間の長期記憶については、情報を保存し、それをツール呼び出しを通じて呼び出すか、プロンプトにメモリを注入することに関するものです。

When constructing this long-term memory, you can use several storage solutions (each comes with specific limitations/advantages):
この長期記憶を構築する際には、いくつかのストレージソリューションを使用できます（それぞれ特定の制限/利点があります）：

- Vector stores (like Pinecone and Weaviate), handle unstructured data but can be complex and costly;
- ベクターストア（PineconeやWeaviateなど）は、非構造化データを処理しますが、複雑でコストがかかる場合があります。

- Key/value stores (like Redis and MongoDB), are fast and simple but lack query power;
- キー/値ストア（RedisやMongoDBなど）は、高速でシンプルですが、クエリ機能が不足しています。

- Knowledge Graphs (like Neo4J, Cognee and DGraph), excel at complex relationships but are resource-intensive and can slow down as they grow.
- ナレッジグラフ（Neo4J、Cognee、DGraphなど）は、複雑な関係に優れていますが、リソースを多く消費し、成長するにつれて遅くなる可能性があります。

We wrote more on the topic here.
このトピックについては、こちらでさらに詳しく書きました。

A Graph is All you Need?
グラフが必要なすべてですか？

Yohei Nakajima, Investor and the creator of BabyAGI says that a graph-based agent is really good at reading and understanding everything about itself, which a key part of self-improvement.
投資家でありBabyAGIの創設者であるYohei Nakajimaは、グラフベースのエージェントが自分自身についてすべてを読み理解するのが非常に得意であり、これは自己改善の重要な部分であると言います。

He’s currently rebuilding BabyAGI with three internal layers of graphs that will handle the code and functions, logs and knowledge.
彼は現在、コードと機能、ログ、知識を処理する3つの内部グラフ層を持つBabyAGIを再構築しています。

Knowledge Graphs are becoming the choice for agentic RAG, because they offer a structured method to navigate data, ensuring more ‘deterministic’ outcomes that can be easily traced.
ナレッジグラフは、データをナビゲートするための構造化された方法を提供し、簡単に追跡できるより「決定論的」な結果を保証するため、エージェントRAGの選択肢となりつつあります。

Towards Deterministic LLM outputs with Graphs
グラフを用いた決定論的LLM出力に向けて

Vasilije Markovic, shares that we need to build better memory engines to handle long term memory for agents.
Vasilije Markovicは、エージェントの長期記憶を処理するために、より良いメモリエンジンを構築する必要があると述べています。

He highlights the main challenges with vector databases like problems with interoperability, maintainability, and fault tolerance.
彼は、相互運用性、保守性、耐障害性の問題など、ベクターデータベースに関する主な課題を強調しています。

He is currently building Cognee, a framework that blends graphs, LLMs and vector retrieval to create deterministic outputs and more reliability for production-grade systems.
彼は現在、グラフ、LLM、およびベクタ取得を組み合わせて決定論的出力を作成し、生産グレードのシステムの信頼性を高めるフレームワークCogneeを構築しています。

Even, recent research, like the Microsoft's GraphRAG paper, highlights how knowledge graphs generated by LLMs greatly improve RAG based retrieval.
最近の研究、例えばMicrosoftのGraphRAG論文は、LLMによって生成されたナレッジグラフがRAGベースの取得を大幅に改善する方法を強調しています。

Human in the loop & Evaluations
ループ内の人間と評価

It's interesting — as we give more control to these workflows, we often need to include a human in the loop to make sure they’re not going off the rails.
興味深いことに、これらのワークフローにより多くのコントロールを与えると、彼らが脱線しないようにするために、しばしばループ内に人間を含める必要があります。

If you’re building more advanced agentic workflows today, you must trace every response at each intermediate step to understand how your workflow operates under specific constraints.
今日、より高度なエージェントワークフローを構築している場合、特定の制約の下でワークフローがどのように機能しているかを理解するために、各中間ステップでのすべての応答を追跡する必要があります。

This is crucial because we can't improve what we don't understand.
これは重要です。なぜなら、私たちは理解していないものを改善することができないからです。

In many instances, human review happens in development and in production:
多くのケースで、人間のレビューは開発と生産の両方で行われます：

In Development: Track and replay tasks with new instructions to understand and improve agent behavior.
開発中：新しい指示でタスクを追跡し再生して、エージェントの行動を理解し改善します。

Run test cases at scale to evaluate the outputs.
スケールでテストケースを実行して出力を評価します。

In Production: Set checkpoints to wait for human approval before continuing.
生産中：続行する前に人間の承認を待つためのチェックポイントを設定します。

Run evaluations with new data, to optimize your workflows, and minimize regressions.
新しいデータで評価を実行して、ワークフローを最適化し、回帰を最小限に抑えます。

Debug observability traces and check what your LLM/model sees
デバッグの可観測性トレースを行い、あなたのLLM/モデルが何を見ているかを確認します。

Anton Eremin, founding engineer at Athena, shared that their wide use-case pool introduces a lot of layers and complexity in their AI workflows.
Athenaの創設エンジニアであるAnton Ereminは、彼らの広範なユースケースプールがAIワークフローに多くの層と複雑さをもたらすと共有しました。

"Focus on prompt and context testing before changing code to ensure optimal outcomes and address limitations.
「最適な結果を確保し、制限に対処するために、コードを変更する前にプロンプトとコンテキストのテストに焦点を当ててください。

Ask questions like these:
次のような質問をしてください：

- Can you complete the task with the provided info? What would you add or change?
- 提供された情報でタスクを完了できますか？ 何を追加または変更しますか？

- Does it work on 10 real-world examples? Where does it struggle? Fix it or inform users of the limitations?
- 10の実世界の例で機能しますか？ どこで苦労していますか？ それを修正するか、ユーザーに制限を通知しますか？

- Will the toolset provider, industry best practices, or research solve this in a month?
- ツールセットプロバイダー、業界のベストプラクティス、または研究がこれを1か月で解決しますか？

4) Interface
4) インターフェース

In some sense, this step can be the last and the first step in the agentic workflow - you need to start the agent!
ある意味で、このステップはエージェントワークフローの最後のステップであり最初のステップでもあります - エージェントを起動する必要があります！

Human-Agent Interface
人間-エージェントインターフェース

Many people believe that a great UI/UX can make agents much more effective, and we completely agree!
多くの人々は、優れたUI/UXがエージェントをはるかに効果的にできると信じており、私たちも完全に同意します！

Just as the chat UI transformed interactions with LLMs, new UI concepts could do the same for agents.
チャットUIがLLMとのインタラクションを変革したように、新しいUIコンセプトもエージェントに同じことをする可能性があります。

We think that users will trust an AI agent more if they can follow and interact with its work through a dedicated, interactive interface.
ユーザーが専用のインタラクティブインターフェースを通じてエージェントの作業を追跡し、対話できる場合、AIエージェントをより信頼するようになると考えています。

Another type could be a collaborative UI.
別のタイプは、コラボレーティブUIです。

Imagine "Google Docs" style setup where you leave comments, and the agent updates the content.
コメントを残し、エージェントがコンテンツを更新する「Google Docs」スタイルの設定を想像してください。

Finally, agents should be deeply integrated with our processes and tasks.
最後に、エージェントは私たちのプロセスやタスクに深く統合されるべきです。

True Unlock at the Embedded Stage
埋め込まれた段階での真の解放

Erik Wikander, founder @ Zupyak says that we're just at the beginning of the true potential of AI agents.
Erik Wikander（Zupyakの創設者）は、私たちはAIエージェントの真の可能性の始まりに過ぎないと言います。

”As LLMs mature, we will go from the current co-pilots to AI co-workers.
「LLMが成熟するにつれて、私たちは現在の共同操縦者からAIの共同作業者へと移行します。

The key to unlocking the true value will be in integrating them into existing processes and systems, which will take time.
真の価値を解放する鍵は、彼らを既存のプロセスやシステムに統合することにあり、これは時間がかかります。

For our own use case which is search optimized content marketing, we see value unlocking quickly the more deeply embedded in to existing workflows and processes.”
検索最適化されたコンテンツマーケティングという私たち自身のユースケースでは、既存のワークフローやプロセスに深く埋め込まれるほど、価値が迅速に解放されるのを見ています。」

Agent-Computer Interface
エージェント-コンピュータインターフェース

Even though ACI is a new concept, it's clear that tweaking the agent-computer interface is essential for better agent performance.
ACIは新しい概念ですが、エージェント-コンピュータインターフェースを調整することがエージェントのパフォーマンスを向上させるために不可欠であることは明らかです。

By constantly adjusting the syntax and structure of tool calls to fit the unique behaviors of different models, we can see big performance gains.
異なるモデルのユニークな行動に合わせてツール呼び出しの構文と構造を常に調整することで、大きなパフォーマンス向上が見られます。

It's just as important and complex as creating a great user experience.
これは、優れたユーザーエクスペリエンスを作成することと同じくらい重要であり、複雑です。

Design Patterns
デザインパターン

There are many design patterns that address how the agent decides which tasks to execute, how it handles task execution, and how it processes feedback or reflection.
エージェントがどのタスクを実行するかを決定する方法、タスク実行を処理する方法、フィードバックや反省を処理する方法に対処する多くのデザインパターンがあります。

Eventually, you'll develop a pattern tailored to your use case by testing various implementations and flows.
最終的には、さまざまな実装とフローをテストすることで、あなたのユースケースに合わせたパターンを開発することになります。

But, below we share some of the latest design patterns for inspiration.
しかし、以下にインスピレーションのための最新のデザインパターンのいくつかを共有します。

1) Single Agent architectures
1) シングルエージェントアーキテクチャ

Single Agent architectures contain a dedicated stage for reasoning about the problem before any action is taken to advance the goal.
シングルエージェントアーキテクチャには、目標を進めるために行動を起こす前に問題について推論するための専用のステージが含まれています。

Here are some common architectures and their advantages/limits:
以下は一般的なアーキテクチャとその利点/制限です：

- ReAct cuts down on hallucinations but can get stuck and needs human feedback.
- ReActは幻覚を減少させますが、行き詰まることがあり、人間のフィードバックが必要です。

- Self-Refine improves initial outputs by using iterative feedback and refinement.
- Self-Refineは、反復的なフィードバックと洗練を使用して初期出力を改善します。

- RAISE adds short-term and long-term memory to ReAct but still struggles with hallucinations.
- RAISEはReActに短期記憶と長期記憶を追加しますが、幻覚に苦しんでいます。

- Reflexion improves success rates by using an LLM evaluator for feedback, but its memory is limited.
- Reflexionは、フィードバックのためにLLM評価者を使用することで成功率を改善しますが、そのメモリは制限されています。

- LATS combines planning and Monte-Carlo tree search for better performance.
- LATSは計画とモンテカルロ木探索を組み合わせてパフォーマンスを向上させます。

- PlaG uses directed graphs to run multiple tasks in parallel, boosting efficiency.
- PlaGは有向グラフを使用して複数のタスクを並行して実行し、効率を向上させます。

2) Multi Agent architectures
2) マルチエージェントアーキテクチャ

Multi-agent architectures allow for smart division of tasks based on each agent's skills and provide valuable feedback from different agent perspectives.
マルチエージェントアーキテクチャは、各エージェントのスキルに基づいてタスクの賢い分割を可能にし、異なるエージェントの視点から貴重なフィードバックを提供します。

These are ideal for tasks requiring feedback from multiple perspectives and parallelizing distinct workflows, such as document generation where one agent reviews and provides feedback on another's work.
これらは、複数の視点からのフィードバックを必要とし、異なるワークフローを並行して実行するタスクに最適です。たとえば、1つのエージェントが他のエージェントの作業をレビューしフィードバックを提供するドキュメント生成などです。

Here are some emerging architectures like:
以下は、いくつかの新たに現れるアーキテクチャです：

- Lead Agents improve team efficiency with a designated leader.
- リードエージェントは、指定されたリーダーを持つことでチームの効率を向上させます。

- DyLAN enhances performance by dynamically re-evaluating agent contributions.
- DyLANはエージェントの貢献を動的に再評価することでパフォーマンスを向上させます。

- Agentverse improves problem-solving through structured task phases.
- Agentverseは構造化されたタスクフェーズを通じて問題解決を改善します。

- MetaGPT reduces unproductive chatter by requiring structured outputs.
- MetaGPTは構造化された出力を要求することで生産的でないおしゃべりを減少させます。

- BabyAGI uses an execution, task creation and prioritization agent to organize daily tasks.
- BabyAGIは、日常のタスクを整理するために実行、タスク作成、優先順位付けエージェントを使用します。

Research shows that a single-agent LLM with strong prompts can achieve almost the same performance as multi-agent system.
研究によると、強力なプロンプトを持つシングルエージェントLLMは、マルチエージェントシステムとほぼ同じパフォーマンスを達成できることが示されています。

So when you’re implementing your agent architecture you should decide based on the broader context of your use-case, and not based on the reasoning requirements.
したがって、エージェントアーキテクチャを実装する際には、推論要件に基づくのではなく、ユースケースのより広い文脈に基づいて決定する必要があります。

The AI Agents Stack
AIエージェントスタック

Agentic workflows will require even more prototyping and evaluation before being deployed in production.
エージェントワークフローは、生産に展開される前にさらに多くのプロトタイピングと評価を必要とします。

Today, however, the focus is on understanding the behavior and determining the right architecture.
しかし、今日の焦点は行動を理解し、適切なアーキテクチャを決定することにあります。

Understanding Behavior Comes First
行動を理解することが最初です

”While there's a lot of potential in agentic workflows, many are still struggling to move into production.
「エージェントワークフローには多くの可能性がありますが、多くはまだ生産に移行するのに苦労しています。

Today, when people evaluate Agents performance, they try to understand the flow/trace of the agents to identify the behavior."
今日、人々がエージェントのパフォーマンスを評価する際、彼らはエージェントのフロー/トレースを理解し、行動を特定しようとします。」

Eduardo Ordax, Principal Go to Market Generative AI at AWS
AWSのプリンシパルGo to Market Generative AIであるEduardo Ordax

The more these systems become agentic the more there will be a need for orchestration frameworks.
これらのシステムがエージェント的になるほど、オーケストレーションフレームワークの必要性が高まります。

These frameworks should enable the following:
これらのフレームワークは次のことを可能にする必要があります：

- Tracing and replaying tasks with new instructions to understand and improve agent paths and executions
- 新しい指示でタスクを追跡し再生して、エージェントのパスと実行を理解し改善すること

- Ability to run LLM calls with fallbacks
- フォールバックを伴うLLM呼び出しを実行する能力

- Human approval in production for moderation and error handling
- モデレーションとエラーハンドリングのための生産における人間の承認

- Save and execute tools (library of pre-built tools, with the ability to save new ones)
- ツールを保存して実行する（事前構築されたツールのライブラリ、新しいツールを保存する能力を持つ）

- Executable arbitrary code at every stage of the workflow to allow for customization
- カスタマイズを可能にするためにワークフローの各段階で実行可能な任意のコード

- Built-in or custom metrics to evaluate agentic paths on hundreds of test cases
- 数百のテストケースでエージェント的パスを評価するための組み込みまたはカスタムメトリック

- Ability to integrate user-generated feedback in eval datasets
- 評価データセットにユーザー生成フィードバックを統合する能力

- Version controlled changes to prompts/model without updating code
- コードを更新せずにプロンプト/モデルのバージョン管理された変更

Lessons from AI Experts
AI専門家からの教訓

Many are currently experimenting with LLMs and Agents, but only a few truly understand the space.
現在、多くの人がLLMとエージェントを試していますが、実際にこの分野を理解しているのはごくわずかです。

We talked with some of these experts and cover their lessons learned, observations and current work that can hopefully aid your AI development process.
私たちはこれらの専門家の何人かと話し、彼らの学んだ教訓、観察、そしてあなたのAI開発プロセスを助けることができると期待される現在の作業を取り上げます。

Understanding Behavior Comes First
行動を理解することが最初です

Eduardo Ordax, Principal Go to Market Generative AI at AWS, shared with us that many of their customers at AWS initially began with simple function-calling LLMs and are now transitioning to more sophisticated agentic workflows.
AWSのプリンシパルGo to Market Generative AIであるEduardo Ordaxは、AWSの多くの顧客が最初はシンプルな関数呼び出しLLMから始まり、現在はより洗練されたエージェントワークフローに移行していると私たちに共有しました。

He has seen three main use-cases:
彼は3つの主要なユースケースを見てきました：

- RAG with multiple strategies under a master orchestrator;
- マスターオーケストレーターの下での複数の戦略を持つRAG;

- Agents with traditional ML (i.e., fraud detection);
- 従来のML（例：詐欺検出）を持つエージェント;

- Agents replacing repetitive RPA tasks.
- 繰り返しのRPAタスクを置き換えるエージェント。

Most common challenges he’s seen is identifying the right LLM for specific tasks.
彼が見てきた最も一般的な課題は、特定のタスクに適したLLMを特定することです。

He says that long term memory is a huge challenge, especially for more complex tasks.
彼は、長期記憶が大きな課題であり、特により複雑なタスクにとってそうであると言います。

Most initially start building with LangChain, but as the complexity grows, they transfer to managed services.
ほとんどの人は最初にLangChainで構築を始めますが、複雑さが増すにつれて、管理サービスに移行します。

Eduardo highlights that while there's a lot of potential in agentic workflows, many are still struggling to move into production.
Eduardoは、エージェントワークフローには多くの可能性がある一方で、多くがまだ生産に移行するのに苦労していることを強調しています。

Current evaluations focus more on understanding agent behavior rather than rushing them into production.
現在の評価は、エージェントの行動を理解することに重点を置いており、彼らを生産に急がせることではありません。

Indeed, agents can take many paths and iterations, each with different executions and will require different kind of evals to build confidence in their performance.
実際、エージェントは多くのパスと反復を取ることができ、それぞれ異なる実行を持ち、パフォーマンスに自信を持つために異なる種類の評価が必要になります。

From Native RAG to Agentic RAG
ネイティブRAGからエージェントRAGへ

Armand Ruiz, VP of Product - AI Platform at IBM, says that most customers he works with are in the demo space and use frameworks (Langchain, CrewAI, LlamaIndex) for prototyping.
IBMのAIプラットフォームの製品担当副社長であるArmand Ruizは、彼が関わっているほとんどの顧客がデモスペースにあり、プロトタイピングのためにフレームワーク（Langchain、CrewAI、LlamaIndex）を使用していると述べています。

For real production enterprise solutions, there are still many gaps and opportunities.
実際の生産エンタープライズソリューションには、まだ多くのギャップと機会があります。

He’s currently helping a lot of companies to navigate from native RAG to Agentic RAG architectures because of the need for automating retrieval, and adapting to new data and changing contexts.
彼は現在、情報の自動取得と新しいデータや変化するコンテキストへの適応の必要性から、ネイティブRAGからエージェントRAGアーキテクチャへの移行を支援しています。

These are two types of architectures he frequently sees:
彼が頻繁に見る2つのアーキテクチャは次のとおりです：

- Document Agents: Each document has a dedicated agent for answering questions and summarizing within its scope.
- ドキュメントエージェント：各ドキュメントには、その範囲内で質問に答えたり要約したりするための専用エージェントがあります。

- Meta-Agent: This top-level agent manages the document agents, coordinating their interactions and combining their outputs for comprehensive responses.
- メタエージェント：このトップレベルのエージェントはドキュメントエージェントを管理し、相互作用を調整し、包括的な応答のために出力を統合します。

Embedded Agents: The Biggest Unlock
埋め込まれたエージェント：最大の解放

Erik Wikander, founder @ Zupyak, says that content marketing today is a very fragmented process with lots of stakeholders and systems involved, often with a disconnect between disciplines like SEO and content.
Erik Wikander（Zupyakの創設者）は、今日のコンテンツマーケティングは非常に断片化されたプロセスであり、多くの利害関係者やシステムが関与しており、しばしばSEOとコンテンツのような分野間の断絶があると言います。

Their goal is to streamline this workflow and bridge this gap, which creates a perfect use case for AI agents.
彼らの目標は、このワークフローを合理化し、このギャップを埋めることであり、これはAIエージェントにとって完璧なユースケースを生み出します。

Currently they’re in co-pilot mode, where the user needs to give their input during the full process.
現在、彼らは共同操縦者モードにあり、ユーザーはプロセス全体で入力を提供する必要があります。

They’re using Vellum to build towards more autonomy, allowing the user to simply give the system a task which it then performs on behalf of the user.
彼らはVellumを使用して、ユーザーがシステムにタスクを単に与え、それをユーザーの代わりに実行する方向に向かっています。

But every customer they talk to wants the AI agent, since they want to move their focus from execution to ideas.
しかし、彼らが話すすべての顧客はAIエージェントを望んでおり、実行からアイデアに焦点を移したいと考えています。

Are graphs all you need?
グラフが必要なすべてですか？

While current RAG solutions significantly improve LLM performance, hallucinations remain an issue.
現在のRAGソリューションはLLMのパフォーマンスを大幅に改善しますが、幻覚は依然として問題です。

Today, many are starting to experiment with knowledge graphs, and latest research shows that for specific use-cases LLM-generated knowledge graphs can outperform baseline RAG.
今日、多くの人がナレッジグラフを試し始めており、最新の研究は特定のユースケースにおいてLLM生成のナレッジグラフがベースラインRAGを上回ることを示しています。

Even beyond that, using graphs in conjunction with long-context models can improve reasoning, and many are experimenting with graphs at every level in the agentic workflow.
さらに、長いコンテキストモデルと組み合わせてグラフを使用することで推論が改善され、多くの人がエージェントワークフローのすべてのレベルでグラフを試しています。

We spoke with Yohei and Vasilije, who are actively working in this field.
私たちは、この分野で積極的に活動しているYoheiとVasilijeと話しました。

Graph-based agents
グラフベースのエージェント

Yohei Nakajima, Investor and the creator of BabyAGI, was probably the first to experiment with autonomous agents.
投資家でありBabyAGIの創設者であるYohei Nakajimaは、おそらく自律エージェントを試した最初の人物です。

He iteratively built a task-driven agent to have various modules like: parallel task execution, skills library to generate code and new skills, self-improvement methods, and even experimented with a novel UI.
彼は、並行タスク実行、コードと新しいスキルを生成するためのスキルライブラリ、自己改善方法などのさまざまなモジュールを持つタスク駆動型エージェントを反復的に構築し、新しいUIの実験も行いました。

Today, his approach is changing.
今日、彼のアプローチは変わりつつあります。

He’s rebuilding BabyAGI as graph-based agents, where he has three internal layers of graphs that will handle the code and functions, logs and knowledge.
彼は現在、コードと機能、ログ、知識を処理する3つの内部グラフ層を持つグラフベースのエージェントとしてBabyAGIを再構築しています。

You can follow his building process here.
彼の構築プロセスをこちらでフォローできます。

The path to deterministic LLM outputs
決定論的LLM出力への道

Vasilije Markovic, Founder @ Cognee emphasizes the need for better memory engines to handle long-term memory for agents, addressing challenges with vector databases such as interoperability, maintainability, and fault tolerance.
Vasilije Markovic（Cogneeの創設者）は、エージェントの長期記憶を処理するためにより良いメモリエンジンの必要性を強調し、相互運用性、保守性、耐障害性などのベクターデータベースに関する課題に取り組んでいます。

He is developing a framework that combines graphs, LLMs, and vector retrieval to create deterministic outputs and enhance reliability for production systems.
彼は、グラフ、LLM、およびベクタ取得を組み合わせて決定論的出力を作成し、生産システムの信頼性を高めるフレームワークを開発しています。

How to move fast with AI development
AI開発を迅速に進める方法

Anton Eremin, founding engineer at Athena, shared that working on a really wide use-case pool introduces a lot of layers and complexity in their AI workflows.
Athenaの創設エンジニアであるAnton Ereminは、非常に広範なユースケースプールで作業することが彼らのAIワークフローに多くの層と複雑さをもたらすと共有しました。

To be able to move fast in developing their agentic workflows, they follow a few best practices:
彼らがエージェントワークフローを迅速に開発するために従っているいくつかのベストプラクティスがあります：

- Research Before Implementation: Explore and test open-source implementations before starting new projects to understand abstractions and edge cases.
- 実装前のリサーチ：新しいプロジェクトを開始する前にオープンソースの実装を探求しテストして、抽象化とエッジケースを理解します。

- Buy/Fork Before Building: Use high-quality projects as components to save time and resources.
- 構築する前に購入/フォーク：高品質のプロジェクトをコンポーネントとして使用して時間とリソースを節約します。

- Change Code/Models Before Fine-Tuning: Modify code or models first due to evolving data and new model releases, rather than fine-tuning models.
- 微調整の前にコード/モデルを変更：データの進化や新しいモデルのリリースに応じて、最初にコードやモデルを変更し、モデルを微調整するのではなく。

- Prompt Engineering First: Focus on prompt and context testing before changing code to ensure optimal outcomes and address limitations.
- プロンプトエンジニアリングを最初に：最適な結果を確保し、制限に対処するために、コードを変更する前にプロンプトとコンテキストのテストに焦点を当てます。

- Debug observability traces and check what your LLM/model sees.
- デバッグの可観測性トレースを行い、あなたのLLM/モデルが何を見ているかを確認します。

Focus on prompt and context testing before changing code to ensure optimal outcomes and address limitations.
最適な結果を確保し、制限に対処するために、コードを変更する前にプロンプトとコンテキストのテストに焦点を当てます。

Ask questions like these:
次のような質問をしてください：

- Would you be able to complete the task with the information and instructions input? What would you add/change?
- 提供された情報と指示でタスクを完了できますか？ 何を追加/変更しますか？

- Does it work on 10 other real-world examples? Where does it struggle and why? Should we solve for this, or just be clear about the current limitations with users and get signal from them before fixing this?
- 10の他の実世界の例で機能しますか？ どこで苦労しており、なぜですか？ これを解決すべきですか、それとも現在の制限についてユーザーに明確にし、修正する前に彼らから信号を得るべきですか？

- Is there a good chance the toolset provider/industry best practices/frontier research will solve this problem for you in a month?
- ツールセットプロバイダー/業界のベストプラクティス/最前線の研究がこの問題を1か月で解決する可能性は高いですか？

Only after doing through everything above it makes sense to touch code and engineer improvements.
上記のすべてを行った後にのみ、コードに触れ、改善を行う意味があります。

From Co-Pilots to Agentic Workflows
共同操縦者からエージェントワークフローへ

Zac Harris, founder @ Rankd, Ex: Copy.ai built a content machine at Copy AI that automates their content generation end to end.
Zac Harris（Rankdの創設者、元Copy.ai）は、Copy AIでコンテンツ生成をエンドツーエンドで自動化するコンテンツマシンを構築しました。

His process includes prioritizing topics, creating briefs and drafts, adding source data, and refinement until the content meets top content standards and guidelines.
彼のプロセスには、トピックの優先順位付け、ブリーフとドラフトの作成、ソースデータの追加、コンテンツが最高のコンテンツ基準とガイドラインを満たすまでの洗練が含まれています。

His workflow mimics some of the basic agentic capabilities.
彼のワークフローは、基本的なエージェント機能のいくつかを模倣しています。

This architecture creates novel, high-quality content which is not achievable with LLMs out of the box.
このアーキテクチャは、LLMでは実現できない新しい高品質のコンテンツを作成します。

While human input is still needed, he’s looking to perfect this system and automate the whole process.
人間の入力がまだ必要ですが、彼はこのシステムを完璧にし、全プロセスを自動化しようとしています。

You can learn more about his technique here.
彼の技術については、こちらでさらに学ぶことができます。

Looking Ahead
今後の展望

Our core belief is that trust is crucial when building these systems, and achieving that trust becomes more challenging as we release more control to agentic workflows.
私たちの核心的な信念は、これらのシステムを構築する際に信頼が重要であり、エージェントワークフローに対するコントロールをより多く放出するにつれて、その信頼を達成することがより困難になるということです。

That's why we need advanced orchestration, observability and evaluation tools.
だからこそ、私たちは高度なオーケストレーション、可観測性、評価ツールを必要としています。

At Vellum, we ensure this trust by helping you build and manage your whole AI development lifecycle - end to end.
Vellumでは、あなたがAI開発ライフサイクル全体を構築し管理するのを助けることで、この信頼を確保しています - エンドツーエンドで。

We've collaborated with hundreds of companies, including Redfin and Drata, and enabled their engineering and product teams to deploy reliable AI systems in production.
私たちはRedfinやDrataを含む数百の企業と協力し、彼らのエンジニアリングおよび製品チームが生産に信頼できるAIシステムを展開できるようにしました。

We're excited to continue innovating in this dynamic space and help more companies integrate AI into their products.
私たちはこのダイナミックな空間での革新を続け、より多くの企業がAIを製品に統合するのを助けることに興奮しています。

If you're interested and you'd like to see a demo, book a call here.
興味がある場合やデモを見たい場合は、こちらで電話を予約してください。

ABOUT THE AUTHOR
著者について

Anita Kirkovska
Anita Kirkovska

Founding GenAI Growth
創設GenAI成長

Anita Kirkovska, is currently leading Growth and Content Marketing at Vellum.
Anita Kirkovskaは、現在Vellumで成長とコンテンツマーケティングをリードしています。

She is a technical marketer, with an engineering background and a sharp acumen for scaling startups.
彼女は技術的なマーケターであり、エンジニアリングのバックグラウンドを持ち、スタートアップをスケールさせるための鋭い洞察力を持っています。

She has helped SaaS startups scale and had a successful exit from an ML company.
彼女はSaaSスタートアップのスケールを支援し、ML企業からの成功したエグジットを果たしました。

Anita writes a lot of content on generative AI to educate business founders on best practices in the field.
Anitaは、ビジネスの創業者にこの分野のベストプラクティスを教育するために、生成AIに関する多くのコンテンツを書いています。

ABOUT THE AUTHOR
著者について

David Vargas
David Vargas

Full Stack Founding Engineer
フルスタック創設エンジニア

David Vargas is a Full-Stack Founding Engineer at Vellum.
David VargasはVellumのフルスタック創設エンジニアです。

He is an experienced software engineer who graduated from MIT in 2017.
彼は2017年にMITを卒業した経験豊富なソフトウェアエンジニアです。

After spending a couple of years at a series C startup, Vargas spent three years on his own as an independent open-source engineer building products for the tools for thought space through a company he still manages called SamePage.
シリーズCのスタートアップで数年を過ごした後、Vargasは独立したオープンソースエンジニアとして3年間、自身が現在も管理しているSamePageという会社を通じて思考ツールのための製品を構築しました。

He now joins Vellum to help build what he believes to be the next era of tools for thought - AI products that could think with us.
彼は現在、私たちと共に考えることができるAI製品、思考のためのツールの次の時代を構築するためにVellumに参加しています。

The Best AI Tips — Direct To Your Inbox
最高のAIヒント — あなたの受信箱に直接

Latest AI news, tips, and techniques
最新のAIニュース、ヒント、テクニック

Specific tips for Your AI use cases
あなたのAIユースケースに特化したヒント

No spam
スパムはありません

Thank you! Your submission has been received!
ありがとうございます！ あなたの提出が受け付けられました！

Oops! Something went wrong while submitting the form.
おっと！ フォームの送信中に何かがうまくいきませんでした。

Each issue is packed with valuable resources, tools, and insights that help us stay ahead in AI development.
各号には、AI開発で先を行くための貴重なリソース、ツール、洞察が詰まっています。

We've discovered strategies and frameworks that boosted our efficiency by 30%, making it a must-read for anyone in the field.
私たちは、効率を30％向上させる戦略とフレームワークを発見しました。これは、この分野の誰にとっても必読です。

Marina Trajkovska
Marina Trajkovska

Head of Engineering
エンジニアリング責任者

This is just a great newsletter.
これは素晴らしいニュースレターです。

The content is so helpful, even when I’m busy I read them.
内容は非常に役立ちます。忙しいときでも私はそれを読みます。

Jeremy Hicks
Jeremy Hicks

Solutions Architect
ソリューションアーキテクト

Related Posts
関連投稿

View More
さらに表示

Guides
ガイド

Synthetic Test Case Generation for LLM Evaluation
LLM評価のための合成テストケース生成

Nov 20, 2024•4min
2024年11月20日•4分

Guides
ガイド

100 Must-Know AI Facts and Statistics for 2024
2024年の知っておくべきAIの事実と統計100選

Oct 16, 2024•5 min
2024年10月16日•5分

Guides
ガイド

Reintroducing Vellum for 2025
2025年のVellumの再紹介

Oct 10, 2024•5 min
2024年10月10日•5分

Guides
ガイド

Cursor AI is god tier
Cursor AIは神のレベルです

Oct 1, 2024•4 min
2024年10月1日•4分

Experiment, Evaluate, Deploy, Repeat.
実験、評価、展開、繰り返し。

AI development doesn’t end once you've defined your system.
AI開発は、システムを定義した時点で終わるわけではありません。

Learn how Vellum helps you manage the entire AI development lifecycle.
VellumがどのようにしてAI開発ライフサイクル全体を管理するのかを学びましょう。

Prompting
プロンプティング

Current Page
現在のページ

Orchestration
オーケストレーション

Current Page
現在のページ

Evaluation
評価

Current Page
現在のページ

Retrieval
取得

Current Page
現在のページ

Deployment
展開

Current Page
現在のページ

Monitoring
監視

Current Page
現在のページ

Build AI systems you can trust
信頼できるAIシステムを構築する

RESOURCES
リソース

Case Studies
ケーススタディ

Guides
ガイド

Product Updates
製品更新

Model Comparison
モデル比較

Documentation
ドキュメント

LLM Leaderboard
LLMリーダーボード

Free Tools
無料ツール

Newsletter
ニュースレター

PRODUCTS
製品

Prompt Engineering
プロンプトエンジニアリング

Document Retrieval
ドキュメント取得

Orchestration
オーケストレーション

evaluations
評価

Deployments
展開

Monitoring
監視

COMPANY
会社

Blog
ブログ

Careers
キャリア

Contact Us
お問い合わせ

Vellum Survey Giveaway Official Rules
Vellum調査ギブアウェイの公式ルール

Terms of Use
利用規約

Privacy Policy
プライバシーポリシー

SOCIALS
ソーシャル

LinkedIn
LinkedIn

Twitter
Twitter

Youtube
Youtube

```
