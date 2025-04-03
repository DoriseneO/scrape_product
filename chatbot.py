
# ✅ Answer common questions 
# ✅ Maintain conversation state across calls
# ✅ Route complex queries to a human for review
# ✅ Use custom state to control its behavior
# ✅ Rewind and explore alternative conversation paths
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing_extensions import TypedDict,Annotated
from langchain_community.tools import tool
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt.tool_node import ToolNode,tools_condition
from langgraph.types import interrupt,Command
import uuid
from operator import add

load_dotenv()
openAI_key = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def human_assistance(state: State) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": state["messages"]})
    
    return  human_response["data"]
    

llm = ChatOpenAI(model="gpt-4o")
search_tool = TavilySearchResults(max_results=2)
checkpointer = MemorySaver()
tools = [search_tool,human_assistance]
llm_with_tools = llm.bind_tools(tools)
graph = StateGraph(State)


def chat_assistance(state:State):
    """llm generates its response"""
    bot_response = llm_with_tools.invoke(state["messages"])
    return{"messages": [bot_response]}
  
graph.add_node("chatbot",chat_assistance)
tool_node = ToolNode(tools=[search_tool,human_assistance])
graph.add_node("tools", tool_node)
graph.add_conditional_edges("chatbot", tools_condition,)

graph.add_edge("tools", "chatbot")
graph.set_entry_point("chatbot")
builder = graph.compile(checkpointer=checkpointer)


while True:
    user_input = input("\nAI: Ask me anything (or type 'quit' to exit)\nUSER: ")
    
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Goodbye!")
        break
    
    thread_id = "thread_id xyz"
    config = {'configurable': {'thread_id': thread_id}}
    ini_state = {
        "messages": [
            HumanMessage(content=user_input)
        ]
    }
   
    events = builder.stream(ini_state, config=config, stream_mode="values")
    
    for event in events:
        if "messages" in event:
         event["messages"][-1].content
        # print(f"AI: {last_msg.content}") 
    
 
    human_typing ="go to linkedin for more...."
    human_command = Command(resume={"data": human_typing})

    human_interrupt = builder.stream(human_command, config, stream_mode="values")
    for event in human_interrupt:
        if "messages" in event:
            human_interrupt_response = event["messages"][-1]
            print(f"AI: {human_interrupt_response.content}")

