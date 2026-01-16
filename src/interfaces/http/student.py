from typing import Optional

from fastapi import Depends, APIRouter

from src.application.use_cases import ShowStudentCourses, ShowStudentCourse
from src.application.dtos.student import SendProblemSolutionDTO, ModuleForStudenteDTO, CourseForStudentDTO
from src.container import (
    auth_student,
    get_show_student_courses_use_case,
    get_show_student_course_use_case
)

student_router = APIRouter(prefix="/study", tags=["Manage studiyng"])


@student_router.get("/course/{course_id}")
async def get_student_course(
    course_id: int,
    user_id: int = Depends(auth_student),
    use_case: ShowStudentCourse = Depends(get_show_student_course_use_case)
) -> Optional[CourseForStudentDTO]:
    return await use_case.execute(course_id)


@student_router.get("/problem/{problem_id}")
async def get_problem(problem_id: int, user_id: int = Depends(auth_student)):
    pass


@student_router.post("/problem/{problem_id}/send_solution")
async def send_problem_solution(dto: SendProblemSolutionDTO, user_id: int = Depends(auth_student)):
    pass
