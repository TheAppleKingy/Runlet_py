from .user import UserRepositoryInterface
from .course import CourseRepositoryInterface
from .problem import ProblemRepositoryInterface
from .module import ModuleRepositoryInterface
from .attempt import AttemptRepositoryInterface
from .tag import TagRepositoryInterface


__all__ = [
    "UserRepositoryInterface",
    "CourseRepositoryInterface",
    "ProblemRepositoryInterface",
    "ModuleRepositoryInterface",
    "AttemptRepositoryInterface",
    "TagRepositoryInterface"
]
