from typing import Optional

from fastapi import APIRouter, Depends

from src.application.dtos.teacher import (
    CourseForTeacherDTO,
    CreateCourseDTO,
    CreateCourseTagsDTO
)
from src.application.use_cases.teacher import ShowTeacherCourse, CreateCourse, AddCourseTags
from src.container import (
    auth_teacher,
    auth_user,
    get_show_teacher_course_use_case,
    get_create_course_use_case,
    get_add_course_tags_use_case
)

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"])


@teacher_router.get("/course/{course_id}")
async def get_course_for_teacher(course_id: int, user_id: int = Depends(auth_teacher), use_case: ShowTeacherCourse = Depends(get_show_teacher_course_use_case)) -> Optional[CourseForTeacherDTO]:
    return await use_case.execute(course_id)


@teacher_router.post("/course")
async def create_course(dto: CreateCourseDTO, user_id: int = Depends(auth_user), use_case: CreateCourse = Depends(get_create_course_use_case)):
    return await use_case.execute(user_id, dto)


@teacher_router.patch("/course/{course_id}/tags")
async def add_tags(course_id: int, dto: CreateCourseTagsDTO, user_id: int = Depends(auth_teacher), use_case: AddCourseTags = Depends(get_add_course_tags_use_case)):
    return await use_case.execute(course_id, dto)
