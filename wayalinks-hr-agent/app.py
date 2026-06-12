from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from agents.jd_generator import generate_jd
from agents.screener import score_candidates
from agents.ranker import rank_candidates
from agents.notifier import invite_shortlisted, notify_hr, send_acceptance
from data.candidates import MOCK_CANDIDATES

DEFAULT_STATE = {
    "stage": 0,
    "graph_started": False,
    "job_description": "",
    "scores": [],
    "shortlisted": [],
    "top_candidate": {},
    "shortlist_sent": False,
    "hr_notified": False,
    "acceptance_sent": False,
    "hr_email": "",
}

for key, val in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = val

PIPELINE_STAGES = [
    "Generate JD",
    "Score Candidates",
    "Shortlist Top 3",
    "Notify HR",
    "HR Review",
    "Offer Sent",
]

st.set_page_config(page_title="HR Recruitment Demo", layout="wide")
st.title("Wayalinks — HR Recruitment Automation Demo")

with st.sidebar:
    st.subheader("HR Email for Notifications")
    hr_email = st.text_input(
        "Enter your email address",
        value=st.session_state.get("hr_email", ""),
        placeholder="hr@company.com",
        key="hr_email_input",
    )
    if hr_email:
        st.session_state.hr_email = hr_email
    elif "hr_email" not in st.session_state:
        st.session_state.hr_email = ""
    if st.session_state.hr_email:
        st.success(f"Notifications will go to **{st.session_state.hr_email}**")
    else:
        st.warning("Enter your email above to receive notifications.")


def stage_style(idx: int) -> str:
    return "✅" if idx < st.session_state.stage else "⬜"


cols = st.columns(len(PIPELINE_STAGES))
for i, label in enumerate(PIPELINE_STAGES):
    icon = stage_style(i)
    cols[i].markdown(f"**{icon} {label}**")
st.divider()


# STAGE 0
if st.session_state.stage == 0:
    st.subheader("Describe the role you're hiring for")
    job_brief = st.text_area(
        "Enter a 1-3 sentence job brief",
        placeholder="e.g. We need a senior frontend engineer with React experience for our payments team...",
        height=100,
    )
    if st.button("Generate Job Description", type="primary"):
        if not job_brief.strip():
            st.warning("Please enter a job brief first.")
            st.stop()

        with st.spinner("Generating job description..."):
            result = generate_jd({"job_brief": job_brief})
            st.session_state.job_description = result["job_description"]
            st.session_state.graph_started = True
            st.session_state.stage = 1
        st.rerun()


# STAGE 1
if st.session_state.stage == 1:
    st.subheader("Generated Job Description")
    with st.expander("View full JD", expanded=True):
        st.write(st.session_state.job_description)

    st.subheader("Candidate Pool")
    for c in MOCK_CANDIDATES:
        st.markdown(f"- **{c['name']}** — {c['experience_years']} years experience")

    if st.button("Analyse All Candidates", type="primary"):
        with st.spinner("Scoring and ranking candidates..."):
            state = {
                "job_description": st.session_state.job_description,
                "candidates": MOCK_CANDIDATES,
            }
            state.update(score_candidates(state))
            state.update(rank_candidates(state))
            st.session_state.scores = state["scores"]
            st.session_state.shortlisted = state["shortlisted"]
            st.session_state.top_candidate = state["top_candidate"]
            st.session_state.stage = 2
        st.rerun()


# STAGE 2
if st.session_state.stage == 2:
    st.subheader("Candidate Rankings")

    if st.session_state.scores:
        rows = []
        for s in st.session_state.scores:
            is_shortlisted = s.get("rank", 999) <= 3
            name_display = f"⭐ {s['name']}" if is_shortlisted else s["name"]
            rows.append(
                {
                    "Rank": s.get("rank", "-"),
                    "Name": name_display,
                    "Score": f"{s['score']}/100",
                    "Reasoning": s["reasoning"],
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("⭐ = Shortlisted (top 3)")

    if st.button("Shortlist Top 3 & Notify HR", type="primary"):
        with st.spinner("Sending shortlist and HR report emails..."):
            state = {
                "job_description": st.session_state.job_description,
                "shortlisted": st.session_state.shortlisted,
                "scores": st.session_state.scores,
                "hr_email": st.session_state.hr_email,
            }
            state.update(invite_shortlisted(state))
            state.update(notify_hr(state))
            st.session_state.shortlist_sent = state["shortlist_sent"]
            st.session_state.hr_notified = state["hr_notified"]
            st.session_state.stage = 3
        st.rerun()


# STAGE 3
if st.session_state.stage == 3:
    tc = st.session_state.top_candidate
    if tc:
        st.subheader("Top Candidate — Ready for Approval")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Name", tc.get("name", "-"))
            st.metric("Score", f"{tc.get('score', 0)}/100")
        with col2:
            st.write("**Reasoning**")
            st.write(tc.get("reasoning", ""))

    st.info("✅ Shortlist emails sent to top 3 candidates")
    st.info("✅ Ranked report emailed to HR")

    st.subheader("HR Action Required")
    st.write("Review the results above. Approve to send the formal offer letter.")
    if st.button("Approve & Send Offer", type="primary"):
        with st.spinner("Sending acceptance email..."):
            state = {
                "job_description": st.session_state.job_description,
                "top_candidate": st.session_state.top_candidate,
            }
            state.update(send_acceptance(state))
            st.session_state.acceptance_sent = state["acceptance_sent"]
            st.session_state.stage = 4
        st.rerun()


# STAGE 4
if st.session_state.stage == 4:
    st.success("## Pipeline Complete")
    tc = st.session_state.top_candidate
    st.markdown(
        f"### ✅ Offer sent to **{tc.get('name', 'the selected candidate')}**"
    )

    st.divider()
    st.subheader("Pipeline Summary")
    st.markdown(
        f"""
- **5 real emails fired** via Resend
  - 3 shortlist notifications to top candidates
  - 1 ranked report to HR
  - 1 formal acceptance to the winner
- **1 HR decision** — the Approve button
- **0 manual steps** besides that

**Job:** {st.session_state.job_description.split(chr(10))[0]}
        """
    )

    if st.button("Start Over"):
        for key in DEFAULT_STATE:
            st.session_state[key] = DEFAULT_STATE[key]
        st.rerun()
