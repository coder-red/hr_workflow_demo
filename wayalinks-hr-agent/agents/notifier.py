import os
import resend


def _send_email(to: str, subject: str, body: str) -> None:
    resend.api_key = os.getenv("RESEND_API_KEY")
    print(f"SENDING EMAIL to={to} subject={subject}")
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to,
        "subject": subject,
        "text": body,
    })


def invite_shortlisted(state: dict) -> dict:
    if not state.get("shortlisted"):
        return {"shortlist_sent": False}
    for c in state["shortlisted"]:
        _send_email(
            to=c["email"],
            subject=f"You've been shortlisted — {state['job_description'].split(chr(10))[0]}",
            body=(
                f"Dear {c['name']},\n\n"
                f"Congratulations! Based on your application, you have been shortlisted "
                f"for the {state['job_description'].split(chr(10))[0]} position.\n\n"
                f"Our HR team will be in touch with the next steps shortly.\n\n"
                f"Best regards,\nWayalinks Recruitment Team"
            ),
        )
    return {"shortlist_sent": True}


def notify_hr(state: dict) -> dict:
    lines = ["Recruitment Update — Candidate Rankings Ready\n"]
    lines.append(f"Job: {state['job_description'].split(chr(10))[0]}\n")
    lines.append(f"{'Rank':<6}{'Name':<22}{'Score':<8}Reasoning")
    lines.append("-" * 80)
    for s in state["scores"]:
        lines.append(f"{s['rank']:<6}{s['name']:<22}{s['score']:<8}{s['reasoning']}")
    lines.append(
        "\nShortlist emails have already been sent to the top 3 candidates."
    )

    _send_email(
        to=state.get("hr_email") or os.getenv("HR_EMAIL"),
        subject="Recruitment Update — Candidate Rankings Ready",
        body="\n".join(lines),
    )
    return {"hr_notified": True}


def send_acceptance(state: dict) -> dict:
    winner = state["top_candidate"]
    _send_email(
        to=winner["email"],
        subject=f"Offer of Employment — {state['job_description'].split(chr(10))[0]}",
        body=(
            f"Dear {winner['name']},\n\n"
            f"Congratulations! We are pleased to inform you that you have been selected "
            f"for the {state['job_description'].split(chr(10))[0]} position at Wayalinks.\n\n"
            f"Official offer documents will follow shortly. Please confirm receipt of this email.\n\n"
            f"Welcome to the team!\n"
            f"Wayalinks HR Department"
        ),
    )
    return {"acceptance_sent": True}
