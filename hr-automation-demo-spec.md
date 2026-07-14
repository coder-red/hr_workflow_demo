# HR Recruitment Automation Demo — Build Spec

## What This Is

A LangGraph-powered HR recruitment pipeline demo. HR enters a job brief, the system generates a full JD, scores 5 pre-loaded candidates against it, automatically emails the top 3 a shortlist notification, emails a ranked report to HR, and after HR approves, fires a formal acceptance email to the winner. Every email is real and sends via Resend.

HR touches the app exactly once — the approve button. Everything else runs automatically.

No database. No FastAPI. State lives in memory and Streamlit session state. Mock candidates are hardcoded.

---

## Pipeline Steps Being Demoed

| Step | From Original List | What Happens |
|------|--------------------|--------------|
| 1 | Generate JD | HR types a 2-line brief, full JD is generated |
| 6 | Score & rank | AI scores all 5 candidates against the JD |
| 4 | Invite top candidates | System auto-emails top 3 a shortlist notification |
| 7 | Notify HR | HR receives ranked report email |
| 8 | HR approval + acceptance | HR approves, winner gets formal acceptance email |

Total emails fired per demo run: **5** (3 shortlist + 1 HR report + 1 acceptance). All real. All Resend.

---

## Tech Stack

```
langgraph
langchain-core
langchain-groq
streamlit
python-dotenv
resend
```

Install: `pip install langgraph langchain-core langchain-groq streamlit python-dotenv resend`

LLM: Groq — model `llama-3.3-70b-versatile`
Email: Resend — sender `onboarding@resend.dev`
No database. No FastAPI. No Redis.

---

## Project Structure

```
hr-agent/
├── agents/
│   ├── jd_generator.py
│   ├── screener.py
│   ├── ranker.py
│   └── notifier.py
├── graph/
│   └── pipeline.py
├── app.py
├── .env.example
└── README.md
```

---

## Environment Variables

`.env.example`:
```
GROQ_API_KEY=your_groq_key_here
RESEND_API_KEY=your_resend_key_here
HR_EMAIL=hr@company.com
```

---

## Mock Candidates

Hardcode in `graph/pipeline.py` or `data/candidates.py`. These are already "submitted" when the demo loads — no form, no waiting.

```python
MOCK_CANDIDATES = [
    {
        "name": "Amara Osei",
        "email": "youremail+amara@gmail.com",
        "experience_years": 5,
        "answers": {
            "relevant_experience": "5 years in frontend engineering, led a team of 3 at a Lagos fintech building React dashboards.",
            "why_role": "Excited by the fintech infrastructure problem space. The payment layer is exactly where I want to build.",
            "availability": "2 weeks notice",
            "salary_expectation": "500k/month"
        }
    },
    {
        "name": "Chidi Nwosu",
        "email": "youremail+chidi@gmail.com",
        "experience_years": 2,
        "answers": {
            "relevant_experience": "2 years junior dev, mostly WordPress and some Vue. No fintech experience.",
            "why_role": "Looking for a career change into fintech.",
            "availability": "Immediately",
            "salary_expectation": "250k/month"
        }
    },
    {
        "name": "Fatima Al-Hassan",
        "email": "youremail+fatima@gmail.com",
        "experience_years": 7,
        "answers": {
            "relevant_experience": "7 years full-stack, 3 of which at Interswitch building payment APIs. Deep knowledge of PCI-DSS compliance.",
            "why_role": "Want to move to a growth-stage company where I can own more of the architecture.",
            "availability": "1 month notice",
            "salary_expectation": "700k/month"
        }
    },
    {
        "name": "Emeka Eze",
        "email": "youremail+emeka@gmail.com",
        "experience_years": 4,
        "answers": {
            "relevant_experience": "4 years backend Python, built 2 internal automation tools. No payments experience but strong on APIs.",
            "why_role": "Interested in the problem, been following the space for a while.",
            "availability": "3 weeks notice",
            "salary_expectation": "450k/month"
        }
    },
    {
        "name": "Ngozi Adeyemi",
        "email": "youremail+ngozi@gmail.com",
        "experience_years": 6,
        "answers": {
            "relevant_experience": "6 years, previously at Flutterwave for 2 years on the merchant onboarding team. Knows the space well.",
            "why_role": "Flutterwave got too corporate. Wants a smaller team with more ownership.",
            "availability": "2 weeks notice",
            "salary_expectation": "600k/month"
        }
    }
]
```

> **Demo setup:** Use Gmail + aliases (`youremail+amara@gmail.com` etc.) — they all land in your inbox. During the call, have your inbox open on a second screen. When 3 shortlist emails fire automatically and then the HR report lands, that's your money shot. The client sees real emails arriving in real time.

---

## LangGraph State

Define this in `graph/pipeline.py`:

```python
from typing import TypedDict, List, Dict, Any

class HRState(TypedDict):
    job_brief: str
    job_description: str
    candidates: List[Dict[str, Any]]
    scores: List[Dict[str, Any]]        # [{name, email, score (0-100), reasoning, rank}]
    top_candidate: Dict[str, Any]
    shortlisted: List[Dict[str, Any]]   # top 3 candidates
    shortlist_sent: bool
    hr_notified: bool
    hr_approved: bool
    acceptance_sent: bool
```

---

## Agent Specs

### `agents/jd_generator.py`

**Input:** `state["job_brief"]`
**Output:** `state["job_description"]`

Prompt the LLM to generate a professional job description with: role summary, 5-7 responsibilities, required qualifications, and nice-to-haves. Return plain text.

---

### `agents/screener.py`

**Input:** `state["job_description"]`, `state["candidates"]`
**Output:** `state["scores"]`

For each candidate, send the LLM the JD and the candidate's answers. Ask it to score 0-100 against the JD with 2-sentence reasoning. Return a list of dicts: `{name, email, score, reasoning}`. Loop candidates one at a time, collect all results.

---

### `agents/ranker.py`

**Input:** `state["scores"]`
**Output:** `state["scores"]` (sorted descending), `state["top_candidate"]`, `state["shortlisted"]`

Sort scores descending by score. Set `top_candidate` to index 0. Set `shortlisted` to the top 3. No LLM call — pure Python.

---

### `agents/notifier.py`

All emails send via Resend. Use this pattern for every send:

```python
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to: str, subject: str, body: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": subject,
        "text": body
    })
```

**Three functions:**

**`invite_shortlisted(state)`**
Loop through `state["shortlisted"]` (top 3 candidates). Send each one a shortlist email:
- Subject: `You've been shortlisted — [Job Title]`
- Body: Congratulate them by name, tell them they've been shortlisted, say HR will be in touch with next steps. Keep it short and professional.
- Sets `state["shortlist_sent"] = True`

**`notify_hr(state)`**
Send to `HR_EMAIL`:
- Subject: `Recruitment Update — Candidate Rankings Ready`
- Body: Full ranked list of all 5 candidates — rank, name, score, reasoning. Plain text table format. Note that shortlist emails have already been sent to the top 3.
- Sets `state["hr_notified"] = True`

**`send_acceptance(state)`**
Send to `state["top_candidate"]["email"]`:
- Subject: `Offer of Employment — [Job Title]`
- Body: Formal congratulations by name. State they have been selected. Say official offer documents will follow. Ask them to confirm receipt.
- Sets `state["acceptance_sent"] = True`

---

## Graph Definition

In `graph/pipeline.py`:

```
START
  → generate_jd
  → score_candidates
  → rank_candidates
  → invite_shortlisted        ← 3 emails fire automatically
  → notify_hr                 ← HR report email fires
  → [INTERRUPT — wait for HR approval]
  → send_acceptance            ← acceptance email fires
END
```

Use `interrupt_after=["notify_hr"]` so the graph pauses after the HR email and waits for approval.

Use `MemorySaver` as the checkpointer. Thread ID: `"hr-demo-thread-1"`.

---

## Streamlit UI — `app.py`

### Pipeline Status Bar

6 stages shown horizontally at the top using `st.columns`:

```
[Generate JD] → [Score Candidates] → [Shortlist Top 3] → [Notify HR] → [HR Review] → [Offer Sent]
```

Each stage turns green with a checkmark as it completes.

### Stage Flow

**Stage 0**
- Text input: "Describe the role in 1-3 sentences"
- Button: "Generate Job Description"
- On click: run `generate_jd`

**Stage 1 — JD Generated**
- Show generated JD in `st.expander`
- Show candidate preview cards (name + experience years)
- Button: "Analyse All Candidates"
- On click: run `score_candidates` → `rank_candidates`

**Stage 2 — Candidates Ranked**
- Show ranked table: Rank | Name | Score | Reasoning
- Highlight top 3 rows (shortlist)
- Button: "Shortlist Top 3 & Notify HR"
- On click: run `invite_shortlisted` → `notify_hr`
- Show: "3 shortlist emails sent to candidates" + "Report emailed to HR"

**Stage 3 — HR Review**
- Show top candidate summary card (name, score, reasoning)
- Show note: "Shortlist emails already sent to top 3"
- Button: "Approve & Send Offer" — this is the ONE action HR takes
- On click: run `send_acceptance`

**Stage 4 — Done**
- Show: "Offer sent to [name]"
- Show full pipeline summary: 5 emails sent, 0 manual steps except one approval

### Session State Keys
```python
st.session_state.stage
st.session_state.job_description
st.session_state.scores
st.session_state.shortlisted
st.session_state.top_candidate
st.session_state.graph_state
```

---

## How to Run

```bash
cp .env.example .env
# fill in your keys
streamlit run app.py
```

---

## README.md

Include:
- One-line description
- Setup instructions
- Architecture: `HR Brief → JD Generator → Screener → Ranker → Shortlist Emails (x3) → HR Report → [HR Approves] → Offer Email`
- Tech stack

---

## What the Demo Proves

HR types two sentences. The system generates a job description, scores 5 candidates against it, sends shortlist emails to the top 3 automatically, emails a ranked report to HR, and sends a formal offer to the winner after one approval click. Five real emails fire. HR makes one decision. That's the workflow.
