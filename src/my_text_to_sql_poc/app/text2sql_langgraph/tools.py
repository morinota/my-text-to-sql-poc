from pathlib import Path
from typing import Annotated, Any, Callable, Iterator, Literal

import duckdb
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.docstore.document import Document
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import DuckDB
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_DB_PATH = "sample_vectorstore.duckdb"
TABLE_METADATA_DIR = Path("data/table_metadata/")
SAMPLE_QUERY_DIR = Path("data/sample_queries/")

PROMPT_CONFIG = OmegaConf.load("prompts/generate_sql_prompt_ver2_jp.yaml")

IntentType = Literal[
    "find_related_info",
    "generate_sql_query",
    "modify_sql_query",
]


class State(TypedDict):
    # add_messages reducer関数を指定しているので、上書きされずに追加される
    messages: Annotated[list[AnyMessage], add_messages]
    intent_type: Annotated[IntentType, Field(description="ユーザの意図タイプ")]


# 終了状態を表すツールを記述
class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="The final answer to the user")


class Text2SQL:
    config = {"configurable": {"thread_id": "1"}}

    def __init__(self) -> None:
        graph_builder = StateGraph(State)
        memory = MemorySaver()

        tools = [retrieve_related_tables, retrieve_related_sample_queries]
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.llm_with_RAG = self.llm.bind_tools(tools)

        graph_builder.add_node("tools", ToolNode(tools))
        graph_builder.add_node("query_generator", self._define_query_generator_node())
        graph_builder.add_node("query_checker", self._define_query_check_node())
        graph_builder.add_edge(START, "query_generator")
        graph_builder.add_conditional_edges(
            source="query_generator",
            path=tools_condition,
            path_map={"tools": "tools", END: END},
        )
        graph_builder.add_edge("query_generator", END)

        self.graph = graph_builder.compile(checkpointer=memory)

    def stream(self, question: str, intent_type: IntentType) -> Iterator[dict[str, Any]]:
        return self.graph.stream(
            {
                "messages": [("user", question)],
                "intent_type": intent_type,
            },
            config=self.config,
            stream_mode="values",
        )

    def _define_rag_node(self) -> Callable[State, State]:
        def rag_node(state: State) -> State:
            """RAGを使用して、質問に関連する情報を取得するノード"""
            related_tables = retrieve_related_tables.invoke(
                {"question": state["messages"][-1].content, "k": 10},
            )
            related_sample_queries = retrieve_related_sample_queries.invoke(
                {"question": state["messages"][-1].content, "k": 5},
            )
            message = f"related_tables: {related_tables}, related_sample_queries: {related_sample_queries}"
            return {"messages": [message]}

        return rag

    def _define_query_generator_node(self) -> Callable[State, State]:
        query_gen_prompt = ChatPromptTemplate.from_messages(

        def query_generator_node(state: State) -> State:
            """query_generatorノードは、メッセージを受け取り、llmを使用して応答を生成する"""
            response = self.llm.invoke(state["messages"])
            return {"messages": [response]}

        return query_generator_node

    def _define_query_check_node(self) -> Callable[State, State]:
        query_check_system = """
        あなたはSQLの専門家であり、注意深くSQLiteクエリを再確認する役割を持っています。以下の一般的なミスがないか確認してください：

        - NULL値を含むNOT INの使用
        - UNION ALLを使用すべき場面でUNIONを使用している
        - 排他的範囲に対してBETWEENを使用している
        - 条件式におけるデータ型の不一致
        - 識別子を適切に引用符で囲んでいるか
        - 関数に正しい数の引数を使用しているか
        - 正しいデータ型にキャストしているか
        - 結合に適切なカラムを使用しているか

        上記のいずれかのミスがあった場合は、クエリを修正してください。ミスがなければ、元のクエリをそのまま出力してください。
        """
        query_check_prompt = ChatPromptTemplate.from_messages(
            [("system", query_check_system), ("placeholder", "{messages}")]
        )
        query_check_pipeline = query_check_prompt | self.llm

        def query_check_node(state: State) -> State:
            """クエリをチェックするノード"""
            response = query_check_pipeline.invoke({"messages": state["messages"][-1]})
            return {"messages": [response]}

        return query_check_node


@tool
def retrieve_related_tables(question: str, k: int) -> dict[str, str]:
    """質問を回答するために、関連しそうなテーブルをretrieveして返す。
    Args:
        question (str): 質問
        k (int): 返り値のテーブル数
    Returns:
        dict[str, str]: key=テーブル名、value=テーブルのメタデータ
    """
    retrieved_table_names = [
        Path(doc.metadata["source"]).stem
        for doc in _retrieve_relevant_docs(question, table_name="table_embeddings", k=k)
    ]
    metadata_by_table = _load_selected_table_metadata(retrieved_table_names)
    return metadata_by_table


@tool
def retrieve_related_sample_queries(question: str, k: int) -> dict[str, str]:
    """質問に関連するサンプルクエリをretrieveして返す
    Args:
        question (str): 質問
        k (int): 返り値のクエリ数
    Returns:
        dict[str, str]: key=クエリ名、value=クエリのメタデータ
    """
    retrieved_query_names = [
        Path(doc.metadata["source"]).stem
        for doc in _retrieve_relevant_docs(question, table_name="query_embeddings", k=k)
    ]
    related_sample_queries = _load_selected_sample_queries(retrieved_query_names)
    return related_sample_queries


def _retrieve_relevant_docs(question: str, table_name: str, k: int = 5) -> list[Document]:
    """ベクトルストアを読み込み、質問に関連するドキュメントをretrieveする"""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    conn = duckdb.connect(database=VECTOR_DB_PATH)
    vectorstore = DuckDB(connection=conn, embedding=embeddings, table_name=table_name)
    return vectorstore.similarity_search(question, k=k)


def _load_selected_table_metadata(table_names: list[str]) -> dict[str, str]:
    """テーブルスメタデータを読み込んで、dict形式で返す"""
    metadata_by_table = {}
    available_tables = [file.stem for file in TABLE_METADATA_DIR.glob("*.txt")]

    for table_name in table_names:
        file_path = TABLE_METADATA_DIR / f"{table_name}.txt"
        if table_name not in available_tables or not file_path.exists():
            raise FileNotFoundError(
                f"Schema file not found for table: {table_name}\n Available tables: {available_tables}"
            )
        with file_path.open("r") as file:
            table_data = file.read()
            metadata_by_table[table_name] = table_data
    return metadata_by_table


def _load_selected_sample_queries(query_names: list[str]) -> dict[str, str]:
    """サンプルクエリを読み込んで、dict形式で返す"""
    sql_by_query_name = {}
    available_queries = [file.stem for file in SAMPLE_QUERY_DIR.glob("*.sql")]

    for query_name in query_names:
        file_path = SAMPLE_QUERY_DIR / f"{query_name}.sql"
        if query_name not in available_queries or not file_path.exists():
            raise FileNotFoundError(
                f"Sample query file not found for query: {query_name}\n Available queries: {available_queries}"
            )
        with file_path.open("r") as file:
            query_data = file.read()
            sql_by_query_name[query_name] = query_data
    return sql_by_query_name


if __name__ == "__main__":
    text2sql = Text2SQL()

    question = "直近1週間の記事のCTRの推移を知りたい。"
    events = text2sql.stream(question)
    for event in events:
        event["messages"][-1].pretty_print()
