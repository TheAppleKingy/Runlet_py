from .test_case import TestCases


class Problem:
    def __init__(
        self,
        id_: int = None,
        name: str = "",
        description: str = "",
        course_id: int = None,
        test_cases: TestCases = None,
    ):
        self.id = id_
        self.name = name
        self.description = description
        self.course_id = course_id
        self.test_cases = test_cases if test_cases is not None else TestCases()
