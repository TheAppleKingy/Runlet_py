from typing import Optional

from fastapi import APIRouter, Query
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.application.use_cases.user import (
    ShowCourse,
    ShowMain,
    CreateCourse,
    RequestSubscribeOnCourse,
    SubscribeOnCourseByLink,
    SubscribeOnCourse
)
from src.domain.value_objects import AuthenticatedUserId, AuthenticatedNotStrictlyUserId
from src.application.dtos.main import MainDTO
from src.application.dtos.course import (
    CourseG2,
    CourseG5,
    CourseC1
)
from src.logger import logger

user_router = APIRouter(prefix="/me", route_class=DishkaRoute)


@user_router.get("/main", response_model=MainDTO)
async def get_main(
    user_id: FromDishka[AuthenticatedNotStrictlyUserId],
    use_case: FromDishka[ShowMain],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=10)
) -> MainDTO:
    data = await use_case.execute(user_id, page=page, size=size)
    return {  # type: ignore
        "as_teacher": data[0],
        "as_student": data[1],
        "paginated": {
            "courses": data[2][0],
            "page": data[2][1],
            "size": data[2][2],
            "total": data[2][3]
        }
    }


@user_router.get("/course/{course_id}")
async def get_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedNotStrictlyUserId],
    use_case: FromDishka[ShowCourse]
) -> Optional[CourseG2]:
    return await use_case.execute(course_id)


@user_router.post("/course")
async def create_course(
    dto: CourseC1,
    user_id: FromDishka[AuthenticatedUserId],
    use_case: FromDishka[CreateCourse]
):
    return await use_case.execute(user_id, dto)


@user_router.get("/course/{course_id}/subscribe/request")
async def request_subscribe(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    use_case: FromDishka[RequestSubscribeOnCourse]
):
    return await use_case.execute(course_id, user_id)


@user_router.get("/course/subscribe/{inviting_token}")
async def subscribe_by_link(
    inviting_token: str,
    user_id: FromDishka[AuthenticatedUserId],
    use_case: FromDishka[SubscribeOnCourseByLink]
):
    return await use_case.execute(inviting_token, user_id)


@user_router.get("/course/{course_id}/subscribe")
async def subscribe_on_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    use_case: FromDishka[SubscribeOnCourse]
):
    return await use_case.execute(user_id, course_id)
