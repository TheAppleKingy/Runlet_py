from typing import Optional

from fastapi import APIRouter, Depends

from src.application.dtos.teacher import (
    CourseForTeacherDTO,
    CreateCourseTagsDTO,
    TeacherCourseToManageDTO,
    UpdateCourseDTO,
    GenerateInviteLinkDTO
)
from src.application.use_cases.teacher import (
    AddCourseTags,
    ShowTeacherCourseToManageProblems,
    ShowTeacherCourseToManageStudents,
    UpdateCourseData,
    GenerateInviteLink
)
from src.container import (
    auth_teacher,
    get_show_teacher_course_to_manage_students_use_case,
    get_show_teacher_course_to_manage_problems_use_case,
    get_add_course_tags_use_case,
    get_update_course_data_use_case,
    get_generate_invite_link_use_case
)

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"])


@teacher_router.get("/course/{course_id}/students")
async def get_teacher_course_to_manage_students(
    course_id: int,
    user_id: int = Depends(auth_teacher),
    use_case: ShowTeacherCourseToManageStudents = Depends(
        get_show_teacher_course_to_manage_students_use_case)
) -> Optional[TeacherCourseToManageDTO]:
    return await use_case.execute(course_id)


@teacher_router.get("/course/{course_id}/problems")
async def get_teacher_course_to_manage_problems(
    course_id: int,
    user_id: int = Depends(auth_teacher),
    use_case: ShowTeacherCourseToManageProblems = Depends(
        get_show_teacher_course_to_manage_problems_use_case)
) -> Optional[TeacherCourseToManageDTO]:
    return await use_case.execute(course_id)


@teacher_router.patch("/course/{course_id}")
async def update_course_data(
    course_id: int,
    dto: UpdateCourseDTO,
    user_id: int = Depends(auth_teacher),
    use_case: UpdateCourseData = Depends(get_update_course_data_use_case)
):
    await use_case.execute(course_id, dto)


@teacher_router.post("/course/{course_id}/invite/create")
async def create_invite_link(
    course_id: int,
    dto: GenerateInviteLinkDTO,
    user_id: int = Depends(auth_teacher),
    use_case: GenerateInviteLink = Depends(get_generate_invite_link_use_case)
):
    return await use_case.execute(course_id, dto)


@teacher_router.patch("/course/{course_id}/tags")
async def add_tags(course_id: int, dto: CreateCourseTagsDTO, user_id: int = Depends(auth_teacher), use_case: AddCourseTags = Depends(get_add_course_tags_use_case)):
    return await use_case.execute(course_id, dto)
