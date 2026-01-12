from pydantic import BaseModel


class CourseForStudentDTO(BaseModel):
    id: int
    name: str
    description: str
