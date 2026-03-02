"""
Gmail SMTP Sender — free, 500 emails/day.
Uses plain text only (HTML looks like spam).

Setup:
1. myaccount.google.com → Security → 2-Step Verification → App Passwords
2. Create app password for "Mail" → get 16-character password
3. Put that password in GMAIL_APP_PASSWORD env var
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings

settings = get_settings()


def send_outreach_email(
    to_email: str, subject: str, body: str, from_name: str
) -> bool:
    """
    Send a plain-text email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    if not settings.gmail_address or not settings.gmail_app_password:
        print("Gmail credentials not configured")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{settings.gmail_address}>"
        msg["To"] = to_email

        # Plain text only — HTML triggers spam filters
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.gmail_address, settings.gmail_app_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
