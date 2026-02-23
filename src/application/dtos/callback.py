from pydantic import BaseModel


from .problem import TestCaseDTO


class ResultDTO(BaseModel):
    test_cases: list[TestCaseDTO]
    err_msg: str
