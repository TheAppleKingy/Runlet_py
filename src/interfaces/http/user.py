from fastapi import APIRouter, Depends

from src.container import auth_user


user_router = APIRouter(prefix="/me")


@user_router.get("/main")
async def get_main(user_id: int = Depends(auth_user)):
    pass
