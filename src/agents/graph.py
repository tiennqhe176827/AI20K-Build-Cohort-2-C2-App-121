from langgraph.graph import END, StateGraph

#from src.agents.nodes.example_node import analyze_node, respond_node


from langgraph.graph import END, StateGraph

from src.agents.nodes.fix_spelling_node import fix_spelling_node
from src.agents.nodes.soap_node import soap_node
from src.agents.nodes.transcribe_node import transcribe_node
from src.agents.state import ClinicalState


def route_after_transcribe(state: ClinicalState) -> str:
    if state.get("error"):
        return END
    return "fix_spelling"


def route_after_fix_spelling(state: ClinicalState) -> str:
    if state.get("error"):
        return END
    return "soap"


def build_graph() -> StateGraph:
    graph = StateGraph(ClinicalState)

    graph.add_node("transcribe", transcribe_node)
    graph.add_node("fix_spelling", fix_spelling_node)
    graph.add_node("soap", soap_node)

    graph.set_entry_point("transcribe")
    graph.add_conditional_edges("transcribe", route_after_transcribe)
    graph.add_conditional_edges("fix_spelling", route_after_fix_spelling)
    graph.add_edge("soap", END)

    return graph.compile()


clinical_agent = build_graph()
