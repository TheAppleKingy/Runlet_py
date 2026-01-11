from typing import Protocol


class EmailServiceInterface(Protocol):
    async def send_mail(self, to: str, topic: str, text: str) -> str: ...
