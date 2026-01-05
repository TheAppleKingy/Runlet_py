from fastapi import APIRouter, Depends

from application.dtos.auth import RegisterUserRequestDTO
from application.use_cases.user import *


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration/request")
async def registration_request(dto: RegisterUserRequestDTO, use_case: RegisterUserConfirm = Depends()):
    pass
