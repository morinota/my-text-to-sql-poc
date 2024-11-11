from typing import Any

from langchain_community.tools import TavilySearchResults
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from omegaconf import OmegaConf

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
search = TavilySearchResults(max_results=2)

# == load the prompt from the config ==
config = OmegaConf.load("./src/my_text_to_sql_poc/app/ai_agent_sample/prompts.yaml")

chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI bot. Your name is {name}."),
        ("human", "Hello, how are you doing?"),
        ("ai", "I'm doing well, thanks!"),
        ("human", "{user_input}"),
    ]
)
sample_prompt = chat_template.format_messages(name="Bob", user_input="What is your name?")

writer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", config.writer_prompt.messages[0].content),
        ("human", config.writer_prompt.messages[1].content),
    ]
)
reviewer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", config.reviewer_prompt.messages[0].content),
        ("human", config.reviewer_prompt.messages[1].content),
    ]
)


# === Define the chain ===


def get_search_results(inputs: dict[str, Any]) -> Any:
    if "search_results" in inputs:
        return inputs["search_results"]
    return search.run(inputs["input"])


## このパイプでつなげた記法は、LCEL(LangChain Expression Language)と呼ばれる記法。
## パイプの前から後に入出力が渡される。
## この一連の動作フローをchainと呼ぶ。
writer_chain = (
    {
        "input": lambda x: x["input"],
        "search_results": get_search_results,
        "review": lambda x: x.get("review", "初回の記事作成のため、レビューはありません。"),
    }
    | writer_prompt
    | llm
    | StrOutputParser()
)

reviewer_chain = reviewer_prompt | llm | StrOutputParser()


def run_blog_creation_process(topic: str) -> tuple[str, str]:
    """実行ワークフローを定義
    - 上記chainを使って、while文で定量評価が8点以上になるまで、
    - ブログ内容とレビュー内容と二つのエージェントに受け渡してブラッシュアップと執筆を繰り返させる
    """
    search_results = search.run(topic)
    blog_content = writer_chain.invoke({"input": topic, "search_results": search_results})
    logger.debug(f"blog_content: {blog_content}")

    review = reviewer_chain.invoke({"blog_content": blog_content})
    logger.debug(f"review: {review}")

    score = parse_score(review)
    logger.debug(f"score: {score}")

    while score <= 7:
        blog_content = writer_chain.invoke({"input": topic, "search_results": search_results, "review": review})
        review = reviewer_chain.invoke({"blog_content": blog_content})
        score = parse_score(review)

    print(f"最終スコア: {score}")
    return blog_content, review


def parse_score(review: str) -> float:
    """reviewの文字列の中から「総合評価: 7.5/10」という形式で書かれたレビューから、スコアを取得する"""
    score_str = review.split("総合評価: ")[1].split("/10")[0]
    return float(score_str)


topic = "A/Bテストの分析時に注意すべき観点について、技術ブログを書いてください。"
final_blog, final_review = run_blog_creation_process(topic)

# final_blog, final_reviewをtxt形式で保存する
with open("blog.txt", "w") as f:
    f.write(final_blog)

with open("review.txt", "w") as f:
    f.write(final_review)
