from .user import UserRepositoryInterface
from .course import CourseRepositoryInterface
from .problem import ProblemRepositoryInterface
from .module import ModuleRepositoryInterface
from .attempt import AttemptRepositoryInterface


__all__ = [
    "UserRepositoryInterface",
    "CourseRepositoryInterface",
    "ProblemRepositoryInterface",
    "ModuleRepositoryInterface",
    "AttemptRepositoryInterface",
]
