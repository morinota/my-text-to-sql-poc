# How to create tools | 🦜️🔗 LangChain

# ツールの作成方法 | 🦜️🔗 LangChain

When constructing an agent, you will need to provide it with a list of Tools that it can use.
エージェントを構築する際には、エージェントが使用できるツールのリストを提供する必要があります。

Besides the actual function that is called, the Tool consists of several components:
呼び出される実際の関数に加えて、ツールは以下のいくつかのコンポーネントで構成されています。

| Attribute | Type | Description |
|-----------|------|-------------|
| name      | str  | Must be unique within a set of tools provided to an LLM or agent. |
| description | str | Describes what the tool does. Used as context by the LLM or agent. |
| args_schema | pydantic.BaseModel | Optional but recommended, and required if using callback handlers. It can be used to provide more information (e.g., few-shot examples) or validation for expected parameters. |
| return_direct | boolean | Only relevant for agents. When True, after invoking the given tool, the agent will stop and return the result directly to the user. |

LangChain supports the creation of tools from:  
LangChainは、以下からツールの作成をサポートしています：

- Functions;
- Functions;
- LangChain Runnables;
- LangChain Runnables;
- By sub-classing from BaseTool -- This is the most flexible method, it provides the largest degree of control, at the expense of more effort and code.  
- BaseToolからのサブクラス化 -- これは最も柔軟な方法であり、最大の制御を提供しますが、より多くの労力とコードが必要です。

Creating tools from functions may be sufficient for most use cases, and can be done via a simple @tool decorator.
関数からツールを作成することは、ほとんどのユースケースに対して十分であり、シンプルな@toolデコレーターを使用して行うことができます。

If more configuration is needed-- e.g., specification of both sync and async implementations-- one can also use the StructuredTool.from_function class method.
より多くの設定が必要な場合（例えば、同期および非同期の実装の両方の仕様など）、StructuredTool.from_functionクラスメソッドを使用することもできます。

In this guide we provide an overview of these methods.
このガイドでは、これらの方法の概要を提供します。

tip: Models will perform better if the tools have well chosen names, descriptions and JSON schemas.
ヒント: ツールに適切に選ばれた名前、説明、およびJSONスキーマがあると、モデルのパフォーマンスが向上します。

## Creating tools from functions

## 関数からツールを作成する

### @tool decorator

### @toolデコレーター

This @tool decorator is the simplest way to define a custom tool.
この@toolデコレーターは、カスタムツールを定義する最も簡単な方法です。

The decorator uses the function name as the tool name by default, but this can be overridden by passing a string as the first argument.
デコレーターは、デフォルトで関数名をツール名として使用しますが、最初の引数として文字列を渡すことで上書きできます。

Additionally, the decorator will use the function's docstring as the tool's description - so a docstring MUST be provided.
さらに、デコレーターは関数のドキュメンテーション文字列をツールの説明として使用します - したがって、ドキュメンテーション文字列は必ず提供する必要があります。

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Let's inspect some of the attributes associated with the tool.
print(multiply.name)
print(multiply.description)
print(multiply.args)
```

API Reference: tool
APIリファレンス: tool

```python
multiply
```

Multiply two numbers.
2つの数を掛け算します。

```python
{'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
```

Or create an async implementation, like this:
また、次のように非同期実装を作成できます：

```python
from langchain_core.tools import tool

@tool
async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

API Reference: tool
APIリファレンス: tool

Note that @tool supports parsing of annotations, nested schemas, and other features:
@toolはアノテーション、ネストされたスキーマ、およびその他の機能の解析をサポートしていることに注意してください：

```python
from typing import Annotated, List

@tool
def multiply_by_max(
    a: Annotated[str, "scale factor"],
    b: Annotated[List[int], "list of ints over which to take maximum"],
) -> int:
    """Multiply a by the maximum of b."""
    return a * max(b)
```

```python
multiply_by_max.args_schema.schema()
```

```json
{
    'description': 'Multiply a by the maximum of b.',
    'properties': {
        'a': {'description': 'scale factor', 'title': 'A', 'type': 'string'},
        'b': {'description': 'list of ints over which to take maximum', 'items': {'type': 'integer'}, 'title': 'B', 'type': 'array'}
    },
    'required': ['a', 'b'],
    'title': 'multiply_by_maxSchema',
    'type': 'object'
}
```

You can also customize the tool name and JSON args by passing them into the tool decorator.
ツール名とJSON引数をカスタマイズするために、ツールデコレーターに渡すこともできます。

```python
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool("multiplication-tool", args_schema=CalculatorInput, return_direct=True)
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Let's inspect some of the attributes associated with the tool.
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)
```

```python
multiplication-tool
```

Multiply two numbers.
2つの数を掛け算します。

```python
{'a': {'description': 'first number', 'title': 'A', 'type': 'integer'}, 'b': {'description': 'second number', 'title': 'B', 'type': 'integer'}}
```

True

```python
True
```

### Docstring parsing

### ドキュメンテーション文字列の解析

@tool can optionally parse Google Style docstrings and associate the docstring components (such as arg descriptions) to the relevant parts of the tool schema.
@toolはオプションでGoogleスタイルのドキュメンテーション文字列を解析し、ドキュメンテーション文字列のコンポーネント（引数の説明など）をツールスキーマの関連部分に関連付けることができます。

To toggle this behavior, specify parse_docstring:
この動作を切り替えるには、parse_docstringを指定します：

```python
@tool(parse_docstring=True)
def foo(bar: str, baz: int) -> str:
    """The foo.
    Args:
        bar: The bar.
        baz: The baz.
    """
    return bar
```

```python
foo.args_schema.schema()
```

```json
{
    'description': 'The foo.',
    'properties': {
        'bar': {'description': 'The bar.', 'title': 'Bar', 'type': 'string'},
        'baz': {'description': 'The baz.', 'title': 'Baz', 'type': 'integer'}
    },
    'required': ['bar', 'baz'],
    'title': 'fooSchema',
    'type': 'object'
}
```

### caution

### 注意

By default, @tool(parse_docstring=True) will raise ValueError if the docstring does not parse correctly.
デフォルトでは、@tool(parse_docstring=True)はドキュメンテーション文字列が正しく解析されない場合、ValueErrorを発生させます。

See API Reference for detail and examples.
詳細と例についてはAPIリファレンスを参照してください。

### StructuredTool

### StructuredTool

The StructuredTool.from_function class method provides a bit more configurability than the @tool decorator, without requiring much additional code.
StructuredTool.from_functionクラスメソッドは、@toolデコレーターよりも少し多くの設定を提供しますが、追加のコードはほとんど必要ありません。

```python
from langchain_core.tools import StructuredTool

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator = StructuredTool.from_function(func=multiply, coroutine=amultiply)

print(calculator.invoke({"a": 2, "b": 3}))
print(await calculator.ainvoke({"a": 2, "b": 5}))
```

API Reference: StructuredTool
APIリファレンス: StructuredTool

To configure it:
設定するには：

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

print(calculator.invoke({"a": 2, "b": 3}))
print(calculator.name)
print(calculator.description)
print(calculator.args)
```

```python
Calculator
```

multiply numbers
数を掛け算します。

```python
{'a': {'description': 'first number', 'title': 'A', 'type': 'integer'}, 'b': {'description': 'second number', 'title': 'B', 'type': 'integer'}}
```

### Creating tools from Runnables

### Runnablesからツールを作成する

LangChain Runnables that accept string or dict input can be converted to tools using the as_tool method, which allows for the specification of names, descriptions, and additional schema information for arguments.
文字列または辞書入力を受け入れるLangChain Runnablesは、as_toolメソッドを使用してツールに変換でき、名前、説明、および引数の追加スキーマ情報を指定できます。

Example usage:
使用例：

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
```

API Reference: GenericFakeChatModel | StrOutputParser | ChatPromptTemplate
APIリファレンス: GenericFakeChatModel | StrOutputParser | ChatPromptTemplate

```python
/var/folders/4j/2rz3865x6qg07tx43146py8h0000gn/T/ipykernel_95770/2548361071.py:14: LangChainBetaWarning: This API is in beta and may change in the future.  as_tool = chain.as_tool(
```

```python
{'answer_style': {'title': 'Answer Style', 'type': 'string'}}
```

See this guide for more detail.
このガイドで詳細を確認してください。

### Subclass BaseTool

### BaseToolをサブクラス化する

You can define a custom tool by sub-classing from BaseTool.
BaseToolからサブクラス化することで、カスタムツールを定義できます。

This provides maximal control over the tool definition, but requires writing more code.
これにより、ツール定義に対する最大の制御が提供されますが、より多くのコードを書く必要があります。

```python
from typing import Optional, Type
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class CustomCalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "useful for when you need to answer questions about math"
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
        return self._run(a, b, run_manager=run_manager.get_sync())
```

API Reference: AsyncCallbackManagerForToolRun | CallbackManagerForToolRun | BaseTool
APIリファレンス: AsyncCallbackManagerForToolRun | CallbackManagerForToolRun | BaseTool

```python
multiply = CustomCalculatorTool()
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)
print(multiply.invoke({"a": 2, "b": 3}))
print(await multiply.ainvoke({"a": 2, "b": 3}))
```

```python
Calculator
```

useful for when you need to answer questions about math
数学に関する質問に答える必要があるときに便利です。

```python
{'a': {'description': 'first number', 'title': 'A', 'type': 'integer'}, 'b': {'description': 'second number', 'title': 'B', 'type': 'integer'}}
```

True

```python
True
```

66

```python
66
```

### How to create async tools

### 非同期ツールの作成方法

LangChain Tools implement the Runnable interface 🏃.
LangChainツールはRunnableインターフェースを実装しています🏃。

All Runnables expose the invoke and ainvoke methods (as well as other methods like batch, abatch, astream etc).
すべてのRunnableはinvokeおよびainvokeメソッド（およびbatch、abatch、astreamなどの他のメソッド）を公開します。

So even if you only provide a sync implementation of a tool, you could still use the ainvoke interface, but there are some important things to know:
したがって、ツールの同期実装のみを提供しても、ainvokeインターフェースを使用できますが、知っておくべき重要なことがあります：

LangChain's by default provides an async implementation that assumes that the function is expensive to compute, so it'll delegate execution to another thread.
LangChainはデフォルトで、関数の計算にコストがかかると仮定して非同期実装を提供しており、そのため、実行を別のスレッドに委任します。

If you're working in an async codebase, you should create async tools rather than sync tools, to avoid incurring a small overhead due to that thread.
非同期コードベースで作業している場合は、そのスレッドによるわずかなオーバーヘッドを回避するために、同期ツールではなく非同期ツールを作成する必要があります。

```python

If you need both sync and async implementations, use StructuredTool.from_function or sub-class from BaseTool.
同期および非同期の両方の実装が必要な場合は、StructuredTool.from_functionを使用するか、BaseToolからサブクラス化してください。

If implementing both sync and async, and the sync code is fast to run, override the default LangChain async implementation and simply call the sync code.
同期と非同期の両方を実装する場合、かつ同期コードが高速で実行される場合は、デフォルトのLangChain非同期実装をオーバーライドし、単に同期コードを呼び出してください。

You CANNOT and SHOULD NOT use the sync invoke with an async tool.
非同期ツールに対して同期invokeを使用することはできず、使用すべきではありません。

```python
from langchain_core.tools import StructuredTool

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator = StructuredTool.from_function(func=multiply)

print(calculator.invoke({"a": 2, "b": 3}))
print(await calculator.ainvoke({"a": 2, "b": 5}))  # Uses default LangChain async implementation incurs small overhead
```

API Reference: StructuredTool
APIリファレンス: StructuredTool

```python
610
```

```python
610
```

```python
from langchain_core.tools import StructuredTool

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

async def amultiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator = StructuredTool.from_function(func=multiply, coroutine=amultiply)

print(calculator.invoke({"a": 2, "b": 3}))
print(await calculator.ainvoke({"a": 2, "b": 5}))  # Uses use provided amultiply without additional overhead
```

API Reference: StructuredTool
APIリファレンス: StructuredTool

```python
610
```

```python
610
```

You should not and cannot use .invoke when providing only an async definition.
非同期定義のみを提供する場合、.invokeを使用すべきではなく、使用できません。

```python
@tool
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

try:
    multiply.invoke({"a": 2, "b": 3})
except NotImplementedError:
    print("Raised not implemented error. You should not be doing this.")
```

Raised not implemented error. You should not be doing this.

```python
実装されていないエラーが発生しました。これを行うべきではありません。
```

### Handling Tool Errors

### ツールエラーの処理

If you're using tools with agents, you will likely need an error handling strategy, so the agent can recover from the error and continue execution.
エージェントとツールを使用している場合、エージェントがエラーから回復し、実行を続けることができるように、エラー処理戦略が必要になるでしょう。

A simple strategy is to throw a ToolException from inside the tool and specify an error handler using handle_tool_error.
シンプルな戦略は、ツール内からToolExceptionをスローし、handle_tool_errorを使用してエラーハンドラーを指定することです。

When the error handler is specified, the exception will be caught and the error handler will decide which output to return from the tool.
エラーハンドラーが指定されると、例外がキャッチされ、エラーハンドラーがツールから返す出力を決定します。

You can set handle_tool_error to True, a string value, or a function.
handle_tool_errorをTrue、文字列値、または関数に設定できます。

If it's a function, the function should take a ToolException as a parameter and return a value.
関数の場合、その関数はToolExceptionをパラメータとして受け取り、値を返す必要があります。

Please note that only raising a ToolException won't be effective.
ToolExceptionをスローするだけでは効果がありません。

You need to first set the handle_tool_error of the tool because its default value is False.
ツールのhandle_tool_errorを最初に設定する必要があります。デフォルト値はFalseです。

```python
from langchain_core.tools import ToolException

def get_weather(city: str) -> int:
    """Get weather for the given city."""
    raise ToolException(f"Error: There is no city by the name of {city}.")
```

API Reference: ToolException
APIリファレンス: ToolException

Here's an example with the default handle_tool_error=True behavior.
デフォルトのhandle_tool_error=Trueの動作の例です。

```python
get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    handle_tool_error=True,
)

get_weather_tool.invoke({"city": "foobar"})
```

```python
'Error: There is no city by the name of foobar.'
```

We can set handle_tool_error to a string that will always be returned.
handle_tool_errorを常に返される文字列に設定できます。

```python
get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    handle_tool_error="There is no such city, but it's probably above 0K there!",
)

get_weather_tool.invoke({"city": "foobar"})
```

```python
"There is no such city, but it's probably above 0K there!"
```

Handling the error using a function:
関数を使用してエラーを処理します：

```python
def _handle_error(error: ToolException) -> str:
    return f"The following errors occurred during tool execution: `{error.args[0]}`"

get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    handle_tool_error=_handle_error,
)

get_weather_tool.invoke({"city": "foobar"})
```

```python
'The following errors occurred during tool execution: `Error: There is no city by the name of foobar.`'
```

### Returning artifacts of Tool execution

### ツール実行の成果物を返す

Sometimes there are artifacts of a tool's execution that we want to make accessible to downstream components in our chain or agent, but that we don't want to expose to the model itself.
時には、ツールの実行の成果物があり、それをチェーンやエージェントの下流コンポーネントにアクセス可能にしたいが、モデル自体には公開したくない場合があります。

For example if a tool returns custom objects like Documents, we may want to pass some view or metadata about this output to the model without passing the raw output to the model.
例えば、ツールがDocumentsのようなカスタムオブジェクトを返す場合、モデルに生の出力を渡さずに、この出力に関するビューやメタデータをモデルに渡したい場合があります。

At the same time, we may want to be able to access this full output elsewhere, for example in downstream tools.
同時に、他の場所、例えば下流のツールでこの完全な出力にアクセスできるようにしたい場合があります。

The Tool and ToolMessage interfaces make it possible to distinguish between the parts of the tool output meant for the model (this is the ToolMessage.content) and those parts which are meant for use outside the model (ToolMessage.artifact).
ToolおよびToolMessageインターフェースは、ツール出力のモデル向けの部分（これはToolMessage.contentです）と、モデル外で使用するための部分（ToolMessage.artifact）を区別することを可能にします。

Requires langchain-core >= 0.2.19
この機能はlangchain-core == 0.2.19で追加されました。パッケージが最新であることを確認してください。

If we want our tool to distinguish between message content and other artifacts, we need to specify response_format="content_and_artifact" when defining our tool and make sure that we return a tuple of (content, artifact):
ツールがメッセージコンテンツと他の成果物を区別できるようにするには、ツールを定義する際にresponse_format="content_and_artifact"を指定し、(content, artifact)のタプルを返すようにする必要があります。

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
```

API Reference: tool
APIリファレンス: tool

If we invoke our tool directly with the tool arguments, we'll get back just the content part of the output:
ツール引数でツールを直接呼び出すと、出力のコンテンツ部分のみが返されます：

```python
generate_random_ints.invoke({"min": 0, "max": 9, "size": 10})
```

```python
'Successfully generated array of 10 random ints in [0, 9].'
```

If we invoke our tool with a ToolCall (like the ones generated by tool-calling models), we'll get back a ToolMessage that contains both the content and artifact generated by the Tool:
ツールをToolCall（ツール呼び出しモデルによって生成されるもの）で呼び出すと、ツールによって生成されたコンテンツと成果物の両方を含むToolMessageが返されます：

```python
generate_random_ints.invoke(
    {
        "name": "generate_random_ints",
        "args": {"min": 0, "max": 9, "size": 10},
        "id": "123",  # required
        "type": "tool_call",  # required
    }
)
```

```python
ToolMessage(content='Successfully generated array of 10 random ints in [0, 9].', name='generate_random_ints', tool_call_id='123', artifact=[4, 8, 2, 4, 1, 0, 9, 5, 8, 1])
```

We can do the same when subclassing BaseTool:
BaseToolをサブクラス化する際にも同様のことができます：

```python
from langchain_core.tools import BaseTool

class GenerateRandomFloats(BaseTool):
    name: str = "generate_random_floats"
    description: str = "Generate size random floats in the range [min, max]."
    response_format: str = "content_and_artifact"
    ndigits: int = 2

    def _run(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
        range_ = max - min
        array = [
            round(min + (range_ * random.random()), ndigits=self.ndigits)
            for _ in range(size)
        ]
        content = f"Generated {size} floats in [{min}, {max}], rounded to {self.ndigits} decimals."
        return content, array

    # Optionally define an equivalent async method
    # async def _arun(self, min: float, max: float, size: int) -> Tuple[str, List[float]]:
    #     ...
```

API Reference: BaseTool
APIリファレンス: BaseTool

```python
rand_gen = GenerateRandomFloats(ndigits=4)

rand_gen.invoke(
    {
        "name": "generate_random_floats",
        "args": {"min": 0.1, "max": 3.3333, "size": 3},
        "id": "123",
        "type": "tool_call",
    }
)
```

```python
ToolMessage(content='Generated 3 floats in [0.1, 3.3333], rounded to 4 decimals.', name='generate_random_floats', tool_call_id='123', artifact=[1.5566, 0.5134, 2.7914])
```

Edit this page
このページを編集

Was this page helpful?
このページは役に立ちましたか？

Previous
前

Custom Retriever
カスタムリトリーバー

Next
次

How to debug your LLM apps
LLMアプリをデバッグする方法

```
