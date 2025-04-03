from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from typing import Annotated, List
import operator

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)  

# Define the state
class State(BaseModel):
    query: Annotated[list, operator.add]  
    positive_feedback: str = "" 
    negative_feedback: str = "" 

def positive_feedback_node(state: State):
    p_feedback = llm.invoke(f"Check if the following feedback is positive: {state.query[-1]}")
    print(f"Positive Feedback: \n{p_feedback.content}")
    state.positive_feedback = p_feedback.content
    return state  

# Node to check for negative feedback
def negative_feedback_node(state: State):
    n_feedback = llm.invoke(f"Check if the following feedback is negative: {state.query[-1]}")
    print(f"Negative Feedback: \n{n_feedback.content}")
    state.negative_feedback = n_feedback.content
    return state  


def aggregator_node(state: State):
    print("Aggregating results...")
    if "positive" in state.positive_feedback.lower():
        print("This is a positive review.")
    elif "negative" in state.negative_feedback.lower():
        print("This is a negative review.")
    else:
        print("The feedback is neutral or unclear.")
    return state  


ini_state = State(query=[input("Write your feedback: ")])

# Build the graph
graph = StateGraph(State)
graph.add_node("positive", positive_feedback_node)
graph.add_node("negative", negative_feedback_node)
graph.add_node("aggregate", aggregator_node)

# Define edges
graph.add_edge(START, "positive")  
graph.add_edge(START, "negative") 
graph.add_edge("positive", "aggregate")  
graph.add_edge("negative", "aggregate")  
graph.add_edge("aggregate", END)  

# Compile and run the graph
builder = graph.compile()
output = builder.invoke(ini_state)
print(output)