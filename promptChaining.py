from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph,START,END
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
class State(BaseModel):
    query: str

def query_node(state:State) :
       generate_query = llm.invoke(f"what is the {state}")
       print(f"define_query: \n{generate_query.content}")
       return state
  
  
def skills_node(state:State):
    generate_skills = llm.invoke(f"tell me the most needed skills to become,make it brief {state}") 
    print(f"\n\n skills_needed:\n{generate_skills.content}")  
    return state

def experience_node(state:State):
    generate_experience = llm.invoke(f"what kind of experience is require,state just two: {state}")
    print(f"\n\n experience_needed:\n{generate_experience.content}")


user_query = "AI Engineer" 
graph = StateGraph(State)
graph.add_node("query_node", query_node)
graph.add_node("skills_node",skills_node)
graph.add_node("experience_node",experience_node)
graph.add_edge(START,"query_node")
graph.add_edge("query_node","skills_node")
graph.add_edge("skills_node","experience_node")
graph.add_edge("experience_node",END)
builder = graph.compile()
ini_state =State(query=user_query)  
result = builder.invoke(ini_state)
print(result)


