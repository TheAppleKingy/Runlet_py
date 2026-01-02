from ..exc import ApplicationError


class NoHandlerRegisteredError(ApplicationError):
    pass


class NoDTOModelRegisteredError(ApplicationError):
    pass
