from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.jd_generator import generate_jd
from agents.screener import score_candidates
from agents.ranker import rank_candidates
from agents.notifier import notify_hr


class HRState(TypedDict):
    job_brief: str
    job_description: str
    candidates: List[Dict[str, Any]]
    scores: List[Dict[str, Any]]
    top_candidate: Dict[str, Any]
    shortlisted: List[Dict[str, Any]]
    hr_notified: bool
    hr_approved: bool


def build_pipeline():
    builder = StateGraph(HRState)
    builder.add_node("generate_jd", generate_jd)
    builder.add_node("score_candidates", score_candidates)
    builder.add_node("rank_candidates", rank_candidates)
    builder.add_node("notify_hr", notify_hr)
    builder.add_edge(START, "generate_jd")
    builder.add_edge("generate_jd", "score_candidates")
    builder.add_edge("score_candidates", "rank_candidates")
    builder.add_edge("rank_candidates", "notify_hr")
    builder.add_edge("notify_hr", END)
    app = builder.compile()
    return app
