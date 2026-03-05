from pydantic import BaseModel, Field


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


class CurrentAttemptInfoDTO(BaseModel):
    problem_id: int
    module_id: int
    course_id: int
    problem_name: str
    course_name: str
    tests_passed: bool
    confirmed_passed: bool
    seen: bool
    pending: bool


class CurrentAttemptsInfoDTO(BaseModel):
    attempts_info: list[CurrentAttemptInfoDTO] = Field(default_factory=list)
    page: int
    pages: int
