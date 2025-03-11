from bs4 import BeautifulSoup
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import bs4
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from typing import List

from langchain_community.vectorstores import Chroma

# Load .env file
load_dotenv()
USER_AGENT = os.getenv("USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

url = ("https://iamdoris.com/")
print(f"the url: {url}")
loader = WebBaseLoader(url, bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("blocks")
        )
    ), requests_kwargs={
    "headers": {
        "User-Agent": USER_AGENT,
    }
})
docs = loader.load()
# print(f"doc: {docs}")

splitter = RecursiveCharacterTextSplitter(chunk_size= 500,chunk_overlap =0)
text_split = splitter.split_documents(docs)
# print(f"splitter: {splitter}")

embeddings =OpenAIEmbeddings(model="text-embedding-3-small")
# print(f"embed: {embeddings}")

vector_store = Chroma.from_documents(
    documents= text_split,
    embedding=embeddings
)
stored_vector = vector_store.add_documents(documents=text_split)
# print(f"vector_store: {stored_vector}")

#RAG 

def retrieval_node(query:str):
    retrieve_response = vector_store.similarity_search(query,k=2)
    # print(f"retrieved_response: {retrieve_response}")
    return retrieve_response


def generate_node(retrieve_response:list):
    generated_response = [doc.page_content for doc in retrieve_response]
    # print(f"generated_response:  {generated_response}")
    return generated_response


llm_model = ChatOpenAI(model="gpt-4o-mini")

conversational_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "You are an AI assistant. Retrieve the relevant documents based on the query and use them to answer the question. "
             "get answers from the vector store and provide response"
             "you are to provide response from the scrapped website"
             "{content}"
             "If the information is insufficient, respond with 'can you be more specific and provide more details.'"),
            ("human", "{user_query}")
        ]
    )


while True:
    query = input("ask me anything \nUser: ")
    if query == 'quit':
        print("Goodbye!")
        break
    vector_response = retrieval_node(query)
    generated_Ai = generate_node(vector_response)
    llm_format = conversational_prompt.format(content =generated_Ai, user_query= vector_response)
    output_parser = StrOutputParser()
    llm = llm_model.invoke(llm_format)
    llm_response = output_parser.invoke(llm)
    print(f"Ai: {llm_response}")

