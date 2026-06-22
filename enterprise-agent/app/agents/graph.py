from langgraph.graph import END, StateGraph

from app.agents.specialized.memory_agent import memory_node
from app.agents.specialized.rag_agent import rag_node
from app.agents.specialized.tool_agent import tool_node
from app.agents.state import AgentState
from app.agents.supervisor import supervisor_node


def _route(state: AgentState) -> str:
    return state.next_agent


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("tool", tool_node)
    graph.add_node("memory", memory_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        _route,
        {"rag": "rag", "tool": "tool", "memory": "memory", "__end__": END},
    )

    for node in ("rag", "tool", "memory"):
        graph.add_edge(node, "supervisor")

    return graph


compiled_graph = build_graph().compile()
