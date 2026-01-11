from pydantic import BaseModel


class MyProfileDTO(BaseModel):
    id: int
    name: str
