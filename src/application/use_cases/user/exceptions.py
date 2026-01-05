from application.exc import ApplicationError


class UserApplicationError(ApplicationError):
    pass


class UndefinedUserError(UserApplicationError):
    pass


class InvalidUserPasswordError(UserApplicationError):
    pass


class PasswordsMismatchError(UserApplicationError):
    pass


class EmailExistsError(UserApplicationError):
    pass
