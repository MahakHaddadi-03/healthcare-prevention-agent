from langgraph.graph import StateGraph, START, END

from nodes import (
    interaction,
    completeness_checker,
    planner,
    question_generator,
    final_response,
    route_after_checker,
)

from state import HealthState

graph_builder = StateGraph(HealthState)

graph_builder.add_node("interaction", interaction)
graph_builder.add_node("completeness_checker", completeness_checker)
graph_builder.add_node("planner", planner)
graph_builder.add_node("question_generator", question_generator)
graph_builder.add_node("final_response", final_response)

graph_builder.add_edge(START, "interaction")

graph_builder.add_edge(
    "interaction",
    "completeness_checker",
)

graph_builder.add_conditional_edges(
    "completeness_checker",
    route_after_checker,
    {
        "planner": "planner",
        "final_response": "final_response",
    },
)

graph_builder.add_edge(
    "planner",
    "question_generator",
)

graph_builder.add_edge(
    "question_generator",
    END,
)

graph_builder.add_edge(
    "final_response",
    END,
)

graph = graph_builder.compile()