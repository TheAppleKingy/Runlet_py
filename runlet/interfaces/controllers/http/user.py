from fastapi import APIRouter, Query
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from runlet.application.interactors import (
    ShowCourse,
    ShowMain,
    CreateCourse,
    RequestSubscribeOnCourse,
    SubscribeOnCourseByLink,
    SubscribeOnCourse,
    ShowMyProfile,
    ShowFavourites,
    AddToFavourites
)
from runlet.domain.interfaces.types import (
    AuthenticatedUserId,
    AuthenticatedNotStrictlyUserId
)
from runlet.application.dtos.main import MainDTO
from runlet.application.dtos.course import (
    CourseG2,
    CourseCreateDTO
)
from runlet.application.dtos.user import UserG2

user_router = APIRouter(prefix="/me", route_class=DishkaRoute)


@user_router.get("/main", response_model=MainDTO)
async def get_main(
    user_id: FromDishka[AuthenticatedNotStrictlyUserId],
    interactor: FromDishka[ShowMain],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=10)
) -> MainDTO:
    data = await interactor(user_id, page=page, size=size)
    return {  # type: ignore
        "as_teacher": data[0],
        "as_student": data[1],
        "paginated": {
            "courses": data[2][0] if data[2] else [],
            "page": data[2][1] if data[2] else 0,
            "size": data[2][2] if data[2] else 0,
            "total": data[2][3] if data[2] else 0
        }
    }


@user_router.get("/profile")
async def get_my_profile(
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[ShowMyProfile],
) -> UserG2:
    return await interactor(user_id)


@user_router.get("/course/{course_id}")
async def get_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedNotStrictlyUserId],
    interactor: FromDishka[ShowCourse]
) -> CourseG2:
    return await interactor(course_id)


@user_router.post("/course")
async def create_course(
    dto: CourseCreateDTO,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[CreateCourse]
):
    return await interactor(user_id, dto)


@user_router.get("/course/{course_id}/subscribe/request")
async def request_subscribe(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[RequestSubscribeOnCourse]
):
    return await interactor(course_id, user_id)


@user_router.get("/course/subscribe/{inviting_token}")
async def subscribe_by_link(
    inviting_token: str,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[SubscribeOnCourseByLink]
):
    return await interactor(inviting_token, user_id)


@user_router.get("/course/{course_id}/subscribe")
async def subscribe_on_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[SubscribeOnCourse]
):
    return await interactor(user_id, course_id)


@user_router.get("/courses/favourites")
async def get_favourites(
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[ShowFavourites]
) -> list[CourseG2]:
    return await interactor(user_id)  # type: ignore[return-value]


@user_router.post("/courses/{course_id}/favourites")
async def add_favourites(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[AddToFavourites]
) -> None:
    await interactor(user_id, course_id)
