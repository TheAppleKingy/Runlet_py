from typing import Optional

from fastapi import (
    APIRouter,
    Query
)
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.application.dtos.course import (
    CourseG3,
    CourseUpdateDTO,
    CourseG6,
    CourseG8
)
from src.application.dtos.teacher import (
    GenLinkDTO,
    LinkDTO,
    DeleteProblemsDTO,
    UpdateTagStudentsDTO,
    ManageModulesDTO,
    ManageTagsDTO
)
from src.application.dtos.user import UserG1
from src.application.dtos.problem import (
    CreateUpdateProblemDTO,
    ProblemG3
)
from src.application.dtos.tag import TagG3
from src.application.use_cases import (
    ShowTeacherCourseModulesToRateStudents,
    ShowTeacherCourseTagsToRateStudents,
    UpdateCourseData,
    GenerateInviteLink,
    CreateUpdateProblem,
    DeleteProblems,
    ManageModules,
    ManageStudents,
    ManageTags,
    ShowTeacherCourseData,
    ShowStudentProblems,
    ShowProblemStudents,
    ShowTagsToUpdate,
    ShowProblemDataToUpdate,
    SearchStudents,
    ShowStudentProblemInfoToRate
)
from src.domain.value_objects import AuthenticatedTeacherId
from src.interfaces.presenters.http.dtos import (
    ModuleWithRateInfoDTO,
    TagsToUpdateDTO,
    CourseWithStudentsSeensDTO
)
from src.interfaces.presenters.http import (
    student_problems_info,
    show_tags_students_with_seen_info,
    show_student_problem_to_rate
)
from src.interfaces.presenters.http.dtos import ProblemInfoForStudentDTO

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"], route_class=DishkaRoute)


@teacher_router.get("/course/{course_id}/rate/tags")
async def get_tags_and_students_to_rate(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseTagsToRateStudents],
) -> CourseWithStudentsSeensDTO:
    """
    Endpoint returns data of course with all students, tags and tags students data.
    Need to add additional data for indicators of progress 
    """
    course, students_info = await use_case.execute(course_id)
    return show_tags_students_with_seen_info(course, students_info)


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


@teacher_router.put("/course/{course_id}/modules")
async def manage_modules(
    course_id: int,
    dto: ManageModulesDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ManageModules]
):
    await use_case.execute(course_id, dto)


@teacher_router.put("/course/{course_id}/problems")
async def create_update_problem(
    course_id: int,
    dto: CreateUpdateProblemDTO,
    use_case: FromDishka[CreateUpdateProblem],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await use_case.execute(course_id, dto)


@teacher_router.get("/course/{course_id}/modules/{module_id}/problems/{problem_id}")
async def get_problem_data_to_update(
    course_id: int,
    module_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowProblemDataToUpdate]
) -> ProblemG3:
    return await use_case.execute(course_id, module_id, problem_id)  # type: ignore[return-value]


@teacher_router.delete("/course/{course_id}/problems")
async def delete_problems(
    course_id: int,
    data: list[DeleteProblemsDTO],
    use_case: FromDishka[DeleteProblems],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await use_case.execute(course_id, data)


@teacher_router.put("/course/{course_id}/tags")
async def manage_tags(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    dto: ManageTagsDTO,
    use_case: FromDishka[ManageTags]
) -> list[TagG3]:
    """
    Returns info id and names of created tags
    """
    return await use_case.execute(course_id, dto)  # type: ignore[return-value]


@teacher_router.patch("/courses/{course_id}/students")
async def manage_students(
    course_id: int,
    data: list[UpdateTagStudentsDTO],
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ManageStudents],
):
    return await use_case.execute(course_id, data)


@teacher_router.get("/courses/{course_id}/data")
async def get_course_data_to_update(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTeacherCourseData]
) -> CourseG8:
    return await use_case.execute(course_id)


@teacher_router.get("/course/{course_id}/update/tags")
async def get_tags_students_to_update(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowTagsToUpdate]
) -> TagsToUpdateDTO:
    students, tags = await use_case.execute(course_id)
    return TagsToUpdateDTO(students=students, tags=tags)


@teacher_router.get("/course/{course_id}/search/students")
async def search_students(
    course_id: int,
    use_case: FromDishka[SearchStudents],
    user_id: FromDishka[AuthenticatedTeacherId],
    tag_id: Optional[int] = Query(default=None, gt=0),
    q: str = Query(min_length=2)
) -> list[UserG1]:
    return await use_case.execute(course_id, q, tag_id=tag_id)  # type: ignore[return-value]


@teacher_router.get("/course/{course_id}/modules/{module_id}/problems/{problem_id}/students/{student_id}")
async def get_student_problem_info_to_rate(
    course_id: int,
    module_id: int,
    problem_id: int,
    student_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    use_case: FromDishka[ShowStudentProblemInfoToRate]
) -> ProblemInfoForStudentDTO:
    return show_student_problem_to_rate(
        await use_case.execute(course_id, module_id, problem_id, student_id)
    )
