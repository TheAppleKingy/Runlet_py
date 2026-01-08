from typing import Protocol


class EmailServiceInterface(Protocol):
    async def send_mail(self, to: str, topic: str, message: str) -> str: ...
