from domain.interfaces.repositories import UserRepositoryInterface
from .base import ReadOnlyUoWInterface, ReadWriteUoWInterface


class ReadUserUoW(ReadOnlyUoWInterface):
    user_repo: UserRepositoryInterface


class ReadWriteUserUoW(ReadWriteUoWInterface):
    user_repo: UserRepositoryInterface
