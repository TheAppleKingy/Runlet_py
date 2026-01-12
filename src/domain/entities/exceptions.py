from ..exc import DomainError


class NoResultsError(DomainError):
    pass


class MismatchTestNumsError(DomainError):
    pass


class MismatchTestsCountError(DomainError):
    pass


class MismatchTestOutputsError(DomainError):
    pass


class DirectAccessError(DomainError):
    pass


class RolesError(DomainError):
    pass


class TestCaseError(DomainError):
    pass


class UndefinedTagError(DomainError):
    pass


class UndefinedModuleError(DomainError):
    pass


class RepeatableNamesError(DomainError):
    pass


class HasNoDirectAccessError(DomainError):
    pass


class NamesAlreadyExistError(DomainError):
    pass
