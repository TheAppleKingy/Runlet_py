from typing import Optional

from fastapi import (
    APIRouter,
    Query
)
from dishka.integrations.fastapi import (
    FromDishka,
    DishkaRoute
)

from runlet.application.dtos.course import (
    CourseG3,
    CourseUpdateDTO,
    CourseG6,
    CourseG8,
)
from runlet.application.dtos.problem import (
    ProblemInfoForTeacherDTO
)
from runlet.application.dtos.teacher import (
    GenLinkDTO,
    LinkDTO,
    DeleteProblemsDTO,
    UpdateTagStudentsDTO,
    ManageModulesDTO,
    ManageTagsDTO,
    RateStudentDTO,
    PaginatedCourseTagsStudentsWithSeensDTO,
    PaginatedProblemStudentsInfoDTO,
    PaginatedTagStudentsDTO,
    PaginatedTagsStudentsDTO,
    PaginatedSearchStudentsDTO,
    PaginatedSearchStudentsWithSeensDTO
)
from runlet.application.dtos.module import (
    ModuleG4
)
from runlet.application.dtos.problem import (
    CreateUpdateProblemDTO,
    ProblemG3
)
from runlet.application.dtos.tag import (
    TagG3,
)
from runlet.application.interactors import (
    ShowTeacherCourseModulesToRateStudents,
    ShowTeacherCourseTagsToRateStudents,
    ShowCourseModulesProblemsToUpdate,
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
    ShowStudentProblemInfoToRate,
    RateStudent,
    SearchStudentsWithSeens,
    DeleteCourse
)
from runlet.domain.interfaces.types import AuthenticatedTeacherId
from runlet.interfaces.presenters.http import (
    student_problems_info,
    show_tags_students_with_seen_info,
    show_student_problem_to_rate,
    show_course_modules_problems_with_seen_info,
    show_problems_students_with_attempt_info,
    show_tags_paginated_students_to_update,
    show_paginated_searched_students_with_seens
)

teacher_router = APIRouter(prefix="/teaching", tags=["Manage teaching"], route_class=DishkaRoute)


@teacher_router.get("/course/{course_id}/rate/tags")
async def get_tags_and_students_to_rate(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowTeacherCourseTagsToRateStudents],
    tag_id: Optional[int] = Query(default=None, gt=0),
    page: int = Query(default=1, gt=0),
    size: int = Query(default=12, gt=0, le=20)
) -> PaginatedCourseTagsStudentsWithSeensDTO:
    course, users_attempts, pages, tag = await interactor(course_id, tag_id=tag_id, page=page, size=size)
    return show_tags_students_with_seen_info(course, users_attempts, tag, page, pages)


@teacher_router.get("/course/{course_id}/rate/students/{student_id}")
async def get_student_problems_info(
    course_id: int,
    student_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowStudentProblems]
) -> list[ModuleG4]:
    attempts, modules = await interactor(course_id, student_id)
    return student_problems_info(attempts, modules)


@teacher_router.get("/course/{course_id}/rate/modules")
async def get_modules_and_problems_to_rate(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowTeacherCourseModulesToRateStudents]
) -> CourseG3:
    course, unseen_problems_ids = await interactor(course_id)
    return show_course_modules_problems_with_seen_info(course, unseen_problems_ids)


@teacher_router.get("/course/{course_id}/rate/modules/{module_id}/problems/{problem_id}")
async def get_problem_students_info(
    course_id: int,
    module_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowProblemStudents],
    page: int = Query(default=1, gt=0),
    size: int = Query(default=7, gt=0, le=7)
) -> PaginatedProblemStudentsInfoDTO:
    students_attempts, pages = await interactor(course_id, module_id, problem_id, page=page, size=size)
    return show_problems_students_with_attempt_info(students_attempts, page, pages)


@teacher_router.patch("/course/{course_id}")
async def update_course_data(
    course_id: int,
    dto: CourseUpdateDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[UpdateCourseData]
) -> None:
    await interactor(course_id, dto)


@teacher_router.post("/course/{course_id}/invite/create")
async def create_invite_link(
    course_id: int,
    dto: GenLinkDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[GenerateInviteLink]
) -> LinkDTO:
    return LinkDTO(link=await interactor(course_id, dto))


@teacher_router.get("/course/{course_id}/problems")
async def get_course_to_update_problems(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowCourseModulesProblemsToUpdate]
) -> CourseG6:
    return await interactor(course_id)


@teacher_router.put("/course/{course_id}/modules")
async def manage_modules(
    course_id: int,
    dto: ManageModulesDTO,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ManageModules]
):
    await interactor(course_id, dto)


@teacher_router.put("/course/{course_id}/problems")
async def create_update_problem(
    course_id: int,
    dto: CreateUpdateProblemDTO,
    interactor: FromDishka[CreateUpdateProblem],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await interactor(course_id, dto)


@teacher_router.get("/course/{course_id}/modules/{module_id}/problems/{problem_id}")
async def get_problem_data_to_update(
    course_id: int,
    module_id: int,
    problem_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowProblemDataToUpdate]
) -> ProblemG3:
    return await interactor(course_id, module_id, problem_id)  # type: ignore[return-value]


@teacher_router.delete("/course/{course_id}/problems")
async def delete_problems(
    course_id: int,
    data: list[DeleteProblemsDTO],
    interactor: FromDishka[DeleteProblems],
    user_id: FromDishka[AuthenticatedTeacherId]
):
    return await interactor(course_id, data)


@teacher_router.put("/course/{course_id}/tags")
async def manage_tags(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    dto: ManageTagsDTO,
    interactor: FromDishka[ManageTags]
) -> list[TagG3]:
    """
    Returns info id and names of created tags
    """
    return await interactor(course_id, dto)  # type: ignore[return-value]


@teacher_router.patch("/courses/{course_id}/students")
async def manage_students(
    course_id: int,
    data: list[UpdateTagStudentsDTO],
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ManageStudents],
):
    return await interactor(course_id, data)


@teacher_router.get("/courses/{course_id}/data")
async def get_course_data_to_update(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowTeacherCourseData]
) -> CourseG8:
    return await interactor(course_id)


@teacher_router.get("/course/{course_id}/update/tags")
async def get_tags_students_to_update(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowTagsToUpdate],
    tag_id: Optional[int] = Query(default=None, gt=0),
    course_page: int = Query(default=1, gt=0),
    course_size: int = Query(default=7, gt=0, le=20),
    tag_page: int = Query(default=1, gt=0),
    tag_size: int = Query(default=1, gt=0, le=20),
) -> PaginatedTagsStudentsDTO:
    course_students, course_pages, tag_students, tag_pages, tag, tags = await interactor(
        course_id,
        tag_id=tag_id,
        course_students_page=course_page,
        course_students_size=course_size,
        tag_students_page=tag_page,
        tag_students_size=tag_size
    )
    return show_tags_paginated_students_to_update(
        course_students,
        course_page,
        course_pages,
        tag,
        tag_students,
        tag_page,
        tag_pages,
        tags
    )


@teacher_router.get("/course/{course_id}/search/students")
async def search_students(
    course_id: int,
    interactor: FromDishka[SearchStudents],
    user_id: FromDishka[AuthenticatedTeacherId],
    tag_id: Optional[int] = Query(default=None, gt=0),
    q: str = Query(min_length=2),
    page: int = Query(default=1, gt=0),
    size: int = Query(default=7, gt=0, le=7)
) -> PaginatedSearchStudentsDTO:
    students, pages = await interactor(course_id, q, tag_id=tag_id, page=page, size=size)  # type: ignore[return-value]
    return PaginatedSearchStudentsDTO(
        students=students,  # type: ignore[arg-type]
        page=page,
        pages=pages
    )


@teacher_router.get("/course/{course_id}/search/students/seens")
async def search_students_with_seens(
    course_id: int,
    interactor: FromDishka[SearchStudentsWithSeens],
    user_id: FromDishka[AuthenticatedTeacherId],
    tag_id: Optional[int] = Query(default=None, gt=0),
    q: str = Query(min_length=2),
    page: int = Query(default=1, gt=0),
    size: int = Query(default=12, gt=0, le=12)
) -> PaginatedSearchStudentsWithSeensDTO:
    students, attempts, pages = await interactor(course_id, q, tag_id=tag_id, page=page, size=size)
    return show_paginated_searched_students_with_seens(students, attempts, page, pages)


@teacher_router.get("/course/{course_id}/modules/{module_id}/problems/{problem_id}/students/{student_id}")
async def get_student_problem_info_to_rate(
    course_id: int,
    module_id: int,
    problem_id: int,
    student_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[ShowStudentProblemInfoToRate]
) -> ProblemInfoForTeacherDTO:
    return show_student_problem_to_rate(
        await interactor(course_id, module_id, problem_id, student_id)
    )


@teacher_router.patch("/course/{course_id}/modules/{module_id}/problems/{problem_id}/students/{student_id}")
async def rate_student(
    course_id: int,
    module_id: int,
    problem_id: int,
    student_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[RateStudent],
    dto: RateStudentDTO
):
    await interactor(course_id, module_id, problem_id, student_id, dto.ok)


@teacher_router.delete("/course/{course_id}")
async def delete_course(
    course_id: int,
    user_id: FromDishka[AuthenticatedTeacherId],
    interactor: FromDishka[DeleteCourse]
):
    await interactor(course_id)
