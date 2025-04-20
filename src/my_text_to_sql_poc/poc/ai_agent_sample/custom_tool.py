import random

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


@tool(response_format="content_and_artifact")
def generate_random_ints(min: int, max: int, size: int) -> tuple[str, list[int]]:
    """Generate size random ints in the range [min, max]."""
    array = [random.randint(min, max) for _ in range(size)]
    content = f"Successfully generated array of {size} random ints in [{min}, {max}]."
    return content, array


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


@tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def add_all(numbers: list[int]) -> int:
    """Add all numbers"""
    return sum(numbers)


tool_list = [generate_random_ints, add_all]

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tool_list)

ai_msg = llm_with_tools.invoke("25未満のランダムな正の整数を10個生成して、それら全てを足し算した結果を出力して")

print(f"{ai_msg.content=}")
print(f"{ai_msg.tool_calls=}")

# ツールの呼び出し
result = generate_random_ints.invoke(
    {"name": "generate_random_ints", "args": {"min": 1, "max": 10, "size": 5}, "id": "123", "type": "tool_call"}
)
# アーティファクトの取り出し
artifact = result.artifact

# 後続のツールでartifactを使用
processed_result = add_all.invoke(artifact)
print(processed_result)
