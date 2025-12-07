from spoon_ai.graph import StateGraph
from typing import TypedDict

class WorkflowState(TypedDict):
    counter: int
    completed: bool

def increment(state: WorkflowState):
    return {"counter": state["counter"] + 1}

def complete(state: WorkflowState):
    return {"completed": True}

# Build and execute workflow
graph = StateGraph(WorkflowState)
graph.add_node("increment", increment)
graph.add_node("complete", complete)
graph.add_edge("increment", "complete")
graph.set_entry_point("increment")

compiled = graph.compile()
result = await compiled.invoke({"counter": 0, "completed": False})
# Result: {"counter": 1, "completed": True}