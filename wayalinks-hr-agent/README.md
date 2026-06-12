# HR Recruitment Automation Demo

A LangGraph-powered HR recruitment pipeline. HR enters a 2-line brief, the system generates a full JD, scores 5 candidates, emails the top 3 a shortlist notification, emails a ranked report to HR, and after HR approves, fires a formal acceptance to the winner. All emails are real (Resend).

## Architecture

```
HR Brief → JD Generator (Groq) → Screener (Groq) → Ranker (sort)
  → Shortlist Emails (x3) → HR Report → [HR Approves] → Offer Email
```

## Tech Stack

- **Orchestration:** LangGraph (stateful graph with interrupt/resume)
- **LLM:** Groq — `llama-3.3-70b-versatile`
- **Email:** Resend
- **UI:** Streamlit
- **State:** In-memory + LangGraph MemorySaver

## Setup

```bash
cp .env.example .env
# Edit .env with your Groq API key, Resend API key, and HR email

pip install -r requirements.txt
streamlit run app.py
```

## How to Demo

1. Open your Gmail inbox on a second screen (use `youremail+alias@gmail.com` aliases)
2. Enter a 1-3 sentence job brief in the Streamlit app
3. Click through the pipeline stages
4. After HR approval, watch the acceptance email arrive in real time

## What It Proves

- HR types two sentences → full JD generated
- 5 candidates scored and ranked automatically
- 3 shortlist emails fire without human intervention
- HR receives a ranked report
- HR clicks one button → formal offer sent
- 5 real emails total, 1 HR decision, 0 manual steps
