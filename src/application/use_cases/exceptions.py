from src.application.exc import ApplicationError


class UndefinedUserError(ApplicationError):
    pass


class InvalidUserPasswordError(ApplicationError):
    pass


class PasswordsMismatchError(ApplicationError):
    pass


class EmailExistsError(ApplicationError):
    pass


class InactiveUserError(ApplicationError):
    pass


class SubscribeUnexsistantCourseError(ApplicationError):
    pass


class InvalidInvitingLingError(ApplicationError):
    pass


class UndefinedCourseError(ApplicationError):
    pass


class HasNoAccessError(ApplicationError):
    pass
