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

class Section(BaseModel):
    name: str = Field(description="Name of the resume section (e.g., Profile, Skills, Experience, Certifications).")
    description: str = Field(description="Brief description of what should be included in this section.")

class Sections(BaseModel):
    sections: List[Section] = Field(description="List of sections for the resume.")

llm_model = llm.with_structured_output(Sections)

class State(TypedDict):
    topic: str  
    sections: List[Section]  
    completed_sections: Annotated[List, operator.add]  
    final_report: str  

# Step 3: Define the Worker State
class WorkerState(TypedDict):
    section: Section  # The section the worker is processing
    completed_sections: Annotated[List, operator.add] 

# Step 4: Create the Orchestrator
def orchestrator(state: State):
    """Orchestrator that generates a plan for the resume."""
    # Generate sections using the LLM
    resume_sections = llm_model.invoke([
        SystemMessage(content="create a good and professional resume based on the human request"),
        HumanMessage(content=f"here {state['topic']}")
    ])
    
    # Ensure sections is a list of Section objects
    if isinstance(resume_sections, tuple):
        resume_sections = list(resume_sections)
    return {"sections": resume_sections.sections}

# Step 5: Create Worker Nodes
def llm_call_profile(state: WorkerState):
    """Worker writes the Profile section of the resume."""
    return process_section(state)

def llm_call_skills(state: WorkerState):
    """Worker writes the Skills section of the resume."""
    return process_section(state)

def llm_call_experience(state: WorkerState):
    """Worker writes the Experience section of the resume."""
    return process_section(state)

def llm_call_certifications(state: WorkerState):
    """Worker writes the Certifications section of the resume."""
    return process_section(state)

def process_section(state: WorkerState):
    """Process a section and generate its content."""
    section = llm.invoke(
        [
            SystemMessage(
                content="Write a resume section following the provided name and description. Use markdown formatting."
            ),
            HumanMessage(
                content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
            ),
        ]
    )
    return {"completed_sections": [section.content]}

def assign_workers(state: State):
    worker_mapping = {
        "Profile": "llm_call_profile",
        "Skills": "llm_call_skills",
        "Experience": "llm_call_experience",
        "Certifications": "llm_call_certifications",
    }
    return [
        Send(worker_mapping.get(task.name), {"task": task})
        for task in state["tasks"]
    ]  

def synthesizer(state: State):
    """Synthesize the full resume from sections."""
    completed_sections = state["completed_sections"]
    completed_resume = "\n\n---\n\n".join(completed_sections)
    return {"final_report": completed_resume}

# Step 8: Build the Graph
resume_builder = StateGraph(State)
resume_builder.add_node("orchestrator", orchestrator)
resume_builder.add_node("llm_call_profile", llm_call_profile)
resume_builder.add_node("llm_call_skills", llm_call_skills)
resume_builder.add_node("llm_call_experience", llm_call_experience)
resume_builder.add_node("llm_call_certifications", llm_call_certifications)
resume_builder.add_node("synthesizer", synthesizer)

# Add edges to connect nodes
resume_builder.add_edge(START, "orchestrator")
resume_builder.add_conditional_edges(
    "orchestrator", assign_workers, 
    ["llm_call_profile", "llm_call_skills", "llm_call_experience", "llm_call_certifications"]
)
resume_builder.add_edge("llm_call_profile", "synthesizer")
resume_builder.add_edge("llm_call_skills", "synthesizer")
resume_builder.add_edge("llm_call_experience", "synthesizer")
resume_builder.add_edge("llm_call_certifications", "synthesizer")
resume_builder.add_edge("synthesizer", END)

# Compile the workflow
resume_workflow = resume_builder.compile()

# Step 9: Invoke the Workflow
state = resume_workflow.invoke({"topic": "Create a professional resume for an AI engineer."})
print(state)





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

# llm = ChatOpenAI(model="gpt-4o")
# # Step 1: Define the Schema for Resume Sections
# class Section(BaseModel):
#     name: str = Field(description="Name of the resume section (e.g., Profile, Skills, Experience, Certifications).")
#     description: str = Field(description="Brief description of what should be included in this section.")

# class Sections(BaseModel):
#     sections: List[Section] = Field(description="List of sections for the resume.")

# # llm_model = llm.with_structured_output(Sections)

# class State(TypedDict):
#     topic: str  
#     sections: List[Section]  
#     completed_sections: Annotated[List, operator.add]  
#     final_report: str  

# # Step 3: Define the Worker State
# class WorkerState(TypedDict):
#     section: Section  # The section the worker is processing
#     completed_sections: Annotated[List, operator.add] 
     
# # Step 4: Create the Orchestrator
# def orchestrator(state: State):
#     """Orchestrator that generates a plan for the resume."""
#     resume_sections = [
#         Section(name="Profile", description="A brief summary of the candidate's background and career goals."),
#         Section(name="Skills", description="A list of the candidate's key skills and competencies."),
#         Section(name="Experience", description="Detailed descriptions of the candidate's work experience."),
#         Section(name="Certifications", description="A list of the candidate's certifications and qualifications."),
#     ]
#     return {"sections": resume_sections}

# # Step 5: Create Worker Nodes
# def llm_call_profile(state: WorkerState):
#     """Worker writes the Profile section of the resume."""
#     return process_section(state)

# def llm_call_skills(state: WorkerState):
#     """Worker writes the Skills section of the resume."""
#     return process_section(state)

# def llm_call_experience(state: WorkerState):
#     """Worker writes the Experience section of the resume."""
#     return process_section(state)

# def llm_call_certifications(state: WorkerState):
#     """Worker writes the Certifications section of the resume."""
#     return process_section(state)

# def process_section(state: WorkerState):
#     """Process a section and generate its content."""
#     section = llm.invoke(
#         [
#             SystemMessage(
#                 content="Write a resume section following the provided name and description. Use markdown formatting."
#             ),
#             HumanMessage(
#                 content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
#             ),
#         ]
#     )

#     return {"completed_sections": [section.content]}
# def assign_workers(state: State):
#     """Assign a worker to each section in the plan."""

#     # Map section names to worker nodes
#     worker_mapping = {
#         "Profile": "llm_call_profile",
#         "Skills": "llm_call_skills",
#         "Experience": "llm_call_experience",
#         "Certifications": "llm_call_certifications",
#     }

#     # Kick off section writing in parallel via Send() API
#     return [Send(worker_mapping[s.name], {"section": s}) for s in state["sections"]]

# # Step 7: Define the Synthesizer
# def synthesizer(state: State):
#     """Synthesize the full resume from sections."""
#     completed_sections = state["completed_sections"]
#     completed_resume = "\n\n---\n\n".join(completed_sections)

#     return {"final_report": completed_resume}

# resume_builder = StateGraph(State)
# resume_builder.add_node("orchestrator", orchestrator)
# resume_builder.add_node("llm_call_profile", llm_call_profile)
# resume_builder.add_node("llm_call_skills", llm_call_skills)
# resume_builder.add_node("llm_call_experience", llm_call_experience)
# resume_builder.add_node("llm_call_certifications", llm_call_certifications)
# resume_builder.add_node("synthesizer", synthesizer)

# # Add edges to connect nodes
# resume_builder.add_edge(START, "orchestrator")
# resume_builder.add_conditional_edges(
#     "orchestrator", assign_workers, 
#     ["llm_call_profile", "llm_call_skills", "llm_call_experience", "llm_call_certifications"]
# )
# resume_builder.add_edge("llm_call_profile", "synthesizer")
# resume_builder.add_edge("llm_call_skills", "synthesizer")
# resume_builder.add_edge("llm_call_experience", "synthesizer")
# resume_builder.add_edge("llm_call_certifications", "synthesizer")
# resume_builder.add_edge("synthesizer", END)

# # Compile the workflow
# resume_workflow = resume_builder.compile()

# # Step 9: Invoke the Workflow
# state = resume_workflow.invoke({"topic": "Create a professional resume for an Ai engineer."})
# print(state)
