# Build Plan — HR Recruitment Automation Demo

## Prerequisites
- Python 3.11+
- Groq API key
- Resend API key (use `onboarding@resend.dev` as sender)

---

## Step 1 — Project Scaffold
- Create directory structure:
  ```
  wayalinks-hr-agent/
  ├── agents/
  │   ├── __init__.py
  │   ├── jd_generator.py
  │   ├── screener.py
  │   ├── ranker.py
  │   └── notifier.py
  ├── graph/
  │   ├── __init__.py
  │   └── pipeline.py
  ├── data/
  │   ├── __init__.py
  │   └── candidates.py
  ├── app.py
  └── .env.example
  ```
- Create `.env.example` with `GROQ_API_KEY`, `RESEND_API_KEY`, `HR_EMAIL`
- Create `requirements.txt` with all deps

---

## Step 2 — Mock Candidates
- Create `data/candidates.py` with the 5 hardcoded candidates from the spec
- Each candidate: name, email, experience_years, answers dict

---

## Step 3 — LangGraph State
- Create `graph/pipeline.py` with `HRState` TypedDict
- All fields: job_brief, job_description, candidates, scores, top_candidate, shortlisted, shortlist_sent, hr_notified, hr_approved, acceptance_sent

---

## Step 4 — Agent: JD Generator
- `agents/jd_generator.py`
- LLM call via Groq (langchain-groq, model `llama-3.3-70b-versatile`)
- Prompt: generate professional JD from 2-line brief
- Output: plain text job description → `state["job_description"]`

---

## Step 5 — Agent: Screener
- `agents/screener.py`
- Loop over 5 candidates, for each: send JD + candidate answers to LLM
- Score 0–100 with 2-sentence reasoning
- Collect into list of `{name, email, score, reasoning}` → `state["scores"]`

---

## Step 6 — Agent: Ranker
- `agents/ranker.py`
- Sort scores descending
- Set `top_candidate` (index 0) and `shortlisted` (top 3)
- Pure Python, no LLM call

---

## Step 7 — Agent: Notifier
- `agents/notifier.py`
- Shared `send_email(to, subject, body)` via Resend
- `invite_shortlisted(state)` — 3 shortlist emails
- `notify_hr(state)` — ranked report to HR
- `send_acceptance(state)` — offer to winner

---

## Step 8 — Graph Assembly
- `graph/pipeline.py` — build LangGraph StateGraph
- Nodes: generate_jd → score_candidates → rank_candidates → invite_shortlisted → notify_hr → send_acceptance
- `interrupt_after=["notify_hr"]` to pause for HR approval
- `MemorySaver` checkpointer with thread ID `"hr-demo-thread-1"`
- Export compiled graph

---

## Step 9 — Streamlit UI
- `app.py` with 6-stage pipeline status bar
- Stage 0: text input + "Generate Job Description" button
- Stage 1: show JD in expander + candidate cards + "Analyse All Candidates" button
- Stage 2: ranked table (highlight top 3) + "Shortlist Top 3 & Notify HR" button
- Stage 3: top candidate card + "Approve & Send Offer" button (the interrupt resume point)
- Stage 4: done screen with pipeline summary
- Session state keys: stage, job_description, scores, shortlisted, top_candidate, graph_state

---

## Step 10 — README
- Setup, run instructions, architecture diagram
- What the demo proves (5 emails, 1 click)

---

## Step 11 — Smoke Test
- `pip install -r requirements.txt`
- Fill `.env` with real keys
- `streamlit run app.py`
- Run full pipeline end-to-end
