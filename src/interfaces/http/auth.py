from fastapi import APIRouter, Depends, Cookie
from fastapi.responses import JSONResponse, RedirectResponse

from application.dtos.auth import RegisterUserRequestDTO
from application.use_cases.user import *

from container import (
    auth_user,
    get_register_request_usecase,
    get_register_confirm_usecase
)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration/request")
async def registration_request(dto: RegisterUserRequestDTO, use_case: RegisterUserRequest = Depends(get_register_request_usecase)):
    await use_case.execute(dto)
    resp = JSONResponse({"detail": "Email with instructions to confirm registration was sent"})
    return resp


@auth_router.get("/registration/confirm")
async def registration_confirm(use_case: RegisterUserConfirm = Depends(get_register_confirm_usecase), token: str = Cookie(default=None, include_in_schema=False)):
    await use_case.execute(token)
    resp = RedirectResponse(url="http://localhost:8000/api/v1/auth/login", status_code=302)
    resp.delete_cookie("token")
    return resp


@auth_router.get("/logout")
async def logout(user_id: int = Depends(auth_user)):
    print("allahu akbarr")
    return {"det": "ok"}
