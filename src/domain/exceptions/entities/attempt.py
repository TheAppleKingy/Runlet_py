from ..base import DomainError


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
