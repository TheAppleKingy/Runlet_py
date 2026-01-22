from typing import Optional

from pydantic import BaseModel


class UserG1(BaseModel):
    id: int
    name: str


class UserG2(BaseModel):
    name: str
    email: str


class UserG3(BaseModel):
    name: str
