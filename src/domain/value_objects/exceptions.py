from ..exc import DomainError


class ValueObjectError(DomainError):
    pass


class DuplicateTestCaseInput(DomainError):
    pass


class ValidationTestCaseError(DomainError):
    pass
