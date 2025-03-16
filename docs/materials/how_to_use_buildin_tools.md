<https://python.langchain.com/docs/how_to/tools_builtin/>

# How to use built-in tools and toolkits | 🦜️🔗 LangChain 組み込みツールとツールキットの使い方 | 🦜️🔗 LangChain

## How-to guides

## ハウツーガイド

How to use built-in tools and toolkits
組み込みツールとツールキットを使用する方法

### Prerequisites

### 前提条件

This guide assumes familiarity with the following concepts:
このガイドは、以下の概念に精通していることを前提としています：

- LangChain Tools
- LangChain Toolkits

### Tools

### ツール

LangChain has a large collection of 3rd party tools. Please visit Tool Integrations for a list of the available tools.
LangChainには多くのサードパーティツールが揃っています。利用可能なツールのリストについては、[tool integrations](https://python.langchain.com/docs/integrations/tools/)を訪問してください。

- 例えばこんなサードパーティツールがある
  - 検索系
  - Code Interpreter系: Pythonなどのプログラミング言語をサンドボックス環境で実行するための、コードインタプリタを提供するツール達
    - サンドボックス環境: 隔離された安全な仮想環境でコードやプログラムを実行する仕組み。
    - 例
      - Azure Container Apps dynamic sessions
      - Bearly Code Interpreter
      - E2B Data Analysis
      - Riza Code Interpreter

**important**
**重要**

When using 3rd party tools, make sure that you understand how the tool works, what permissions it has. Read over its documentation and check if anything is required from you from a security point of view. Please see our security guidelines for more information.
サードパーティツールを使用する際は、そのツールの動作、権限を理解していることを確認してください。**ドキュメントを読み、セキュリティの観点から何か要求されることがないか**確認してください。詳細については、セキュリティガイドラインをご覧ください。

Let's try out the Wikipedia integration.
Wikipedia統合を試してみましょう。

```python
!pip install -qU langchain-community wikipedia
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
tool = WikipediaQueryRun(api_wrapper=api_wrapper)
print(tool.invoke({"query": "langchain"}))
```

API Reference: WikipediaQueryRun | WikipediaAPIWrapper
APIリファレンス：WikipediaQueryRun | WikipediaAPIWrapper

```
Page: LangChain
Summary: LangChain is a framework designed to simplify the creation of applications
```

The tool has the following defaults associated with it:
ツールには、次のデフォルトが関連付けられています：

```python
print(f"Name: {tool.name}")
print(f"Description: {tool.description}")
print(f"args schema: {tool.args}")
print(f"returns directly?: {tool.return_direct}")
```

```
Name: wikipedia
Description: A wrapper around Wikipedia. Useful for when you need to answer general questions about people, places, companies, facts, historical events, or other subjects. Input should be a search query.
args schema: {'query': {'description': 'query to look up on wikipedia', 'title': 'Query', 'type': 'string'}}
returns directly?: False
```

### Customizing Default Tools

### デフォルトツールのカスタマイズ

We can also modify the built in name, description, and JSON schema of the arguments.
組み込みの名前、説明、および引数のJSONスキーマを変更することもできます。

When defining the JSON schema of the arguments, it is important that the inputs remain the same as the function, so you shouldn't change that. But you can define custom descriptions for each input easily.
引数のJSONスキーマを定義する際には、入力が関数と同じであることが重要ですので、それを変更しないでください。しかし、各入力のカスタム説明を簡単に定義することができます。

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from pydantic import BaseModel, Field

class WikiInputs(BaseModel):
    """Inputs to the wikipedia tool."""
    query: str = Field(
        description="query to look up in Wikipedia, should be 3 or less words"
    )

tool = WikipediaQueryRun(
    name="wiki-tool",
    description="look up things in wikipedia",
    args_schema=WikiInputs,
    api_wrapper=api_wrapper,
    return_direct=True,
)

print(tool.run("langchain"))
```

API Reference: WikipediaQueryRun | WikipediaAPIWrapper
APIリファレンス：WikipediaQueryRun | WikipediaAPIWrapper

Page: LangChain
ページ：LangChain

Summary: LangChain is a framework designed to simplify the creation of applications
要約：LangChainはアプリケーションの作成を簡素化するために設計されたフレームワークです。

```python
print(f"Name: {tool.name}")
print(f"Description: {tool.description}")
print(f"args schema: {tool.args}")
print(f"returns directly?: {tool.return_direct}")
```

Name: wiki-tool
名前：wiki-tool

Description: look up things in wikipedia
説明：Wikipediaで物事を調べる

args schema: {'query': {'description': 'query to look up in Wikipedia, should be 3 or less words', 'title': 'Query', 'type': 'string'}}
引数スキーマ：{'query': {'description': 'Wikipediaで調べるクエリ、3語以下である必要があります', 'title': 'クエリ', 'type': 'string'}}

returns directly?: True
直接返すか？：True

### How to use built-in toolkits

### 組み込みツールキットの使い方

Toolkits are collections of tools that are designed to be used together for specific tasks. They have convenient loading methods.
ツールキットは、特定のタスクのために一緒に使用されるように設計されたツールのコレクションです。便利なロードメソッドがあります。

All Toolkits expose a get_tools method which returns a list of tools.
すべてのツールキットは、ツールのリストを返すget_toolsメソッドを公開しています。

You're usually meant to use them this way:
通常はこのように使用します：

```

```md
# Initialize a toolkittoolkit = ExampleTookit(...)# Get list of toolstools = toolkit.get_tools()Edit this pageWas this page helpful?PreviousHow to handle multiple queries when doing query analysisNextHow to pass through arguments from one step to the nextToolsCustomizing Default ToolsHow to use built-in toolkitsCommunityTwitterGitHubOrganizationPythonJS/TSMoreHomepageBlogYouTubeCopyright © 2024 LangChain, Inc.
# ツールキットを初期化するtoolkit = ExampleTookit(...)# ツールのリストを取得するtools = toolkit.get_tools()このページを編集このページは役に立ちましたか？前回複数のクエリを処理する方法クエリ分析の際次に、あるステップから次のステップへ引数を渡す方法ツールデフォルトツールのカスタマイズ組み込みツールキットの使用方法コミュニティTwitterGitHub組織PythonJS/TSもっとホームページブログYouTube著作権 © 2024 LangChain, Inc.
```
