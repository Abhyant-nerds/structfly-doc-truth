from langgraph.graph import StateGraph, END
from app.graph.state import GraphState

from app.graph.nodes.ingest import ingest_document
from app.graph.nodes.evidence import build_evidence_bundle
from app.graph.nodes.classify import guess_document_type
from app.graph.nodes.discover import discover_candidate_fields
from app.graph.nodes.consolidate import consolidate_candidates
from app.graph.nodes.review import build_review_package
from app.graph.nodes.truth import build_ground_truth_record

def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("ingest", ingest_document)
    builder.add_node("evidence", build_evidence_bundle)
    builder.add_node("classify", guess_document_type)
    builder.add_node("discover", discover_candidate_fields)
    builder.add_node("consolidate", consolidate_candidates)
    builder.add_node("review", build_review_package)
    builder.add_node("truth", build_ground_truth_record)

    builder.set_entry_point("ingest")

    builder.add_edge("ingest", "evidence")
    builder.add_edge("evidence", "classify")
    builder.add_edge("classify", "discover")
    builder.add_edge("discover", "consolidate")
    builder.add_edge("consolidate", "review")
    builder.add_edge("review", "truth")
    builder.add_edge("truth", END)

    return builder.compile()

graph = build_graph()
