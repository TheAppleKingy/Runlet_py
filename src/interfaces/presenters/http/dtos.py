from pydantic import BaseModel


class ProblemWithRateInfoDTO(BaseModel):
    id: int
    name: str
    tests_passed: bool


class ModuleWithRateInfoDTO(BaseModel):
    name: str
    order: int
    problems: list[ProblemWithRateInfoDTO] = []
