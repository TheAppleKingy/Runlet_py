from typing import Optional

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.application.dtos.teacher import (
    CourseForTeacherDTO,
    CreateCourseTagsDTO,
    TeacherCourseToManageProblemsDTO,
    TeacherCourseToManageStudentsDTO,
    UpdateCourseDTO,
    GenerateInviteLinkDTO,
    GenInviteLinkDTO
)
from src.application.use_cases.teacher import (
    AddCourseTags,
    ShowTeacherCourseToManageProblems,
    ShowTeacherCourseToManageStudents,
    UpdateCourseData,
    GenerateInviteLink
)
from src.domain.value_objects import AuthenticatedTeacherId
teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"], route_class=DishkaRoute)


@teacher_router.get("/course/{course_id}/students")
async def get_teacher_course_to_manage_students(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseToManageStudents]
) -> Optional[TeacherCourseToManageStudentsDTO]:
    """
    Endpoint returns data of course with all needed tags and tags students data
    """
    return await use_case.execute(course_id)


@teacher_router.get("/course/{course_id}/problems")
async def get_teacher_course_to_manage_problems(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseToManageProblems]
) -> Optional[TeacherCourseToManageProblemsDTO]:
    """
    Endpoint returns data of course with all needed modules and modules problems data
    """
    return await use_case.execute(course_id)


@teacher_router.patch("/course/{course_id}")
async def update_course_data(
    course_id: int,
    dto: UpdateCourseDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[UpdateCourseData]
):
    await use_case.execute(course_id, dto)


@teacher_router.post("/course/{course_id}/invite/create")
async def create_invite_link(
    course_id: int,
    dto: GenerateInviteLinkDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[GenerateInviteLink]
) -> GenInviteLinkDTO:
    return {"link": await use_case.execute(course_id, dto)}  # type: ignore


@teacher_router.patch("/course/{course_id}/tags")
async def add_tags(
    course_id: int,
    dto: CreateCourseTagsDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[AddCourseTags]
):
    """
    Endpoint adds only new tags(if tags with existing names will be provided returns 400)
    and automatically add students to tags if provided
    """
    return await use_case.execute(course_id, dto)
