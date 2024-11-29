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
  - return_direct(bool):
    - オプショナル。Agentにのみ関連する。Trueの場合、与えられたツールを起動したあと、Agentは停止し、結果をユーザに直接返す。

- tips: ツールに適切に選ばれた名前、説明、およびJSONスキーマがあると、モデルのパフォーマンスが向上する

### toolの定義方法

- 関数にtool decoratorを適用する方法
- BaseToolクラスを継承する方法
- StructuredToolデータクラスを使用する方法
- Runnablesからtoolを作成する方法

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
# search
# Look up things online.
# {'query': {'title': 'Query', 'type': 'string'}}
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
# multiply
# Multiply two numbers.
# {'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
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

- @toolデコレータは`parse_docstring`オプションでgoogleスタイルのdocstringを解析し、docstringのコンポーネント(引数の説明など)をtool schemaの関連部分に紐づけることができる。
  - デフォルトでは、@tool(parse_docstring=True)はドキュメンテーション文字列が正しく解析されない場合、ValueErrorを発生させてしまう。
  - 詳細はAPIリファレンスを参照。

```python
@tool(parse_docstring=True)
def foo(bar: str, baz: int) -> str:
    """The foo.
    Args:
        bar: The bar.
        baz: The baz.
    """
    return bar

foo.args_schema.schema()
# {
#     'description': 'The foo.',
#     'properties': {
#         'bar': {'description': 'The bar.', 'title': 'Bar', 'type': 'string'},
#         'baz': {'description': 'The baz.', 'title': 'Baz', 'type': 'integer'}
#     },
#     'required': ['bar', 'baz'],
#     'title': 'fooSchema',
#     'type': 'object'
# }
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

- この方法は、前の2つ(tools decorator, BaseTool)の中間的な方法。
  - BaseToolを継承する方法よりも簡単で、tool decoratorを使う方法よりも柔軟。

```python
def search_function(query: str)->str:
    return "LangChain"

search = StructuredTool.from_function(
    func=search_function,
    name="Search",
    description="useful for when you need to answer questions about current events",
    # coroutine= ... <- you can specify an async method if desired as well
)

print(search.name)
print(search.description)
print(search.args)
```

- custom args_schemaを定義して、入力に関する詳細情報を提供することもできる。

```python
class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True,
    # coroutine= ... <- you can specify an async method if desired as well
)

print(calculator.name) 
# >>> Calculator
print(calculator.description) 
# >>> multiply numbers
print(calculator.args) 
# >>> {'a': {'description': 'first number', 'title': 'A', 'type': 'integer'}, 'b': {'description': 'second number', 'title': 'B', 'type': 'integer'}}

```

#### Runnablesからtoolを作成する方法

- 文字列または辞書入力を受け入れる**LangChain Runnables** (=chain的なやつ...??:thinking:)は、as_toolメソッドを使用してツールに変換でき、名前、説明、および引数の追加スキーマ情報を指定できる。

```python
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [("human", "Hello. Please respond in the style of {answer_style}.")]
)

# Placeholder LLM
llm = GenericFakeChatModel(messages=iter(["hello matey"]))
chain = prompt | llm | StrOutputParser()

as_tool = chain.as_tool(
    name="Style responder", description="Description of when to use tool."
)

as_tool.args
{'answer_style': {'title': 'Answer Style', 'type': 'string'}}
```

### toolのエラーハンドリング

- toolがエラーに遭遇し、例外がキャッチされない場合、agentは実行を停止する。
- Agentに実行を継続させたい場合は、`ToolException`をraiseさせ、`handle_tool_error`を適切に設定できる。
  - `ToolException`がthrowされると、Agentは作業を停止せず、toolの`handle_tool_error`変数にしたがって例外を処理し、処理結果がobservationとしてagentに返される。
    - (`ToolException`を発生させるだけでは意味がなく、`handle_tool_error`変数を適切に設定しないと、エラーが発生した際にAgentが停止してしまう...!!:thinking:)
- `handle_tool_error`変数について
  - bool型やstr型、関数として設定ができる。
    - 関数として設定されている場合は、その関数は`ToolException`を引数として受け取り、str型を返す必要がある。
  - デフォルト値は`False`

- もし`handle_tool_error`を設定しない場合はどうなる?? (i.e. `handle_tool_error=False`)

```python
from langchain_core.tools import ToolException

def search_tool1(s: str):
    raise ToolException("The search tool1 is not available.")

search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
)
search.run("test")

>>> ToolException   Traceback (most recent call last)
>>> ToolException: The search tool1 is not available.
...
```

- 次に、`handle_tool_error`をTrueに設定してみる

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=True,
)
search.run("test")

>>> 'The search tool1 is not available.'  # 処理が停止せず、エラーが処理されていることがわかる
```

- また、`handle_tool_error`に、tool errorを処理するcustom関数を定義する場合
  
```python
def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )

search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=_handle_error,
)
search.run("test")

>>> 'The following errors occurred during tool execution:The search tool1 is not available.Please try another tool.' # 処理が停止せず、エラーが処理されていることがわかる
```

### 非同期(async)なtoolの作成方法

- 前提として、LangChainツールはRunnableインターフェースの実装である。そして、**全てのRunnableはinvokeおよびainvokeメソッド(およびbatch、abatch、astreamなどの他のメソッド)を公開**している。
- なのでtoolも同期処理の実装のみでも、ainvokeメソッドを使用できるが、注意すべき重要なことがある。
  - LangChainはデフォルトで、関数の計算にコストがかかると仮定して非同期実装を提供しており、そのため、実行を別のスレッドに委任する
  - なので、同期ツールではなく非同期ツールを作成する方が効率的。
    - **同期および非同期の両方の実装が必要な場合は、StructuredTool.from_functionを使用するか、BaseToolからサブクラス化する必要がある**。
      - ex. BaseToolの場合は、`def _run()`メソッドと`async def _arun()`メソッドの両方を実装する。
      - ex. StructuredToolの場合は、`func`引数に同期関数、`coroutine`引数に非同期関数を指定する。

### ツール実行の成果物を返す(結構使いそう!)

- 時には、**ツールの実行の成果物があり、それをチェーンやエージェントの下流コンポーネントではアクセス可能にしたいが、モデル自体には公開したくない場合**がある。
  - (うんうん、ありそう...!A/Bテストmetricsの実数値とか...!:thinking:)
  - ex. ツールがDocumentsのようなカスタムオブジェクトを返す場合、モデルに生の出力を渡さずに、この出力に関するビューやメタデータをモデルに渡したかったりする。

- ToolおよびToolMessageインターフェースは、**ツール出力のモデル向けの部分（これはToolMessage.contentです）と、モデル外で使用するための部分（ToolMessage.artifact）を区別する**ことを可能にする
  - toolが message contentと他のartifactsを区別可能にするには、toolを定義する際に`response_format="content_and_artifact"`を指定し、`(content, artifact)`のタプルを返すようにする必要がある。
    - 詳細はtoolのAPI referenceを参照
- 例:

```python
import random
from typing import List, Tuple
from langchain_core.tools import tool

@tool(response_format="content_and_artifact")
def generate_random_ints(min: int, max: int, size: int) -> Tuple[str, List[int]]:
    """Generate size random ints in the range [min, max]."""
    array = [random.randint(min, max) for _ in range(size)]
    content = f"Successfully generated array of {size} random ints in [{min}, {max}]."
    return content, array

# ツールを直接呼び出すと、出力のコンテンツ部分のみが返される
generate_random_ints.invoke({"min": 0, "max": 9, "size": 10})

>>> 'Successfully generated array of 10 random ints in [0, 9].'

# もしtoolをToolCall（tool-callingモデルによって生成されるもの）で呼び出すと、toolが生成したcontentとartifactの両方を含むToolMessageが返される
generate_random_ints.invoke(
    {
        "name": "generate_random_ints",
        "args": {"min": 0, "max": 9, "size": 10},
        "id": "123",  # required
        "type": "tool_call",  # required
    }
)

>>> ToolMessage(content='Successfully generated array of 10 random ints in [0, 9].', name='generate_random_ints', tool_call_id='123', artifact=[4, 8, 2, 4, 1, 0, 9, 5, 8, 1])
```

-
-
