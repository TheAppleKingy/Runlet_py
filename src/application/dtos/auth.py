from pydantic import BaseModel, EmailStr, Field


class LoginUserDTO(BaseModel):
    email: EmailStr
    password: str


class RegisterUserRequestDTO(BaseModel):
    name: str = Field(max_length=100, min_length=1)
    email: EmailStr
    first_password: str
    second_password: str
