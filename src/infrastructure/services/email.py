from aiosmtplib import SMTP

from email.message import EmailMessage

from ..configs import email_conf


class AsyncEmailService:
    async def send_mail(self, to: str, topic: str, message: str) -> str:
        client = SMTP(
            hostname=email_conf.email_host,
            port=email_conf.email_port,
            use_tls=True,
        )
        message = EmailMessage()
        message['From'] = email_conf.email_sender
        message['To'] = to
        message['Subject'] = topic
        message.set_content(message)
        await client.send_message()
        async with client as smtp:
            smtp.login(email_conf.email_sender, email_conf.email_sender_password)
            await smtp.send_message(message)
