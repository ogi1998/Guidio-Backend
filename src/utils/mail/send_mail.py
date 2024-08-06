import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from core.settings import DEFAULT_FROM_EMAIL
from src import config

logging.basicConfig(level=logging.DEBUG)

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME if config.MAIL_USERNAME else '',
    MAIL_FROM=str(config.MAIL_FROM) if config.MAIL_FROM else DEFAULT_FROM_EMAIL,
    MAIL_PASSWORD=config.MAIL_PASSWORD if config.MAIL_PASSWORD else '',
    MAIL_SERVER=config.MAIL_SERVER if config.MAIL_SERVER else '',
    MAIL_PORT=config.MAIL_PORT if config.MAIL_PORT else 587,
    MAIL_STARTTLS=config.MAIL_STARTTLS if config.MAIL_STARTTLS else True,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS if config.MAIL_SSL_TLS else False,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / 'templates/mail/',
    SUPPRESS_SEND=config.SUPPRESS_SEND if config.SUPPRESS_SEND else 0,
)


async def send_mail(subject: str, recipients: list[EmailStr], body: Dict[str, Any],
                    template_name: str) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=body,
        subtype=MessageType.html,
    )
    try:
        fm = FastMail(conf)
        await fm.send_message(message, template_name=template_name)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Sending email failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sending email failed"
        )
