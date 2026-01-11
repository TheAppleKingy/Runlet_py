from fastapi import Depends, APIRouter

from src.application.use_cases import ShowStudentCourses
from src.application.dtos.student import SendProblemSolutionDTO
from src.container import (
    auth_user,
    get_show_student_courses_use_case
)

student_router = APIRouter(prefix="/study", tags=["Manage studiyng"])


@student_router.get("/courses")
async def get_my_study_courses(user_id: int = Depends(auth_user), use_case: ShowStudentCourses = Depends(get_show_student_courses_use_case)):
    return await use_case.execute(user_id)


@student_router.get("/course/{course_id}/problems")
async def get_course_problems(course_id: int, user_id: int = Depends(auth_user)):
    pass


@student_router.get("/problem/{problem_id}")
async def get_problem(problem_id: int, user_id: int = Depends(auth_user)):
    pass


@student_router.post("/problem/{problem_id}/send_solution")
async def send_problem_solution(dto: SendProblemSolutionDTO, user_id: int = Depends(auth_user)):
    pass


@student_router.get("/course/subscribe/{token}")
async def subscribe_by_link(token: str, user_id: int = Depends(auth_user)):
    pass
