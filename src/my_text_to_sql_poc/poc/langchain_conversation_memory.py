from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

memory = ConversationBufferMemory()
memory.save_context(
    inputs={"input": "マッチョとは何ですか？"},
    outputs={"output": "男性の強靱さを表す思想や行動を指す言葉です"},
)
memory.save_context(inputs={"input": "どんな人がマッチョですか？"}, outputs={"output": "筋肉質で、男らしい人"})
print(memory.load_memory_variables({}))
