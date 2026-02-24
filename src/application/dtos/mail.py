from pydantic import BaseModel


class SendMailDTO(BaseModel):
    to: str
    topic: str
    message: str
