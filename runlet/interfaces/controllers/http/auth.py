from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from runlet.domain.value_objects import AuthenticatedUserId
from runlet.application.dtos.auth import (
    RegisterUserRequestDTO,
    LoginUserDTO,
    ChangePasswordRequestDTO,
    ChangePasswordConfirmDTO
)
from runlet.application.interactors import (
    RegisterUserRequest,
    RegisterUserConfirm,
    LoginUser,
    ChangePasswordRequest,
    ChangePasswordConfirm
)


auth_router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@auth_router.post("/registration/request", response_model=None)
async def registration_request(
    dto: RegisterUserRequestDTO,
    interactor: FromDishka[RegisterUserRequest]
):
    await interactor(dto)
    return {"detail": "Email with instructions to confirm registration was sent"}


@auth_router.get("/registration/confirm/{token}")
async def registration_confirm(
    token: str,
    interactor: FromDishka[RegisterUserConfirm]
) -> None:
    return await interactor(token)


@auth_router.post("/login")
async def login(
    dto: LoginUserDTO,
    interactor: FromDishka[LoginUser],
    token: str = Cookie(default=None, include_in_schema=False)
):
    token = await interactor(dto)
    resp = JSONResponse({"detail": "Logged in"})
    resp.set_cookie("token", token)
    return resp


@auth_router.get("/logout")
async def logout(user_id: FromDishka[AuthenticatedUserId]):
    resp = JSONResponse({"detail": "Logged out"})
    resp.delete_cookie("token")
    return resp


@auth_router.post("/change_password/request")
async def request_change_password(
    dto: ChangePasswordRequestDTO,
    interactor: FromDishka[ChangePasswordRequest]
):
    await interactor(dto.email)
    return {"detail": "Email with instructions sent"}


@auth_router.post("/change_password/confirm/{token}")
async def confirm_change_password(
    token: str,
    dto: ChangePasswordConfirmDTO,
    interactor: FromDishka[ChangePasswordConfirm]
):
    await interactor(token, dto)
    return {"detail": "Password changed successfuly"}
