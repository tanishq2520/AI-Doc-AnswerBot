import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

openai_api_key = 'api_key'

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.7,
    max_tokens=500,
    api_key=openai_api_key
)

memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=500
)

embeddings = OpenAIEmbeddings(api_key=openai_api_key)

vector_db = Chroma(embedding_function=embeddings, collection_name="my_collection", persist_directory="./my_chroma_db")

retriever = ContextualCompressionRetriever(
    base_compressor=LLMChainExtractor.from_llm(llm),
    base_retriever=vector_db.as_retriever()
)

prompt_template = ChatPromptTemplate.from_template("""\
    Context: {context}
    Chat History: {chat_history}
    Human: {question}
    AI: Please provide a relevant answer based on the context and chat history.
""")

conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": prompt_template}
)

def chatbot_response(user_input):
    return conversation_chain.invoke({"question": user_input})["answer"]
