from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.application.use_cases.user import (
    ShowCourse,
    ShowMain,
    CreateCourse,
    RequestSubscribeOnCourse,
    SubscribeOnCourseByLink,
    SubscribeOnCourse
)
from src.application.dtos.user import MainDTO
from src.application.dtos.course import (
    PaginatedCoursesDTO,
    CourseForUnauthorizedDTO,
    CreateCourseDTO
)
from src.container import (
    auth_user,
    get_show_main_use_case,
    auth_user_no_raise,
    get_show_course_use_case,
    get_create_course_use_case,
    get_request_sub_use_case,
    get_sub_by_link_use_case,
    get_sub_course_use_case
)
from src.logger import logger

user_router = APIRouter(prefix="/me")


@user_router.get("/main", response_model=MainDTO)
async def get_main(
    user_id: Optional[int] = Depends(auth_user_no_raise),
    use_case: ShowMain = Depends(get_show_main_use_case),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=10)
):
    data = await use_case.execute(user_id, page=page, size=size)
    return {
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
    user_id: Optional[int] = Depends(auth_user_no_raise),
    use_case: ShowCourse = Depends(get_show_course_use_case)
) -> Optional[CourseForUnauthorizedDTO]:
    return await use_case.execute(course_id)


@user_router.post("/course")
async def create_course(
    dto: CreateCourseDTO,
    user_id: int = Depends(auth_user),
    use_case: CreateCourse = Depends(get_create_course_use_case)
):
    return await use_case.execute(user_id, dto)


@user_router.get("/course/{course_id}/subscribe/request")
async def request_subscribe(
    course_id: int,
    user_id: int = Depends(auth_user),
    use_case: RequestSubscribeOnCourse = Depends(get_request_sub_use_case)
):
    return await use_case.execute(course_id, user_id)


@user_router.get("/course/subscribe/{inviting_token}")
async def subscribe_by_link(
    inviting_token: str,
    user_id: int = Depends(auth_user),
    use_case: SubscribeOnCourseByLink = Depends(get_sub_by_link_use_case)
):
    return await use_case.execute(inviting_token, user_id)


@user_router.get("/course/{course_id}/subscribe")
async def subscribe_on_course(
    course_id: int,
    user_id: int = Depends(auth_user),
    use_case: SubscribeOnCourse = Depends(get_sub_course_use_case)
):
    return await use_case.execute(user_id, course_id)
