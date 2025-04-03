from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from typing import Annotated, List, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
import operator
from langgraph.constants import Send

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o")

#i am planing my wedding and
#i want rita for makeup
#ladi for dress
#shelter for food
#tracy for event

class worker_schema(BaseModel):
    vendors_name:str= Field(None,description="give me the very best vendor in nieria"),
    vendors_price: str=Field(None,description="give me their prices")
    
class state_schema(BaseModel):
    my_list: List[worker_schema]
        
class State(TypedDict):
    name_of_what_i_want: str
    my_list: List[worker_schema]
    completed_list: Annotated[list,operator.add]
    
class worker_state(TypedDict):
    each_worker: worker_schema
    completed_list: Annotated[list,operator.add]
    
#structure the schema
llm_planner = llm.with_structured_output(state_schema)

def orchestrator(state:State):
    planner = llm_planner.invoke([
        SystemMessage(content="each worker should provide response for the planing of my wedding")
    ,
    HumanMessage(content=f"here is the exact thing i want them to answer {state['name_of_what_i_want']}")]) 
    return{ "completed_list" : planner.my_list}

def worker(state:worker_state):
     worker_llm =llm.invoke([
        SystemMessage(content="provide the list of the best and highly rated"),
        HumanMessage(content=f"{state['each_worker'].vendors_name} and {state['each_worker'].vendors_price}")
    ])
     return{ "completed_list" : worker_llm.content}
 
 
 
