from pydantic import BaseModel


class SendProblemSolutionDTO(BaseModel):
    code: str
    lang: str
