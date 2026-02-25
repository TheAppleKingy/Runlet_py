from pydantic import BaseModel


from .problem import TestCaseDTO


class ResultDTO(BaseModel):
    test_cases: list[TestCaseDTO]
    err_msg: str
    problem_id: int
    student_id: int
    course_id: int
    code: str
