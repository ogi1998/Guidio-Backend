# To start a local smtp debugging server, run in terminal:
# python -m smtpd -c DebuggingServer -n localhost:1025

import smtplib
from email.message import EmailMessage

from core.settings import DEFAULT_FROM_EMAIL


def send_mail(subject: str, recipients: list[str], text_content: str = '', html_content: str = '',
              from_email: str = None) -> None:
    msg = EmailMessage()
    port = 1025
    smtp_server = "localhost"
    msg["Subject"] = subject
    msg["From"] = from_email if from_email is not None else DEFAULT_FROM_EMAIL
    msg["To"] = recipients

    msg.set_content(text_content)

    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP(smtp_server, port) as server:
        server.send_message(msg)
