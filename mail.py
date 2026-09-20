#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Email the filtered dba.dk results."""

import os
import smtplib
import sys
from email.message import EmailMessage


def send(subject: str, body: str) -> None:
    """Send a plain text email with SMTP credentials from the environment."""
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.environ["MAIL_FROM"]
    message["To"] = os.environ["MAIL_TO"]
    message.set_content(body)
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)


def main() -> None:
    """Read the LLM output from stdin and email it."""
    results = sys.stdin.read().strip()
    send("dba.dk finder", f"Hello,\n\nThese results may be interesting:\n\n{results}\n")


if __name__ == "__main__":
    main()
