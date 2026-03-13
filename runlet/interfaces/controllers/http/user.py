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
    AddToFavourites,
    ShowCurrentAttempts,
    DeleteFavourites,
    ChangeUsername
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
from runlet.application.dtos.user import (
    UserG2,
    CurrentAttemptsInfoDTO,
    UserG3
)
from runlet.interfaces.presenters.http.user import (
    show_current_attempts_info,
    show_main
)

user_router = APIRouter(prefix="/me", route_class=DishkaRoute)


@user_router.get("/main", response_model=MainDTO)
async def get_main(
    user_id: FromDishka[AuthenticatedNotStrictlyUserId],
    interactor: FromDishka[ShowMain],
    all_page: int = Query(default=1, gt=0),
    all_size: int = Query(default=20, le=20),
    as_teacher_page: int = Query(default=1, gt=0),
    as_teacher_size: int = Query(default=6, le=6),
    as_student_page: int = Query(default=1, gt=0),
    as_student_size: int = Query(default=6, le=6)
) -> MainDTO:
    all_courses, all_pages, as_teacher, as_teacher_pages, as_student, as_student_pages = await interactor(
        user_id,
        all_page,
        all_size,
        as_teacher_page,
        as_teacher_size,
        as_student_page,
        as_student_size
    )
    return show_main(
        all_courses,
        all_page,
        all_pages,
        as_teacher,
        as_teacher_page,
        as_teacher_pages,
        as_student,
        as_student_page,
        as_student_pages
    )


@user_router.get("/profile")
async def get_my_profile(
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[ShowMyProfile],
) -> UserG2:
    return await interactor(user_id)


@user_router.put("/profile")
async def change_username(
    user_id: FromDishka[AuthenticatedUserId],
    dto: UserG3,
    interactor: FromDishka[ChangeUsername]
):
    await interactor(user_id, dto)


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


@user_router.delete("/courses/{course_id}/favourites")
async def delete_favourites(
    course_id: int,
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[DeleteFavourites]
):
    await interactor(user_id, course_id)


@user_router.get("/attempts")
async def get_current_attempts(
    user_id: FromDishka[AuthenticatedUserId],
    interactor: FromDishka[ShowCurrentAttempts],
    page: int = Query(default=1, gt=0),
    size: int = Query(default=20, le=20, gt=0)
) -> CurrentAttemptsInfoDTO:
    data, pages = await interactor(user_id, page, size)
    return show_current_attempts_info(data, page, pages)
