# Langchain

## callbacksについて

- 参考:<https://book.st-hakky.com/data-science/langchain-callbacks/>
- callbacksとは
  - LangChainに限らずコールバックは、プログラミングにおいて非常に重要な概念。
  - **特定のイベントが発生したときに実行される関数や手続き**を指す。
- LangChainのコールバック
  - 特定のタスクが完了したとき、または特定のイベントが発生したときに呼び出される。これにより、**開発者は特定のタイミングでカスタムロジックを実行できる**ようになる。
    - ex.)
      - LangChainの学習プロセスが終了したときに通知を送る、
      - 特定の条件下で学習を早期終了する、
      - 学習中のモデルのパフォーマンスをログに記録する、etc.
- callback handler
  - LangchainのCallbacksを管理するためのクラス。
    - アプリケーションの特定のイベントに対して、自分で定義した処理を実行可能にする。
  - callback handlerが対応可能なイベント
    - `on_llm_start`: LLMの動作が開始されたとき
    - `on_chat_model_start`: チャットモデルの動作が開始されたとき
    - `on_llm_new_token`: LLMが新しいトークンを生成したとき
    - `on_llm_end`: LLMの動作が終了したとき
    - `on_chain_start`: チェーンの動作が開始されたとき
    - `on_chain_end`: チェーンの動作が終了したとき
    - `on_chain_error`: チェーンの動作中にエラーが発生したとき

- BaseCallbackHandler
  - 他のコールバックハンドラの親クラスとして機能する。すべてのメソッドはデフォルトで何もしないが、継承先のクラスでオーバーライドされる。
-

## カスタムツールの定義

- 独自のAgentを構築する際には、Agentが利用できるtoolのlistを提供する必要がある。

### toolの構成要素

- 呼び出される実際の関数に加えて、toolはいくつかの構成要素を持つ
  - name(str):
    - 必須。Agentに提供されるtool集合の中で、一意である必要がある。
  - description(str):
    - オプショナルだが推奨。Agentがtoolの使用を判断するために使用される。
  - args_schema (Pydantic BaseModel):
    - オプショナルだが推奨。追加情報(ex. few-shot example)やパラメータの検証のために役立つ。

### toolの定義方法

- まず一般的に必要なものをインポートする。

```python
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
```

#### tool decoratorを使う方法

- **`@tool`デコレータは、custom toolを定義する最も簡単な方法**である。
  - デフォルトでは関数名をtool nameとして使用するが、第一引数としてnameを指定することでオーバーライドできる。
  - また、**decorateされた関数のdocstringをdescriptionとして使用する。従って、docstringは必須になる**...!

- 単一の入力値を受け取る関数の例

```python
@tool
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"

print(search.name)
print(search.description)
print(search.args)
```

- 複数の入力値を受け取る関数の例

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

print(multiply.name)
print(multiply.description)
print(multiply.args)
```

- tool nameやargs_schema引数をカスタマイズする場合

```python
class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")

@tool("search-tool", args_schema=SearchInput, return_direct=True)
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"
```

#### BaseToolクラスを継承する方法

- BaseToolクラスをサブクラス化することで、カスタムツールを明示的に定義することもできる。
  - tool decoratorと比較して、より柔軟にcustom toolを定義できる。一方で手間がかかる。

- 単一の入力値を受け取る関数の例

```python
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")

class CustomSearchTool(BaseTool):
    name = "custom_search"
    description = "useful for when you need to answer questions about current events"
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return "LangChain"

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

search = CustomSearchTool()
print(search.name)
print(search.description)
print(search.args)
```

- 複数の入力値を受け取る関数の例

```python
class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True

    def _run(
        self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return a * b

    async def _arun(
        self,
        a: int,
        b: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")

multiply = CustomCalculatorTool()
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)
```

#### StructuredToolデータクラスを使用する方法

hogehoge
