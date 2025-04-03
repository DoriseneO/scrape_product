#build trivia now
# from langchain_openai import ChatOpenAI
# from pydantic import BaseModel
# from langgraph.graph import StateGraph,START,END
# from typing import Dict,Any
# from langchain_core.messages import AIMessage,HumanMessage
# import os
# from langgraph.graph.message import MessagesState,add_messages
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  
# llm =ChatOpenAI(model="gpt-4o-mini")

# def question_node(state: MessagesState):
#     for message in state.messages:
#         # Generate a response for the question
#         if message == HumanMessage:
#            response = llm.invoke(f"Provide the correct answer to: {message}")
#         new_message=AIMessage(content = response.content)
#         state = add_messages(state,new_message)
#     return state

# def correct_answer_node(state:MessagesState):
#     for message in state.messages:
#         if message == AIMessage:
#            verification=llm.invoke(f"confirmed the response 'correct' or 'wrong' {message}")
#            verified_msg = AIMessage(content=verification)
#            add_messages(state,verified_msg)
#     # print(f"i have a response {correct_ans.content}")
#     return state
      
# ini_state = MessagesState(messages=[
#     HumanMessage(content="What is the capital of France?"),
#     HumanMessage(content="Who wrote 'Romeo and Juliet'?")
# ])

# # question_node(ini_state)
# # correct_answer_node(ini_state)
# graph = StateGraph(MessagesState)
# graph.add_node("question_node", question_node)
# graph.add_node("correct_answer_node", correct_answer_node)
# graph.add_edge(START ,"question_node")
# graph.add_edge("correct_answer_node",END)
# builder = graph.compile()

# result = builder.invoke(ini_state)
# print(result)


from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import MessagesState, add_messages
import os
from typing import Annotated
from typing_extensions import TypedDict

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Initialize the LLM
llm = ChatOpenAI(model="gpt-4")  # Use a valid model name

class State(TypedDict):
    messages:Annotated[list,add_messages]
    

# Define the question node
def question_node(state: MessagesState):
    for message in state.messages:
        if isinstance(message, HumanMessage):
            response = llm.invoke(f"Provide the correct answer to: {message.content}")
            new_message = AIMessage(content=response.content)
            state = add_messages(state, new_message)
            return state
    

# Define the correct answer node
def correct_answer_node(state: MessagesState):
    for message in state.messages:
        # Check if the message is an AIMessage
        if isinstance(message, AIMessage):
            # Verify the answer
            verification = llm.invoke(f"Confirm if the response is correct or wrong: {message.content}")
            # Create a new AIMessage with the verification result
            verification_message = AIMessage(content=verification.content)
            # Add the verification message to the state using `add_messages`
            state = add_messages(state, verification_message)
            return state
    

# Define initial questions
ini_state = MessagesState(messages=[
    HumanMessage(content="What is the capital of France?"),
    HumanMessage(content="Who wrote 'Romeo and Juliet'?")
])

# Build the graph
graph = StateGraph(MessagesState)
graph.add_node("question_node", question_node)
graph.add_node("correct_answer_node", correct_answer_node)
graph.add_edge(START, "question_node")
graph.add_edge("question_node", "correct_answer_node")
graph.add_edge("correct_answer_node", END)
builder = graph.compile()

# Invoke the graph
result = builder.invoke(ini_state)

# Print the final state
for message in result.messages:
    print(f"{type(message).__name__}: {message.content}")