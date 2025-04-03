#build trivia now
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph,START,END
from typing import Dict,Any
from langchain_core.messages import AIMessage
import os
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph.message import MessagesState,add_messages
from langgraph.checkpoint.memory import MemorySaver
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class State(BaseModel):
    messages_one: list[Dict[str,Any]]
  
llm =ChatOpenAI(model="gpt-4o-mini")


def question_node(state: State):
    for message in state.messages_one:
        # Generate a response for the question
        response = llm.invoke(f"Provide the correct answer to: {message["question"]}")
        message["answer"] =response.content 
        # print(f"Question: {question}")
        # print(f"Response: {response.content}\n")
    return state

def correct_answer_node(state:State):
    for message in state.messages_one:
        llm.invoke(f"confirmed the response 'correct' or 'wrong' {message["answer"]}")
    # print(f"i have a response {correct_ans.content}")
   
      
all_questions = [
   {"question" :"What is the capital of Nigeria?"},
   {"question": "Who is the president of Nigeria?"},
   {"question": "What is the father's role in a family?"}
]

ini_state = State(messages_one=all_questions)
checkpointer = MemorySaver()
thread_id = "thread_id"
config ={"configurable": {"thread_id": thread_id}}

question_node(ini_state)
correct_answer_node(ini_state)
graph = StateGraph(State)
graph.add_node("question_node", question_node)
graph.add_node("correct_answer_node", correct_answer_node)
graph.add_edge(START ,"question_node")
graph.add_edge("correct_answer_node",END)
builder = graph.compile(checkpointer=checkpointer)

# for graph_stream in builder.stream(ini_state,stream_mode="values"):
#     print(graph_stream)

travel_time = builder.stream(ini_state,config=config, stream_mode="values")
for travel in travel_time:
    last_msg = travel['messages_one']
    print(f"travel_time {last_msg}")

