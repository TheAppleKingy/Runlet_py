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


class UserWithSeenDTO(UserG1):
    seen: bool


class UserG4(UserWithSeenDTO):
    tests_passed: bool
    confirmed_passed: bool
