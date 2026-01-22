import aiosmtplib
import asyncio

from email.message import EmailMessage
from src.logger import logger
from src.application.interfaces.services import EmailServiceInterface
from ..configs import EmailConfig


class AsyncEmailService(EmailServiceInterface):
    def __init__(self, conf: EmailConfig):
        self._conf = conf

    async def send_mail(self, to: str, topic: str, text: str):
        message = EmailMessage()
        message['From'] = self._conf.email_sender
        message['To'] = to
        message['Subject'] = topic
        message.set_content(text)
        asyncio.create_task(self._def_task(message))

    async def _def_task(self, msg: EmailMessage):
        async with aiosmtplib.SMTP(hostname=self._conf.email_host, port=self._conf.email_port, use_tls=True) as cli:
            await cli.login(self._conf.email_sender, self._conf.email_sender_password)
            try:
                await cli.send_message(msg)
                logger.info(f"Email with topic '{msg['Subject']}' sent to '{msg['To']}'")
            except Exception as e:
                logger.error(
                    f"Unable to send email with topic '{msg['Subject']}' to '{msg["To"]}': {e}")
