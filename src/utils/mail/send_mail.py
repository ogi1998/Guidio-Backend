from pathlib import Path
from typing import Dict, Any

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from core.settings import DEFAULT_FROM_EMAIL
from src import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_FROM=str(config.MAIL_FROM) if config.MAIL_FROM else DEFAULT_FROM_EMAIL,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / 'templates/mail/',
    SUPPRESS_SEND=1,
)


def send_mail(recipients: list[EmailStr], body: Dict[str, Any], template_name: str) -> None:
    message = MessageSchema(
        subject="Activation email",
        recipients=recipients,
        template_body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    fm.send_message(message, template_name=template_name)
