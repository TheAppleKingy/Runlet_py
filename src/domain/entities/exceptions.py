from ..exc import DomainError


class NoResultsError(DomainError):
    pass


class MismatchTestNumsError(DomainError):
    pass


class MismatchTestsCountError(DomainError):
    pass


class MismatchTestOutputsError(DomainError):
    pass


class DuplicateTestCaseInput(DomainError):
    pass


class DirectAccessError(DomainError):
    pass


class RolesError(DomainError):
    pass


class TestCaseError(DomainError):
    pass


class ValidationTestCaseError(DomainError):
    pass


class UpdateForbiddenError(DomainError):
    pass
