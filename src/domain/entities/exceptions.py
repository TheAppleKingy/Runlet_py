from ..exc import DomainError


class AttemptError(DomainError):
    pass


class NoResultsError(AttemptError):
    pass


class MismatchTestNumsError(AttemptError):
    pass


class MismatchTestsCountError(AttemptError):
    pass


class MismatchTestOutputsError(AttemptError):
    pass


class DuplicateTestCaseInput(AttemptError):
    pass


class CourseError(DomainError):
    pass


class DirectAccessError(CourseError):
    pass


class RolesError(CourseError):
    pass


class TestCaseError(DomainError):
    pass


class ValidationTestCaseError(TestCaseError):
    pass


class UpdateForbiddenError(TestCaseError):
    pass
