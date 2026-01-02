from ..base import DomainError


class CourseError(DomainError):
    pass


class DirectAccessError(CourseError):
    pass


class RolesError(CourseError):
    pass
