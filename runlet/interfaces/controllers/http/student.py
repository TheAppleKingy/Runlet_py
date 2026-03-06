from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from runlet.application.interactors import (
    ShowStudentCourse,
    ShowProblemToSolve,
    SendProblemSolution,
)
from runlet.application.dtos.student import SendProblemSolutionDTO
from runlet.application.dtos.course import (
    CourseG7
)
from runlet.application.dtos.problem import ProblemInfoForStudentDTO
from runlet.domain.interfaces.types import AuthenticatedStudentId
from runlet.interfaces.presenters.http import (
    show_problem_info_for_student_to_solve,
)

student_router = APIRouter(prefix="/study", tags=["Manage studiyng"], route_class=DishkaRoute)


@student_router.get("/course/{course_id}")
async def get_student_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedStudentId],
    interactor: FromDishka[ShowStudentCourse]
) -> CourseG7:
    return await interactor(course_id)


@student_router.get("/course/{course_id}/modules/{module_id}/problems/{problem_id}")
async def get_problem_to_solve(
    course_id: int,
    module_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedStudentId],
    interactor: FromDishka[ShowProblemToSolve]
) -> ProblemInfoForStudentDTO:
    problem, attempt, langs = await interactor(user_id, course_id, module_id, problem_id)
    return show_problem_info_for_student_to_solve(problem, attempt, langs)


@student_router.post("/course/{course_id}/modules/{module_id}/problems/{problem_id}")
async def send_problem_solution(
    course_id: int,
    module_id: int,
    problem_id: int,
    dto: SendProblemSolutionDTO,
    user_id: FromDishka[AuthenticatedStudentId],
    interactor: FromDishka[SendProblemSolution]
):
    return await interactor(course_id, module_id, problem_id, user_id, dto)
