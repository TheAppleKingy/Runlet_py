import aiosmtplib
import asyncio

from email.message import EmailMessage
from src.logger import logger
from src.application.interfaces.services import EmailServiceInterface
from ..configs import email_conf


class AsyncEmailService(EmailServiceInterface):
    async def send_mail(self, to: str, topic: str, text: str):
        message = EmailMessage()
        message['From'] = email_conf.email_sender
        message['To'] = to
        message['Subject'] = topic
        message.set_content(text)
        asyncio.create_task(self._def_task(message))

    async def _def_task(self, msg: EmailMessage):
        async with aiosmtplib.SMTP(hostname=email_conf.email_host, port=email_conf.email_port, use_tls=True) as cli:
            await cli.login(email_conf.email_sender, email_conf.email_sender_password)
            try:
                await cli.send_message(msg)
                logger.info(f"Email with registration confirm link was sent to {msg["To"]}")
            except Exception as e:
                logger.error(f"Unable to send email for {msg["To"]}: {e}")
