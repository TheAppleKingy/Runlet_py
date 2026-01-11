from fastapi import APIRouter, Depends

from src.container import (
    auth_user
)

user_router = APIRouter(prefix="/me", tags=["User endpoints"])


@user_router.get("/profile")
async def my_profile(user_id: int = Depends(auth_user), use_case=None):
    pass


@user_router.get("/courses")
async def get_my_courses(user_id: int = Depends(auth_user)):
    pass
