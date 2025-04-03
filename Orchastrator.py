# from pydantic import BaseModel, Field
# from langgraph.graph import StateGraph, START, END
# from langchain_openai import ChatOpenAI
# import os
# from typing import Annotated, List, TypedDict
# from langchain_core.messages import SystemMessage, HumanMessage
# import operator
# from langgraph.constants import Send

# # Set up OpenAI API key
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# #first prepare a structured schema for the worker
# class worker_schema(BaseModel):
#     name:str = Field(None,description="write a brief profile summary")
#     description: str = Field(None,description="highlight the required skils")
   
# class orchestrator_schema(BaseModel):
#     each_section : list[worker_schema]
    
# llm = ChatOpenAI(model="gpt-4o")
# llm_planner = llm.with_structured_output(orchestrator_schema)

# #build the generate state
# class State(TypedDict):
#     name: str
#     sections :list[worker_schema]
#     section_complete: Annotated[list, operator.add]
#     final_state :str
    
# class workerState(TypedDict):
#     sections : worker_schema
#     section_complete: Annotated[list,operator.add]
    
# #create the orchastrator node
# def orchastrator_node(state:State):
#     planner = llm_planner.invoke([
#         SystemMessage(content="prepare a well structured resume with the provided task"),
#         HumanMessage(content=f"heres the information to use{state["name"]}")
#     ])
#     return {"sections": planner}
    

# def worker_1(state:workerState):
#    worker_1_llm =  llm.invoke([
#        SystemMessage(content=f"provide a professional and short summary of profile based on"),
#        HumanMessage(content=f"{state["sections"]}")
#    ]
#     )
#    return {"section_complete": worker_1_llm}
  

# def worker_2(state:workerState):
#     worker_2_llm = llm.invoke([
#         SystemMessage(content=f"provide a brief and proffestional job expereince based on the "),
#         HumanMessage(content=f"{state["sections"]}")
#     ])
#     return {"section_complete" : worker_2_llm}
  
# def worker_3(state:workerState):
#     worker_3_llm = llm.invoke([
#         SystemMessage(content=f" based on create skills for a resume"),
#         HumanMessage(content=f"{state["sections"]}")
#     ])
#     return{"section_complete": worker_3_llm}
   

# def worker_4(state:workerState):
#     worker_4_llm = llm.invoke([
#         SystemMessage(content=f"based on  create a good job experience"),
#         HumanMessage(content=f"{state["sections"]}")
#     ])
#     return{"section_complete" :worker_4_llm}
  
# #synth then together like building then
# def synth(state:State):
#     """putting all the workers together"""
#     completed_section = state["section_complete"]
#     all_completed_section = "\n\n".join(completed_section)
#     state["final_state"] = all_completed_section


# #assign each worker
# def assign_workers(state: State):
#     workers_dict = {
#         "profile": "worker_1",
#         "experience": "worker_2",
#         "skills": "worker_3",
#         "certification": "worker_4",
#     }
#     return [
#         Send(workers_dict.get(section), {"sections": section})
#         for section in state["sections"]
#     ]
# orchestrator = StateGraph(State)
# orchestrator.add_node("orchastrator", orchastrator_node)
# orchestrator.add_node("worker_1", worker_1)
# orchestrator.add_node("worker_2" ,worker_2)
# orchestrator.add_node("worker_3", worker_3)
# orchestrator.add_node("worker_4", worker_4)
# orchestrator.add_node("syn",synth)

# orchestrator.add_edge(START, "orchastrator")
# orchestrator.add_conditional_edges("orchastrator",assign_workers,["worker_1", "worker_2", "worker_3","worker_4"])
# orchestrator.add_edge("worker_1" ,"syn")
# orchestrator.add_edge("worker_2","syn")
# orchestrator.add_edge("worker_3","syn")
# orchestrator.add_edge("worker_4","syn")
# orchestrator.add_edge("syn",END)

# builder = orchestrator.compile()
# ini_state = State(name="AI ENGINEER",sections=[],section_complete=[],final_state="")
# response = builder.invoke(ini_state)
# print(response)

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import Send

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o")

# Define the state as a dictionary
def orchestrator_node(state):
    """Orchestrator that generates a plan for the resume."""
    planner = llm.invoke([
        SystemMessage(content="prepare a well-structured resume with the provided task"),
        HumanMessage(content=f"here's the information to use: {state['name']}")
    ])
    return {"sections": [planner.content]}

# Worker functions
def worker_1(state):
    """Worker writes the Profile section of the resume."""
    worker_1_llm = llm.invoke([
        SystemMessage(content="provide a professional and short summary of profile based on the provided information"),
        HumanMessage(content=f"{state['sections']}")
    ])
    return {"section_complete": [worker_1_llm.content]}

def worker_2(state):
    """Worker writes the Experience section of the resume."""
    worker_2_llm = llm.invoke([
        SystemMessage(content="provide a brief and professional job experience based on the provided information"),
        HumanMessage(content=f"{state['sections']}")
    ])
    return {"section_complete": [worker_2_llm.content]}

def worker_3(state):
    """Worker writes the Skills section of the resume."""
    worker_3_llm = llm.invoke([
        SystemMessage(content="based on the provided information, create skills for a resume"),
        HumanMessage(content=f"{state['sections']}")
    ])
    return {"section_complete": [worker_3_llm.content]}

def worker_4(state):
    """Worker writes the Certifications section of the resume."""
    worker_4_llm = llm.invoke([
        SystemMessage(content="based on the provided information, create a good job experience"),
        HumanMessage(content=f"{state['sections']}")
    ])
    return {"section_complete": [worker_4_llm.content]}

def worker_default(state):
    """Default worker for unknown sections."""
    worker_default_llm = llm.invoke([
        SystemMessage(content="process the provided section"),
        HumanMessage(content=f"{state['sections']}")
    ])
    return {"section_complete": [worker_default_llm.content]}

# Synthesize the final output
def synth(state):
    """Combine all completed sections into the final state."""
    completed_sections = state["section_complete"]
    all_completed_sections = "\n\n".join(completed_sections)
    state["final_state"] = all_completed_sections
    return state

# Assign workers to sections
def assign_workers(state):
    """Assign a worker to each section in the plan."""
    workers_dict = {
        "profile": "worker_1",
        "experience": "worker_2",
        "skills": "worker_3",
        "certification": "worker_4",
    }
    return [
        Send(workers_dict.get(section, "worker_default"), {"sections": section})
        for section in state["sections"]
    ]

# Build the workflow
orchestrator = StateGraph(dict)
orchestrator.add_node("orchestrator", orchestrator_node)
orchestrator.add_node("worker_1", worker_1)
orchestrator.add_node("worker_2", worker_2)
orchestrator.add_node("worker_3", worker_3)
orchestrator.add_node("worker_4", worker_4)
orchestrator.add_node("worker_default", worker_default)
orchestrator.add_node("syn", synth)

# Define edges
orchestrator.add_edge(START, "orchestrator")
orchestrator.add_conditional_edges(
    "orchestrator", assign_workers, ["worker_1", "worker_2", "worker_3", "worker_4", "worker_default"]
)
orchestrator.add_edge("worker_1", "syn")
orchestrator.add_edge("worker_2", "syn")
orchestrator.add_edge("worker_3", "syn")
orchestrator.add_edge("worker_4", "syn")
orchestrator.add_edge("worker_default", "syn")
orchestrator.add_edge("syn", END)

# Compile the workflow
builder = orchestrator.compile()

# Initialize the state
ini_state = {
    "name": "AI ENGINEER",
    "sections": [],
    "section_complete": [],
    "final_state": ""
}

# Invoke the workflow
response = builder.invoke(ini_state)
print(response["final_state"])