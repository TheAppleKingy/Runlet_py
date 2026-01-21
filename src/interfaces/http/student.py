from typing import Optional

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.application.use_cases import ShowStudentCourses, ShowStudentCourse
from src.application.dtos.student import SendProblemSolutionDTO, ModuleForStudenteDTO, CourseForStudentDTO
from src.domain.value_objects import AuthenticatedStudentId

student_router = APIRouter(prefix="/study", tags=["Manage studiyng"], route_class=DishkaRoute)


@student_router.get("/course/{course_id}")
async def get_student_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedStudentId],
    use_case: FromDishka[ShowStudentCourse]
) -> Optional[CourseForStudentDTO]:
    return await use_case.execute(course_id)


@student_router.get("/course/{course_id}/problem/{problem_id}")
async def get_problem_to_solve(
    course_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedStudentId]
):
    """
    This controller should return data of problem, list of possible programming languages and test info if administrator passed.
    Especially data of this controller's response need to show client before sending solve.
    """
    pass


@student_router.post("/course/{course_id}/problem/{problem_id}")
async def send_problem_solution(
    course_id: int,
    problem_id: int,
    dto: SendProblemSolutionDTO,
    user_id: FromDishka[AuthenticatedStudentId]
):
    pass
