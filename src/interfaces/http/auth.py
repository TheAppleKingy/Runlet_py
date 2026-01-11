from fastapi import APIRouter, Depends, Cookie
from fastapi.responses import JSONResponse, RedirectResponse

from src.application.dtos.auth import RegisterUserRequestDTO, LoginUserDTO
from src.application.use_cases import *

from src.container import (
    auth_user,
    get_register_request_usecase,
    get_register_confirm_usecase,
    get_login_usecase
)
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration/request")
async def registration_request(dto: RegisterUserRequestDTO, use_case: RegisterUserRequest = Depends(get_register_request_usecase)):
    await use_case.execute(dto)
    return {"detail": "Email with instructions to confirm registration was sent"}


@auth_router.get("/registration/confirm/{token}")
async def registration_confirm(token: str, use_case: RegisterUserConfirm = Depends(get_register_confirm_usecase)):
    await use_case.execute(token)
    resp = RedirectResponse(url="http://localhost:8000/api/v1/auth/login", status_code=302)
    resp.delete_cookie("token")
    return resp


@auth_router.post("/login")
async def login(dto: LoginUserDTO, use_case: LoginUser = Depends(get_login_usecase), token: str = Cookie(default=None, include_in_schema=False)):
    if token:
        return {"detail": "Alreeady logged in"}
    token = await use_case.execute(dto)
    resp = JSONResponse({"detail": "Logged in"})
    resp.set_cookie("token", token)
    return resp


@auth_router.get("/logout")
async def logout(user_id: int = Depends(auth_user)):
    resp = JSONResponse({"detail": "Logged out"})
    resp.delete_cookie("token")
    return resp
