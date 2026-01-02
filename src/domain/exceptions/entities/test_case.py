from ..base import DomainError


class TestCaseError(DomainError):
    pass


class ValidationTestCaseError(TestCaseError):
    pass


class UpdateForbiddenError(TestCaseError):
    pass
