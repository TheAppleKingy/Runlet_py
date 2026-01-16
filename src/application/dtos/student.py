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
    problems: list[ProblemForStudentDTO]


class CourseForStudentDTO(BaseModel):
    id: int
    name: str
    description: str
    modules: list[ModuleForStudenteDTO]
