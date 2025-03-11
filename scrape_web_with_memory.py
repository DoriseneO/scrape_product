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
from langgraph.graph import START, StateGraph,END
from typing_extensions import Annotated, List, TypedDict
from langgraph.checkpoint.memory import MemorySaver

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

splitter = RecursiveCharacterTextSplitter(chunk_size= 1000,chunk_overlap =0)
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
#define stategraph

class State(TypedDict):
    content: list[Document]
    query: str
    answer: str

def retrieval_node(state: State):
    retrieve_response = vector_store.similarity_search(state["query"],k=5)
    # print(f"retrieved_response: {retrieve_response}")
    return {"content": retrieve_response}


def generate_node(state:State):
    generated_response = [doc.page_content for doc in state["content"]]
    # print(f"generated_response:  {generated_response}")
    return {"answer": generated_response}


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

graph_builder = StateGraph(State)  
graph_builder.add_node("retrieve", retrieval_node)
graph_builder.add_node("generate", generate_node)
graph_builder.set_entry_point( "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

 # Specify an ID for the thread
config = {"configurable": {"thread_id": "abc123"}}

while True:
    query = input("ask me anything \nUser: ")
    if query == 'quit':
        print("Goodbye!")
        break
    
    initial_state = State(content=[], query=query, answer="")

     # Run the graph
    final_state = graph.invoke(initial_state,config)

     # Format the prompt with the final state
    llm_format = conversational_prompt.invoke({"content": final_state["answer"], "user_query": final_state["query"]})

    output_parser = StrOutputParser()
    
    # Generate the response
    llm_response = output_parser.invoke(llm_model.invoke(llm_format))
    print(f"AI: {llm_response}")