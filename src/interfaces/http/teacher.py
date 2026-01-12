from fastapi import APIRouter, Depends

from src.application.dtos.teacher import (
    CourseToUpdateDTO
)
from src.container import auth_teacher

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"])


@teacher_router.get("/course/{course_id}/redact", response_model=CourseToUpdateDTO)
async def get_course_to_redact(course_id: int, user_id: int = Depends(auth_teacher)):
    pass
