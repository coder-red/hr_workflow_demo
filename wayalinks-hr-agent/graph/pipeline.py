from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.jd_generator import generate_jd
from agents.screener import score_candidates
from agents.ranker import rank_candidates
from agents.notifier import invite_shortlisted, notify_hr, send_acceptance


class HRState(TypedDict):
    job_brief: str
    job_description: str
    candidates: List[Dict[str, Any]]
    scores: List[Dict[str, Any]]
    top_candidate: Dict[str, Any]
    shortlisted: List[Dict[str, Any]]
    shortlist_sent: bool
    hr_notified: bool
    hr_approved: bool
    acceptance_sent: bool


def build_pipeline():
    builder = StateGraph(HRState)
    builder.add_node("generate_jd", generate_jd)
    builder.add_node("score_candidates", score_candidates)
    builder.add_node("rank_candidates", rank_candidates)
    builder.add_node("invite_shortlisted", invite_shortlisted)
    builder.add_node("notify_hr", notify_hr)
    builder.add_node("send_acceptance", send_acceptance)
    builder.add_edge(START, "generate_jd")
    builder.add_edge("generate_jd", "score_candidates")
    builder.add_edge("score_candidates", "rank_candidates")
    builder.add_edge("rank_candidates", "invite_shortlisted")
    builder.add_edge("invite_shortlisted", "notify_hr")
    builder.add_edge("notify_hr", "send_acceptance")
    builder.add_edge("send_acceptance", END)
    app = builder.compile()
    return app
