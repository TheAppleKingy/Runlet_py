from typing import Optional

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.application.dtos.course import (
    CourseG3,
    CourseG4,
    CourseUpdateDTO,
    CourseG6,
    CourseG8
)
from src.application.dtos.teacher import (
    GenLinkDTO,
    LinkDTO,
    DeleteTagsDTO,
    DeleteProblemsDTO,
    AddStudentsDTO,
    DeleteStudentsDTO,
    DeleteModulesDTO
)
from src.application.dtos.user import UserG1
from src.application.dtos.problem import (
    ProblemCreateDTO,
    ProblemUpdateDTO
)
from src.application.dtos.module import (
    ModuleCreateDTO,
    ModuleUpdateDTO
)
from src.application.use_cases import (
    ShowTeacherCourseModulesToRateStudents,
    ShowTeacherCourseTagsToRateStudents,
    UpdateCourseData,
    GenerateInviteLink,
    CreateProblem,
    UpdateProblem,
    DeleteProblems,
    CreateModules,
    UpdateModules,
    DeleteModules,
    AddStudents,
    DeleteStudents,
    DeleteTags,
    ShowTeacherCourseData,
    ShowStudentProblems,
    ShowProblemStudents
)
from src.domain.value_objects import AuthenticatedTeacherId
from src.interfaces.presenters.http.dtos import ModuleWithRateInfoDTO
from src.interfaces.presenters.http import student_problems_info

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"], route_class=DishkaRoute)


@teacher_router.get("/course/{course_id}/rate/tags")
async def get_tags_and_students_to_rate(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseTagsToRateStudents]
) -> Optional[CourseG4]:
    """
    Endpoint returns data of course with all students, tags and tags students data.
    Need to add additional data for indicators of progress 
    """
    return await use_case.execute(course_id)


@teacher_router.get("/course/{course_id}/rate/students/{student_id}")
async def get_student_problems_info(
    course_id: int,
    student_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowStudentProblems]
) -> list[ModuleWithRateInfoDTO]:
    attempts, modules = await use_case.execute(course_id, student_id)
    return student_problems_info(attempts, modules)


@teacher_router.get("/course/{course_id}/rate/modules")
async def get_modules_and_problems_to_rate(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseModulesToRateStudents]
) -> Optional[CourseG3]:
    """
    Endpoint returns data of course with all needed modules and modules problems data.
    Need to add additional data for indicators of progress 
    """
    return await use_case.execute(course_id)


@teacher_router.get("/course/{course_id}/rate/problems/{problem_id}")
async def get_problem_students_info(
    course_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowProblemStudents]
) -> list[UserG1]:
    return await use_case.execute(problem_id)


@teacher_router.patch("/course/{course_id}")
async def update_course_data(
    course_id: int,
    dto: CourseUpdateDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[UpdateCourseData]
) -> None:
    await use_case.execute(course_id, dto)


@teacher_router.post("/course/{course_id}/invite/create")
async def create_invite_link(
    course_id: int,
    dto: GenLinkDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[GenerateInviteLink]
) -> LinkDTO:
    return LinkDTO(link=await use_case.execute(course_id, dto))


@teacher_router.get("/course/{course_id}/problems")
async def get_course_to_update_problems(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseModulesToRateStudents]
) -> Optional[CourseG6]:
    return await use_case.execute(course_id)


@teacher_router.post("/course/{course_id}/modules")
async def create_modules(
    course_id: int,
    data: list[ModuleCreateDTO],
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[CreateModules]
):
    return await use_case.execute(course_id, data)


@teacher_router.put("/course/{course_id}/modules")
async def update_modules(
    course_id: int,
    data: list[ModuleUpdateDTO],
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[UpdateModules]
):
    return await use_case.execute(course_id, data)


@teacher_router.delete("/course/{course_id}/modules")
async def delete_modules(
    course_id: int,
    dto: DeleteModulesDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[DeleteModules],
):
    return await use_case.execute(course_id, dto.modules_ids)


@teacher_router.post("/course/{course_id}/modules/{module_id}/problems")
async def create_problem(
    course_id: int,
    module_id: int,
    dto: ProblemCreateDTO,
    use_case: FromDishka[CreateProblem],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await use_case.execute(course_id, module_id, dto)


@teacher_router.put("/course/{course_id}/modules/{module_id}/problems/{problem_id}")
async def update_problem(
    course_id: int,
    module_id: int,
    problem_id: int,
    dto: ProblemUpdateDTO,
    use_case: FromDishka[UpdateProblem],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    await use_case.execute(course_id, module_id, problem_id, dto)


@teacher_router.delete("/course/{course_id}/problems")
async def delete_problems(
    course_id: int,
    dto: DeleteProblemsDTO,
    use_case: FromDishka[DeleteProblems],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await use_case.execute(course_id, dto)


# @teacher_router.patch("/course/{course_id}/tags")
# async def add_tags(
#     course_id: int,
#     dto: AddTagsDTO,
#     user_id: FromDishka[AuthenticatedTeacherId],
#     use_case: FromDishka[AddTags]
# ):
#     """
#     Endpoint adds only new tags(if tags with existing names will be provided returns 400)
#     and automatically add students to tags if provided
#     """
#     return await use_case.execute(course_id, dto)


@teacher_router.delete("/course/{course_id}/tags")
async def delete_tags(
    course_id: int,
    dto: DeleteTagsDTO,
    use_case: FromDishka[DeleteTags],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await use_case.execute(course_id, dto.tags_ids)


@teacher_router.patch("/courses/{course_id}/students")
async def add_students(
    course_id: int,
    dto: AddStudentsDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[AddStudents],
):
    return await use_case.execute(course_id, dto)


@teacher_router.delete("/courses/{course_id}/students")
async def delete_students(
    course_id: int,
    dto: DeleteStudentsDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[DeleteStudents],
):
    return await use_case.execute(course_id, dto)


@teacher_router.get("/courses/{course_id}/data")
async def get_course_data_to_update(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseData]
) -> CourseG8:
    return await use_case.execute(course_id)
