from typing import TypedDict
import uuid
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

class State(TypedDict):
   """The graph state."""
   name: str
def node_1(state:State):
    response = state['name'] + " ENE"
    return{"name" : response}

def human_interrupt(state:State):
    value= interrupt(
        { "original": state["name"],
        "instruction": "Approve or edit this name"} 
    )
    return{"name": value}

graph = StateGraph(State)
graph.add_node("node_1",node_1)
graph.add_node("human",human_interrupt)
graph.add_edge(START,"node_1")
graph.add_edge("node_1","human")
graph.add_edge("human" ,END)

checkpointer = MemorySaver()
thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

builder = graph.compile(checkpointer=checkpointer)
ini = State(name ="doris")
print(builder.invoke(ini,config=thread_config))

for chunk in builder.stream({"name": "Original text"}, config=thread_config):
   print(chunk)

for chunk in builder.stream(Command(resume="approved it"), config=thread_config):
   print(chunk)