from langgraph.graph import StateGraph, START, END

from nodes import (
    interaction,
    completeness_checker,
    planner,
    question_generator,
    decision_layer,
    confidence_router,
    rule_engine,
    output_layer,
    risk_persistence
)

from state import HealthState

graph_builder = StateGraph(HealthState)

graph_builder.add_node("interaction", interaction)
graph_builder.add_node("completeness_checker", completeness_checker)
graph_builder.add_node("planner", planner)
graph_builder.add_node("question_generator", question_generator)
graph_builder.add_node("decision_layer", decision_layer)
graph_builder.add_node("confidence_router", confidence_router)
graph_builder.add_node("rule_engine", rule_engine)
graph_builder.add_node("output_layer", output_layer)
graph_builder.add_node("risk_persistence",risk_persistence)
graph_builder.add_edge(START, "interaction")
graph_builder.add_edge("interaction", "completeness_checker")


def route_after_completeness(state: HealthState):

    return "planner" if not state["completed"] else "decision_layer"


graph_builder.add_conditional_edges(
    "completeness_checker",
    route_after_completeness,
    {"planner": "planner", "decision_layer": "decision_layer"},
)

graph_builder.add_edge("planner", "question_generator")
graph_builder.add_edge("question_generator", END)

graph_builder.add_edge("decision_layer", "confidence_router")
graph_builder.add_edge("confidence_router", "rule_engine")
graph_builder.add_edge("rule_engine", "risk_persistence")
graph_builder.add_edge("risk_persistence", "output_layer")
graph_builder.add_edge("output_layer", END)

graph = graph_builder.compile()
print(graph.get_graph().draw_ascii())