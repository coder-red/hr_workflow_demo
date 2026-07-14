"""
Ranker agent.

Pure Python sorting — no LLM call. Takes scored candidates, sorts descending
by score, assigns ranks, and identifies the top candidate and shortlist (top 3).
"""


def rank_candidates(state: dict) -> dict:
    """
    LangGraph node. Sorts state["scores"] by score descending, assigns rank,
    sets top_candidate (index 0) and shortlisted (top 3).
    """
    scores = sorted(state["scores"], key=lambda x: x["score"], reverse=True)

    # Assign rank after sorting
    for i, s in enumerate(scores):
        s["rank"] = i + 1

    return {
        "scores": scores,
        "top_candidate": scores[0],
        "shortlisted": scores[:3],
    }
