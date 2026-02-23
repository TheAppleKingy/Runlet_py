from pydantic import BaseModel


class UserG1(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserG2(BaseModel):
    id: int
    name: str
    email: str


class UserG3(BaseModel):
    name: str
