from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage

# Set up OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the schema for routing
class Route(BaseModel):
    step: Literal["positive", "negative", "neutral"] = Field(
        None, description="The next step in the routing process"
    )

# Define the state
class State(BaseModel):
    query: str
    decision: str = ""
    output: str = ""

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_route = llm.with_structured_output(Route)

# Define nodes
def positive_node(state: State):
    state.output = "This is a positive response."
    return state

def negative_node(state: State):
    state.output = "This is a negative response."
    return state

def neutral_node(state: State):
    state.output = "This is a neutral response."
    return state

# Define the router node
def llm_call_router(state: State):
    # Use the LLM to decide the next step
    decision = structured_route.invoke([
        SystemMessage(content="Route the input to 'positive', 'negative', or 'neutral' based on the sentiment."),
        HumanMessage(content=state.query),
    ])
    state.decision = decision.step
    return state

# Define the conditional edge function
def route_decision(state: State):
    if state.decision == "positive":
        print("thank you ,we hope you have fun")
        return "positive_node"
    elif state.decision == "negative":
        return "negative_node"
    elif state.decision == "neutral":
        return "neutral_node"

# Build the workflow
router_builder = StateGraph(State)

# Add nodes
router_builder.add_node("positive_node", positive_node)
router_builder.add_node("negative_node", negative_node)
router_builder.add_node("neutral_node", neutral_node)
router_builder.add_node("llm_call_router", llm_call_router)

# Add edges
router_builder.add_edge(START, "llm_call_router")
router_builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {
        "positive_node": "positive_node",
        "negative_node": "negative_node",
        "neutral_node": "neutral_node",
    },
)
router_builder.add_edge("positive_node", END)
router_builder.add_edge("negative_node", END)
router_builder.add_edge("neutral_node", END)

# Compile the workflow
router_workflow = router_builder.compile()

# Invoke the workflow
user_input = input("Ask anything: ")
initial_state = State(query=user_input)
final_state = router_workflow.invoke(initial_state)

# Print the output
print(final_state["output"])