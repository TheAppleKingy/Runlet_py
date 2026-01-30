from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.domain.value_objects import AuthenticatedUserId
from src.application.dtos.auth import RegisterUserRequestDTO, LoginUserDTO
from src.application.use_cases import *


auth_router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@auth_router.post("/registration/request", response_model=None)
async def registration_request(
    dto: RegisterUserRequestDTO,
    use_case: FromDishka[RegisterUserRequest]
):
    await use_case.execute(dto)
    return {"detail": "Email with instructions to confirm registration was sent"}


@auth_router.get("/registration/confirm/{token}")
async def registration_confirm(
    token: str,
    use_case: FromDishka[RegisterUserConfirm]
) -> None:
    return await use_case.execute(token)


@auth_router.post("/login")
async def login(
    dto: LoginUserDTO,
    use_case: FromDishka[LoginUser],
    token: str = Cookie(default=None, include_in_schema=False)
):
    token = await use_case.execute(dto)
    resp = JSONResponse({"detail": "Logged in"})
    resp.set_cookie("token", token)
    return resp


@auth_router.get("/logout")
async def logout(user_id: FromDishka[AuthenticatedUserId]):
    resp = JSONResponse({"detail": "Logged out"})
    resp.delete_cookie("token")
    return resp
