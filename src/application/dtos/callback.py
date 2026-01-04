from pydantic import BaseModel


class CodeRunCallbackDTO(BaseModel):
    test_num: int
