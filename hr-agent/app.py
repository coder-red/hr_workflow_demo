from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from agents.jd_generator import generate_jd
from agents.screener import score_candidates
from agents.ranker import rank_candidates
from agents.notifier import notify_hr
from data.candidates import MOCK_CANDIDATES

DEFAULT_STATE = {
    "stage": 0,
    "graph_started": False,
    "job_description": "",
    "scores": [],
    "shortlisted": [],
    "top_candidate": {},
    "shortlist_invited": False,
    "offer_sent": False,
    "hr_notified": False,
    "hr_email": "",
}

for key, val in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = val

PIPELINE_STAGES = [
    "Generate JD",
    "Score & Rank",
    "Invite",
    "Offer",
    "Notify HR",
    "Done",
]

st.set_page_config(page_title="HR Recruitment Demo", layout="wide")
st.title("HR Recruitment Automation Demo")

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


# STAGE 0 — Generate JD
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


# STAGE 1 — Score & Rank
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


# STAGE 2 — Invite Shortlisted (simulated)
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

    st.subheader("Invite Shortlisted Candidates?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Yes, send invitations", type="primary"):
            st.session_state.shortlist_invited = True
            st.session_state.stage = 3
            st.rerun()
    with col2:
        if st.button("✗ Skip"):
            st.session_state.shortlist_invited = False
            st.session_state.stage = 3
            st.rerun()


# STAGE 3 — Send Offer (simulated)
if st.session_state.stage == 3:
    if st.session_state.shortlist_invited:
        st.success("✉️ Invitation emails sent to shortlisted candidates (simulated)")
    else:
        st.info("⏭️ Shortlist invitations skipped")

    tc = st.session_state.top_candidate
    if tc:
        st.subheader(f"Top Candidate: **{tc.get('name', '-')}**")
        st.write(f"Score: **{tc.get('score', 0)}/100**")
        st.write(tc.get("reasoning", ""))

    st.subheader("Send Offer Letter?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Yes, send offer", type="primary"):
            st.session_state.offer_sent = True
            st.session_state.stage = 4
            st.rerun()
    with col2:
        if st.button("✗ Skip"):
            st.session_state.offer_sent = False
            st.session_state.stage = 4
            st.rerun()


# STAGE 4 — Notify HR (actual email)
if st.session_state.stage == 4:
    if st.session_state.offer_sent:
        st.success(f"✉️ Offer sent to **{st.session_state.top_candidate.get('name', '')}** (simulated)")
    else:
        st.info("⏭️ Offer skipped")

    st.subheader("Notify HR with Full Report")
    st.write("Send the ranking report to your email.")

    if st.button("Send Report to My Email", type="primary"):
        if not st.session_state.hr_email:
            st.warning("Enter your email in the sidebar first.")
            st.stop()
        with st.spinner("Sending ranking report..."):
            state = {
                "job_description": st.session_state.job_description,
                "scores": st.session_state.scores,
                "hr_email": st.session_state.hr_email,
            }
            state.update(notify_hr(state))
            st.session_state.hr_notified = state["hr_notified"]
            st.session_state.hr_notified_simulated = state.get("hr_notified_simulated", False)
            st.session_state.hr_error_reason = state.get("error_reason", "")
            st.session_state.stage = 5
        st.rerun()


# STAGE 5 — Done
if st.session_state.stage == 5:
    st.success("## Pipeline Complete")

    if st.session_state.get("hr_notified_simulated"):
        err = st.session_state.get("hr_error_reason", "")
        st.warning(f"⚠️ Report email **failed**")
        st.code(err, language="text")
    else:
        st.info(f"✅ Ranked report sent to **{st.session_state.hr_email}**")

    st.subheader("Summary")
    parts = [f"- **{len(st.session_state.scores)}** candidates scored and ranked"]
    if st.session_state.shortlist_invited:
        parts.append("- ✉️ Shortlist invitations sent (simulated)")
    else:
        parts.append("- ⏭️ Shortlist invitations skipped")
    if st.session_state.offer_sent:
        parts.append(f"- ✉️ Offer sent to **{st.session_state.top_candidate.get('name', '')}** (simulated)")
    else:
        parts.append("- ⏭️ Offer skipped")
    parts.append(f"- 📧 Report emailed to HR\n**Job:** {st.session_state.job_description.split(chr(10))[0]}")

    st.markdown("\n".join(parts))

    if st.button("Start Over"):
        for key in DEFAULT_STATE:
            st.session_state[key] = DEFAULT_STATE[key]
        st.rerun()
