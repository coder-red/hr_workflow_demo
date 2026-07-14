import os
import json
import urllib.request
import urllib.error


AISEND_URL = "https://api.aisend.app/api/v1/emails"


def _send_email(to: str, subject: str, body: str) -> tuple[bool, str]:
    api_key = os.getenv("AISEND_API_KEY")
    if not api_key:
        return False, "AISEND_API_KEY not set in .env"

    payload = json.dumps({
        "from": "hello@send.aisend.app",
        "to": to,
        "subject": subject,
        "text": body,
    }).encode()

    req = urllib.request.Request(
        AISEND_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 201:
                print(f"  ✅ EMAIL SENT to={to} subject={subject}")
                return True, ""
            body = resp.read().decode()
            print(f"  ⚠️  EMAIL FAILED to={to} status={resp.status}: {body}")
            return False, body
    except urllib.error.HTTPError as e:
        reason = e.read().decode()
        print(f"  ⚠️  EMAIL FAILED to={to} HTTP {e.code}: {reason}")
        return False, reason
    except Exception as e:
        print(f"  ⚠️  EMAIL FAILED to={to}: {e}")
        return False, str(e)


# ============================================================
# PREVIOUS VERSIONS (commented for reference)
# ============================================================

# --- Gmail SMTP ---
# import smtplib
# from email.message import EmailMessage
# def _send_email(to, subject, body):
#     sender = os.getenv("SENDER_EMAIL")
#     password = os.getenv("SENDER_PASSWORD")
#     ...
#     server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
#     server.login(sender, password)
#     server.send_message(msg)

# --- Brevo API ---
# BREVO_URL = "https://api.brevo.com/v3/smtp/email"
# ...
# headers = {"api-key": api_key, "Content-Type": "application/json"}
# payload = {"sender": {"email": sender_email}, "to": [{"email": to}], ...}

# --- Ethereal (fake SMTP for testing) ---
# def _get_ethereal_creds():
#     req = urllib.request.Request("https://api.nodemailer.com/user", data=b"", ...)
#     ... returns user, pass ...
# server = smtplib.SMTP("smtp.ethereal.email", 587)
# server.login(user, password)

# --- Resend API ---
# import resend
# resend.api_key = os.getenv("RESEND_API_KEY")
# resend.Emails.send({"from": "...", "to": to, ...})


def notify_hr(state: dict) -> dict:
    lines = ["Recruitment Update — Candidate Rankings Ready\n"]
    lines.append(f"Job: {state['job_description'].split(chr(10))[0]}\n")
    lines.append(f"{'Rank':<6}{'Name':<22}{'Score':<8}Reasoning")
    lines.append("-" * 80)
    for s in state["scores"]:
        lines.append(f"{s['rank']:<6}{s['name']:<22}{s['score']:<8}{s['reasoning']}")

    sent, reason = _send_email(
        to=state.get("hr_email") or os.getenv("HR_EMAIL"),
        subject="Recruitment Update — Candidate Rankings Ready",
        body="\n".join(lines),
    )
    return {"hr_notified": True, "hr_notified_simulated": not sent, "error_reason": reason}
