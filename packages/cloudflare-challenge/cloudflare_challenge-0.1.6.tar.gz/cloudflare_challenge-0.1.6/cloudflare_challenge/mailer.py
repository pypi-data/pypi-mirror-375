# Import smtplib for the actual sending function
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from flask import current_app


def sendmail(
    html: str,
) -> bool:
    mailhost = current_app.config.get("MAIL_SERVER")
    you = current_app.config.get("CF_MAIL_RECIPIENT")
    if mailhost is None or you is None:
        return False
    port = current_app.config.get("MAIL_PORT")
    if port and ":" not in mailhost:
        mailhost = f"{mailhost}:{port}"
    subject: str = "Cloudflare Challenge"
    me: str = current_app.config.get(
        "MAIL_DEFAULT_SENDER",
        "cloudflare.challenge@flask.org",
    )
    msg = MIMEText(html, "html")

    msg["Subject"] = subject
    msg["From"] = me
    msg["To"] = you

    with smtplib.SMTP() as s:
        s.connect(mailhost)
        s.sendmail(me, [you], msg.as_string())
    return True
