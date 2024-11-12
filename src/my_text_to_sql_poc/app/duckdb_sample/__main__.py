from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import DuckDB
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("state_of_the_union.txt")
documents = loader.load()

documents = CharacterTextSplitter().split_documents(documents)
embeddings = OpenAIEmbeddings()

docsearch = DuckDB.from_documents(documents, embeddings)

query = "What did the president say about Ketanji Brown Jackson"
docs = docsearch.similarity_search(query)

print(docs[0].page_content)
