```md
## Concepts 概念

Concepts  
概念  

Skip to content  
コンテンツにスキップ  

Initializing search  
検索の初期化  

GitHub  
GitHub  

Home  
ホーム  

Tutorials  
チュートリアル  

How-to Guides  
ハウツーガイド  

Conceptual Guides  
概念ガイド  

Reference  
リファレンス  

GitHub  
GitHub  

Home  
ホーム  

Tutorials  
チュートリアル  

How-to Guides  
ハウツーガイド  

Conceptual Guides  
概念ガイド  

Conceptual Guides  
概念ガイド  

LangGraph  
LangGraph  

LangGraph  
LangGraph  

Why LangGraph?  
なぜLangGraphなのか？  

LangGraph Glossary  
LangGraph用語集  

Agent architectures  
エージェントアーキテクチャ  

Multi-agent Systems  
マルチエージェントシステム  

Human-in-the-loop  
ヒューマン・イン・ザ・ループ  

Persistence  
永続性  

Memory  
メモリ  

Streaming  
ストリーミング  

FAQ  
よくある質問  

LangGraph Platform  
LangGraphプラットフォーム  

LangGraph Platform  
LangGraphプラットフォーム  

High Level  
高レベル  

Components  
コンポーネント  

LangGraph Server  
LangGraphサーバー  

Deployment Options  
デプロイメントオプション  

Reference  
リファレンス  

Table of contents  
目次  

LangGraph  
LangGraph  

LangGraph Platform  
LangGraphプラットフォーム  

High Level  
高レベル  

Components  
コンポーネント  

LangGraph Server  
LangGraphサーバー  

Deployment Options  
デプロイメントオプション  

Home  
ホーム  

Conceptual Guides  
概念ガイド  

Conceptual Guide¶  
概念ガイド¶  

This guide provides explanations of the key concepts behind the LangGraph framework and AI applications more broadly.  
このガイドは、LangGraphフレームワークとAIアプリケーション全般の背後にある重要な概念の説明を提供します。  

We recommend that you go through at least the Quick Start before diving into the conceptual guide.  
概念ガイドに入る前に、少なくともクイックスタートを通過することをお勧めします。  

This will provide practical context that will make it easier to understand the concepts discussed here.  
これにより、ここで議論されている概念を理解しやすくする実践的な文脈が提供されます。  

The conceptual guide does not cover step-by-step instructions or specific implementation examples — those are found in the Tutorials and How-to guides.  
概念ガイドは、ステップバイステップの指示や特定の実装例をカバーしていません — それらはチュートリアルやハウツーガイドにあります。  

For detailed reference material, please see the API reference.  
詳細なリファレンス資料については、APIリファレンスを参照してください。  

LangGraph¶  
LangGraph¶  

High Level  
高レベル  

Why LangGraph?: A high-level overview of LangGraph and its goals.  
なぜLangGraphなのか？: LangGraphとその目標の高レベルの概要。  

Concepts  
概念  

LangGraph Glossary: LangGraph workflows are designed as graphs, with nodes representing different components and edges representing the flow of information between them.  
LangGraph用語集: LangGraphのワークフローはグラフとして設計されており、ノードは異なるコンポーネントを表し、エッジはそれらの間の情報の流れを表します。  

This guide provides an overview of the key concepts associated with LangGraph graph primitives.  
このガイドは、LangGraphのグラフプリミティブに関連する重要な概念の概要を提供します。  

Common Agentic Patterns: An agent uses an LLM to pick its own control flow to solve more complex problems!  
一般的なエージェントパターン: エージェントはLLMを使用して、より複雑な問題を解決するために自分自身の制御フローを選択します！  

Agents are a key building block in many LLM applications.  
エージェントは、多くのLLMアプリケーションにおける重要な構成要素です。  

This guide explains the different types of agent architectures and how they can be used to control the flow of an application.  
このガイドでは、さまざまなタイプのエージェントアーキテクチャと、それらがアプリケーションのフローを制御するためにどのように使用できるかを説明します。  

Multi-Agent Systems: Complex LLM applications can often be broken down into multiple agents, each responsible for a different part of the application.  
マルチエージェントシステム: 複雑なLLMアプリケーションは、しばしば複数のエージェントに分解でき、それぞれがアプリケーションの異なる部分を担当します。  

This guide explains common patterns for building multi-agent systems.  
このガイドでは、マルチエージェントシステムを構築するための一般的なパターンを説明します。  

Human-in-the-Loop: Explains different ways of integrating human feedback into a LangGraph application.  
ヒューマン・イン・ザ・ループ: LangGraphアプリケーションに人間のフィードバックを統合するさまざまな方法を説明します。  

Persistence: LangGraph has a built-in persistence layer, implemented through checkpointers.  
永続性: LangGraphには、チェックポイントを通じて実装された組み込みの永続性レイヤーがあります。  

This persistence layer helps to support powerful capabilities like human-in-the-loop, memory, time travel, and fault-tolerance.  
この永続性レイヤーは、ヒューマン・イン・ザ・ループ、メモリ、タイムトラベル、フォールトトレランスなどの強力な機能をサポートするのに役立ちます。  

Memory: Memory in AI applications refers to the ability to process, store, and effectively recall information from past interactions.  
メモリ: AIアプリケーションにおけるメモリは、過去のインタラクションから情報を処理、保存、効果的に想起する能力を指します。  

With memory, your agents can learn from feedback and adapt to users' preferences.  
メモリを使用することで、エージェントはフィードバックから学び、ユーザーの好みに適応できます。  

Streaming: Streaming is crucial for enhancing the responsiveness of applications built on LLMs.  
ストリーミング: ストリーミングは、LLM上に構築されたアプリケーションの応答性を向上させるために重要です。  

By displaying output progressively, even before a complete response is ready, streaming significantly improves user experience (UX), particularly when dealing with the latency of LLMs.  
出力を段階的に表示することで、完全な応答が準備される前でも、ストリーミングはユーザーエクスペリエンス（UX）を大幅に向上させ、特にLLMのレイテンシーに対処する際に効果的です。  

FAQ: Frequently asked questions about LangGraph.  
FAQ: LangGraphに関するよくある質問。  

LangGraph Platform¶  
LangGraphプラットフォーム¶  

LangGraph Platform is a commercial solution for deploying agentic applications in production, built on the open-source LangGraph framework.  
LangGraphプラットフォームは、オープンソースのLangGraphフレームワークに基づいて構築された、エージェントアプリケーションを本番環境にデプロイするための商業ソリューションです。  

The LangGraph Platform offers a few different deployment options described in the deployment options guide.  
LangGraphプラットフォームは、デプロイメントオプションガイドで説明されているいくつかの異なるデプロイメントオプションを提供します。  

Tip  
ヒント  

LangGraph is an MIT-licensed open-source library, which we are committed to maintaining and growing for the community.  
LangGraphはMITライセンスのオープンソースライブラリであり、私たちはコミュニティのためにそれを維持し、成長させることにコミットしています。  

You can always deploy LangGraph applications on your own infrastructure using the open-source LangGraph project without using LangGraph Platform.  
LangGraphプラットフォームを使用せずに、オープンソースのLangGraphプロジェクトを使用して、自分のインフラストラクチャ上でLangGraphアプリケーションを常にデプロイできます。  

High Level¶  
高レベル¶  

Why LangGraph Platform?: The LangGraph platform is an opinionated way to deploy and manage LangGraph applications.  
なぜLangGraphプラットフォームなのか？: LangGraphプラットフォームは、LangGraphアプリケーションをデプロイおよび管理するための意見に基づいた方法です。  

This guide provides an overview of the key features and concepts behind LangGraph Platform.  
このガイドは、LangGraphプラットフォームの背後にある重要な機能と概念の概要を提供します。  

Deployment Options: LangGraph Platform offers four deployment options: Self-Hosted Lite, Self-Hosted Enterprise, bring your own cloud (BYOC), and Cloud SaaS.  
デプロイメントオプション: LangGraphプラットフォームは、4つのデプロイメントオプションを提供します: セルフホステッドライト、セルフホステッドエンタープライズ、持ち込みクラウド（BYOC）、およびクラウドSaaS。  

This guide explains the differences between these options, and which Plans they are available on.  
このガイドでは、これらのオプションの違いと、それらが利用可能なプランについて説明します。  

Plans: LangGraph Platforms offer three different plans: Developer, Plus, Enterprise.  
プラン: LangGraphプラットフォームは、3つの異なるプランを提供します: デベロッパー、プラス、エンタープライズ。  

This guide explains the differences between these options, what deployment options are available for each, and how to sign up for each one.  
このガイドでは、これらのオプションの違い、各プランで利用可能なデプロイメントオプション、および各プランへのサインアップ方法を説明します。  

Template Applications: Reference applications designed to help you get started quickly when building with LangGraph.  
テンプレートアプリケーション: LangGraphを使用して迅速に構築を開始するために設計されたリファレンスアプリケーション。  

Components¶  
コンポーネント¶  

The LangGraph Platform comprises several components that work together to support the deployment and management of LangGraph applications:  
LangGraphプラットフォームは、LangGraphアプリケーションのデプロイと管理をサポートするために連携して機能するいくつかのコンポーネントで構成されています:  

LangGraph Server: The LangGraph Server is designed to support a wide range of agentic application use cases, from background processing to real-time interactions.  
LangGraphサーバー: LangGraphサーバーは、バックグラウンド処理からリアルタイムインタラクションまで、幅広いエージェントアプリケーションのユースケースをサポートするように設計されています。  

LangGraph Studio: LangGraph Studio is a specialized IDE that can connect to a LangGraph Server to enable visualization, interaction, and debugging of the application locally.  
LangGraphスタジオ: LangGraphスタジオは、LangGraphサーバーに接続して、アプリケーションの視覚化、インタラクション、およびデバッグをローカルで可能にする専門のIDEです。  

LangGraph CLI: LangGraph CLI is a command-line interface that helps to interact with a local LangGraph.  
LangGraph CLI: LangGraph CLIは、ローカルのLangGraphと対話するのに役立つコマンドラインインターフェースです。  

Python/JS SDK: The Python/JS SDK provides a programmatic way to interact with deployed LangGraph Applications.  
Python/JS SDK: Python/JS SDKは、デプロイされたLangGraphアプリケーションと対話するためのプログラム的な方法を提供します。  

Remote Graph: A RemoteGraph allows you to interact with any deployed LangGraph application as though it were running locally.  
リモートグラフ: リモートグラフを使用すると、デプロイされたLangGraphアプリケーションとローカルで実行されているかのように対話できます。  

LangGraph Server¶  
LangGraphサーバー¶  

Application Structure: A LangGraph application consists of one or more graphs, a LangGraph API Configuration file (langgraph.json), a file that specifies dependencies, and environment variables.  
アプリケーション構造: LangGraphアプリケーションは、1つ以上のグラフ、LangGraph API構成ファイル（langgraph.json）、依存関係を指定するファイル、および環境変数で構成されます。  

Assistants: Assistants are a way to save and manage different configurations of your LangGraph applications.  
アシスタント: アシスタントは、LangGraphアプリケーションの異なる構成を保存および管理する方法です。  

Web-hooks: Webhooks allow your running LangGraph application to send data to external services on specific events.  
ウェブフック: ウェブフックを使用すると、実行中のLangGraphアプリケーションが特定のイベントに基づいて外部サービスにデータを送信できます。  

Cron Jobs: Cron jobs are a way to schedule tasks to run at specific times in your LangGraph application.  
Cronジョブ: Cronジョブは、LangGraphアプリケーション内で特定の時間にタスクを実行するようにスケジュールする方法です。  

Double Texting: Double texting is a common issue in LLM applications where users may send multiple messages before the graph has finished running.  
ダブルテキスト: ダブルテキストは、ユーザーがグラフの実行が完了する前に複数のメッセージを送信する可能性があるLLMアプリケーションで一般的な問題です。  

This guide explains how to handle double texting with LangGraph Deploy.  
このガイドでは、LangGraph Deployを使用してダブルテキストを処理する方法を説明します。  

Deployment Options¶  
デプロイメントオプション¶  

Self-Hosted Lite: A free (up to 1 million nodes executed), limited version of LangGraph Platform that you can run locally or in a self-hosted manner.  
セルフホステッドライト: ローカルまたはセルフホステッド方式で実行できる、無料（最大100万ノード実行）の制限付きLangGraphプラットフォームのバージョン。  

Cloud SaaS: Hosted as part of LangSmith.  
クラウドSaaS: LangSmithの一部としてホストされます。  

Bring Your Own Cloud: We manage the infrastructure, so you don't have to, but the infrastructure all runs within your cloud.  
持ち込みクラウド: 私たちがインフラストラクチャを管理するので、あなたはそれを気にする必要はありませんが、インフラストラクチャはすべてあなたのクラウド内で実行されます。  

Self-Hosted Enterprise: Completely managed by you.  
セルフホステッドエンタープライズ: 完全にあなたが管理します。  

Comments  
コメント  

Back to top  
トップに戻る  

Previous  
前へ  

MULTIPLE_SUBGRAPHS  
MULTIPLE_SUBGRAPHS  

Next  
次へ  

Why LangGraph?  
なぜLangGraphなのか？  

Made with  
作成者  
Material for MkDocs Insiders
```