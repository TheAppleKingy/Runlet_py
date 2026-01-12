from pydantic import BaseModel


class SendProblemSolutionDTO(BaseModel):
    code: str
    lang: str


class ProblemForStudentDTO(BaseModel):
    id: int
    name: str
    description: str


class ModuleForStudenteDTO(BaseModel):
    id: int
    name: str
    problems: list[ProblemForStudentDTO] = []


class GetCourseProblemsForStudentDTO(BaseModel):
    modules: list[ModuleForStudenteDTO] = []
