from typing import Sequence

from langchain import hub
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DuckDB
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, TypedDict


def prepare_dummy_data() -> None:
    # ダミーデータ作成
    research_texts = [
        "研究レポート：新しいAIモデルが画像認識精度を98%に向上させた結果",
        "学術論文サマリー：自然言語処理分野でTransformerが主流アーキテクチャになった理由",
        "量子コンピューティングによる機械学習手法の最新動向",
    ]
    development_texts = [
        "プロジェクトA：UIデザイン完了、API統合中",
        "プロジェクトB：新機能Xテスト中、バグ修正必要",
        "製品Y：リリース前のパフォーマンス最適化段階",
    ]

    # テキストをベクトルDBに保存
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    research_docs = splitter.create_documents(research_texts)
    development_docs = splitter.create_documents(development_texts)
    embeddings = OpenAIEmbeddings()
    research_vectorstore = DuckDB.from_documents(
        documents=research_docs, embeddings=embeddings, collec
    )
