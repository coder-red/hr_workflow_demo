"""
Screener agent.

Scores all candidates in a single LLM call for speed (batched).
Returns a JSON array of {name, score, reasoning} objects.
"""

import json


def score_candidates(state: dict) -> dict:
    """
    LangGraph node. Scores ALL candidates in one LLM call instead of looping.
    This is ~5x faster since it avoids sequential API round-trips.
    """
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate

    SYSTEM_PROMPT = """You are a technical recruiter. Score ALL candidates below against the job description.

Return ONLY a JSON array of objects. Each object must have exactly three keys:
- "name": the candidate's name
- "score": an integer from 0 to 100
- "reasoning": a 2-sentence explanation of the score

Do not include any other text or formatting. The array must have exactly {count} entries."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Job Description:\n{job_description}\n\n"
            "{candidate_details}\n\n"
            "Return a JSON array of {count} objects, one per candidate, with name, score, reasoning.",
        ),
    ])

    candidates = state["candidates"]
    details = "\n---\n".join(
        f"Candidate Name: {c['name']}\n"
        f"Experience: {c['experience_years']} years\n"
        f"Relevant Experience: {c['answers']['relevant_experience']}\n"
        f"Why Role: {c['answers']['why_role']}\n"
        f"Availability: {c['answers']['availability']}\n"
        f"Salary Expectation: {c['answers']['salary_expectation']}"
        for c in candidates
    )

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    chain = prompt | llm
    result = chain.invoke({
        "job_description": state["job_description"],
        "candidate_details": details,
        "count": len(candidates),
    })

    parsed = json.loads(result.content.strip())

    scores = []
    for c, p in zip(candidates, parsed):
        scores.append({
            "name": c["name"],
            "email": c["email"],
            "score": p["score"],
            "reasoning": p["reasoning"],
        })

    return {"scores": scores}
