## Defining Custom Tools | 🦜️🔗 LangChain

Defining Custom Tools
カスタムツールの定義

When constructing your own agent, you will need to provide it with a list of Tools that it can use.
独自のエージェントを構築する際には、エージェントが使用できるツールのリストを提供する必要があります。

Besides the actual function that is called, the Tool consists of several components:
呼び出される実際の関数に加えて、ツールは以下のいくつかのコンポーネントで構成されています。

- name (str), is required and must be unique within a set of tools provided to an agent
- name (str)：必須であり、エージェントに提供されるツールのセット内で一意でなければなりません。

- description (str), is optional but recommended, as it is used by an agent to determine tool use
- description (str)：オプションですが推奨されます。エージェントがツールの使用を判断するために使用されます。

- args_schema (Pydantic BaseModel), is optional but recommended, can be used to provide more information (e.g., few-shot examples) or validation for expected parameters.
- args_schema (Pydantic BaseModel)：オプションですが推奨されます。追加情報（例：少数ショットの例）や期待されるパラメータの検証を提供するために使用できます。

There are multiple ways to define a tool. In this guide, we will walk through how to do for two functions:
ツールを定義する方法はいくつかあります。このガイドでは、2つの関数の定義方法を説明します。

- A made up search function that always returns the string "LangChain"
- 常に文字列「LangChain」を返す架空の検索関数

- A multiplier function that will multiply two numbers by each other
- 2つの数を掛け算する乗算関数

The biggest difference here is that the first function only requires one input, while the second one requires multiple.
ここでの最大の違いは、最初の関数は1つの入力のみを必要とするのに対し、2番目の関数は複数の入力を必要とすることです。

Many agents only work with functions that require single inputs, so it's important to know how to work with those.
多くのエージェントは単一の入力を必要とする関数でのみ動作するため、それらを扱う方法を知っておくことが重要です。

For the most part, defining these custom tools is the same, but there are some differences.
ほとんどの場合、これらのカスタムツールを定義することは同じですが、いくつかの違いがあります。

# Import things that are needed generically

# 一般的に必要なものをインポートする

```python
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
```

API Reference:
APIリファレンス：

BaseTool
BaseTool

StructuredTool
StructuredTool

tool
tool

@tool decorator
この @tool デコレーターは、カスタムツールを定義する最も簡単な方法です。

The decorator uses the function name as the tool name by default, but this can be overridden by passing a string as the first argument.
デコレーターは、デフォルトで関数名をツール名として使用しますが、最初の引数として文字列を渡すことで上書きできます。

Additionally, the decorator will use the function's docstring as the tool's description - so a docstring MUST be provided.
さらに、デコレーターは関数のドキュメンテーション文字列をツールの説明として使用します。したがって、ドキュメンテーション文字列は必ず提供する必要があります。

```python
@tool
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"
```

print(search.name)
print(search.description)
print(search.args)

```python
search
search(query: str) -> str - Look up things online.
{'query': {'title': 'Query', 'type': 'string'}}
```

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

print(multiply.name)
print(multiply.description)
print(multiply.args)

```python
multiply
multiply(a: int, b: int) -> int - Multiply two numbers.
{'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
```

You can also customize the tool name and JSON args by passing them into the tool decorator.
ツール名やJSON引数をカスタマイズするために、ツールデコレーターに渡すこともできます。

```python
class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")
```

```python
@tool("search-tool", args_schema=SearchInput, return_direct=True)
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"
```

print(search.name)
print(search.description)
print(search.args)
print(search.return_direct)

```python
search-tool
search-tool(query: str) -> str - Look up things online.
{'query': {'title': 'Query', 'description': 'should be a search query', 'type': 'string'}}
True
```

Subclass BaseTool
BaseToolをサブクラス化する

You can also explicitly define a custom tool by subclassing the BaseTool class.
BaseToolクラスをサブクラス化することで、カスタムツールを明示的に定義することもできます。

This provides maximal control over the tool definition, but is a bit more work.
これにより、ツール定義に対する最大の制御が提供されますが、少し手間がかかります。

```python
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
```

```python
class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

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
```

```python
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
```

API Reference:
APIリファレンス：

AsyncCallbackManagerForToolRun
AsyncCallbackManagerForToolRun

CallbackManagerForToolRun
CallbackManagerForToolRun

```python
search = CustomSearchTool()
print(search.name)
print(search.description)
print(search.args)
```

```python
custom_search
useful for when you need to answer questions about current events
{'query': {'title': 'Query', 'description': 'should be a search query', 'type': 'string'}}
```

```python
multiply = CustomCalculatorTool()
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)
```

```python
Calculator
useful for when you need to answer questions about math
{'a': {'title': 'A', 'description': 'first number', 'type': 'integer'}, 'b': {'title': 'B', 'description': 'second number', 'type': 'integer'}}
True
```

StructuredTool dataclass
StructuredToolデータクラス

You can also use a StructuredTool dataclass.
StructuredToolデータクラスを使用することもできます。

This methods is a mix between the previous two.
この方法は、前の2つの混合です。

It's more convenient than inheriting from the BaseTool class, but provides more functionality than just using a decorator.
BaseToolクラスを継承するよりも便利ですが、デコレーターを使用するだけよりも多くの機能を提供します。

```python
def search_function(query: str):
    return "LangChain"
```

```python
search = StructuredTool.from_function(
    func=search_function,
    name="Search",
    description="useful for when you need to answer questions about current events",
    # coroutine= ... <- you can specify an async method if desired as well
)
```

print(search.name)
print(search.description)
print(search.args)

```python
Search
Search(query: str) - useful for when you need to answer questions about current events
{'query': {'title': 'Query', 'type': 'string'}}
```

You can also define a custom args_schema to provide more information about inputs.
カスタムargs_schemaを定義して、入力に関する詳細情報を提供することもできます。

```python
class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")
```

```python
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

```python
calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True,
    # coroutine= ... <- you can specify an async method if desired as well
)
```

print(calculator.name)
print(calculator.description)
print(calculator.args)

```python
Calculator
Calculator(a: int, b: int) -> int - multiply numbers
{'a': {'title': 'A', 'description': 'first number', 'type': 'integer'}, 'b': {'title': 'B', 'description': 'second number', 'type': 'integer'}}
```

Handling Tool Errors
ツールエラーの処理

When a tool encounters an error and the exception is not caught, the agent will stop executing.
ツールがエラーに遭遇し、例外がキャッチされない場合、エージェントは実行を停止します。

If you want the agent to continue execution, you can raise a ToolException and set handle_tool_error accordingly.
エージェントに実行を続けさせたい場合は、ToolExceptionを発生させ、handle_tool_errorを適切に設定できます。

When ToolException is thrown, the agent will not stop working, but will handle the exception according to the handle_tool_error variable of the tool, and the processing result will be returned to the agent as observation, and printed in red.
ToolExceptionがスローされると、エージェントは作業を停止せず、ツールのhandle_tool_error変数に従って例外を処理し、処理結果が観察としてエージェントに返され、赤色で印刷されます。

You can set handle_tool_error to True, set it a unified string value, or set it as a function.
handle_tool_errorをTrueに設定したり、統一された文字列値を設定したり、関数として設定することができます。

If it's set as a function, the function should take a ToolException as a parameter and return a str value.
関数として設定されている場合、その関数はToolExceptionをパラメータとして受け取り、str値を返す必要があります。

Please note that only raising a ToolException won't be effective.
ToolExceptionを発生させるだけでは効果がありません。

You need to first set the handle_tool_error of the tool because its default value is False.
ツールのhandle_tool_errorを最初に設定する必要があります。デフォルト値はFalseです。

```python
from langchain_core.tools import ToolException

def search_tool1(s: str):
    raise ToolException("The search tool1 is not available.")
```

API Reference:
APIリファレンス：

ToolException

First, let's see what happens if we don't set handle_tool_error - it will error.
まず、handle_tool_errorを設定しない場合に何が起こるか見てみましょう - エラーが発生します。

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
)
search.run("test")
```

```
---------------------------------------------------------------------------

ToolException                             Traceback (most recent call last)

```

```
Cell In[58], line 7
     1 search = StructuredTool.from_function(
     2     func=search_tool1,
     3     name="Search_tool1",
     4     description=description,
     5 )
----> 7 search.run("test")

```

```
File ~/workplace/langchain/libs/core/langchain_core/tools.py:344, in BaseTool.run(self, tool_input, verbose, start_color, color, callbacks, tags, metadata, run_name, **kwargs)
    342 if not self.handle_tool_error:
    343     run_manager.on_tool_error(e)
--> 344     raise e
    345 elif isinstance(self.handle_tool_error, bool):
    346     if e.args:
```

```
File ~/workplace/langchain/libs/core/langchain_core/tools.py:337, in BaseTool.run(self, tool_input, verbose, start_color, color, callbacks, tags, metadata, run_name, **kwargs)
    334 try:
    335     tool_args, tool_kwargs = self._to_args_and_kwargs(parsed_input)
    336     observation = (
--> 337         self._run(*tool_args, run_manager=run_manager, **tool_kwargs)
    338         if new_arg_supported
    339         else self._run(*tool_args, **tool_kwargs)
    340     )
    341 except ToolException as e:
    342     if not self.handle_tool_error:
```

```
File ~/workplace/langchain/libs/core/langchain_core/tools.py:631, in StructuredTool._run(self, run_manager, *args, **kwargs)
    622 if self.func:
    623     new_argument_supported = signature(self.func).parameters.get("callbacks")
    624     return (
    625         self.func(
    626             *args,
    627             callbacks=run_manager.get_child() if run_manager else None,
    628             **kwargs,
    629         )
    630         if new_argument_supported
--> 631         else self.func(*args, **kwargs)
    632     )
    633 raise NotImplementedError("Tool does not support sync")
```

```
Cell In[55], line 5, in search_tool1(s)
      4 def search_tool1(s: str):
----> 5     raise ToolException("The search tool1 is not available.")
```

```
ToolException: The search tool1 is not available.
```

Now, let's set handle_tool_error to be True
次に、handle_tool_errorをTrueに設定してみましょう。

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=True,
)
search.run("test")
```

```
'The search tool1 is not available.'
```

We can also define a custom way to handle the tool error
ツールエラーを処理するカスタム方法を定義することもできます。

```python
def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )
```

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=_handle_error,
)
search.run("test")
```

```
'The following errors occurred during tool execution:The search tool1 is not available.Please try another tool.'
```

Help us out by providing feedback on this documentation page:
このドキュメントページにフィードバックを提供してください：

Previous
前へ

Tools
ツール

Next
次へ

Tools as OpenAI Functions
OpenAI関数としてのツール

@tool decorator
@toolデコレーター

Subclass BaseTool
BaseToolをサブクラス化する

StructuredTool dataclass
StructuredToolデータクラス

Handling Tool Errors
ツールエラーの処理

Community
コミュニティ

Discord
Discord

Twitter
Twitter

GitHub
GitHub

Python
Python

JS/TS
JS/TS

More
もっと

Homepage
ホームページ

Blog
ブログ

YouTube
YouTube

Copyright © 2024 LangChain, Inc.
著作権 © 2024 LangChain, Inc.

```
