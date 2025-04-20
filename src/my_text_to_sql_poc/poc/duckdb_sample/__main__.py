import duckdb
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import DuckDB
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from tiktoken import encoding_for_model

EMBEDDING_MODEL_NAME = "text-embedding-3-small"
PRICE_DOLLAR_PER_1K_TOKENS = 0.00002
# 埋め込みモデルAPIについて
## 1536次元, dimensionsパラメータを指定して、次元数を小さくすることも可能。
## 利用料金はinput tokens数によって決まる。
### 1ドルあたり62,500ページのテキストを処理できる
### -> 1ページを800トークンとすると、1ドルで62,500*800 = 50 mil tokensを処理できる
### -> よって1000トークンあたりの金額は 1,000/50 million = 0.00002

# 埋め込みを永続化するための設定
db_path = "sample_database.duckdb"
connection = duckdb.connect(database=db_path)

loader = DirectoryLoader("data/summarized_schema/", glob="*.txt")  # *.txt でテキストファイルのみを指定
documents = loader.load()

documents = CharacterTextSplitter().split_documents(documents)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)

# トークン数を計算
encoding = encoding_for_model(EMBEDDING_MODEL_NAME)
total_tokens = sum(len(encoding.encode(doc.page_content)) for doc in documents)
# 利用料金を計算
cost = (total_tokens / 1000) * PRICE_DOLLAR_PER_1K_TOKENS
print(f"Total tokens: {total_tokens}")
print(f"Estimated cost: ${cost:.4f}")

# NOTE: LangchainのDuckDB wrapperが、テーブルスキーマを自動生成して
docsearch = DuckDB.from_documents(documents, embeddings, connection=connection)

query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(query)

print(docs[0].page_content)
print(len(docs))
