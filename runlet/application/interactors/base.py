from runlet.application.interfaces.repositories import (
    CourseRepositoryInterface,
    UserRepositoryInterface,
    AttemptRepositoryInterface
)

from runlet.application.interfaces.uow import UoWInterface


class _CourseRepoRelatedInteractor:
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
    ):
        self._uow = uow
        self._course_repo = course_repo


class _CourseUserReposRelatedInteractor(_CourseRepoRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        super().__init__(uow, course_repo)
        self._user_repo = user_repo


class _CourseAttemptReposRelatedInteractor(_CourseRepoRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        attempt_repo: AttemptRepositoryInterface
    ):
        super().__init__(uow, course_repo)
        self._attempt_repo = attempt_repo


class _AttemptUserRepoRelatedInteractor:
    def __init__(
        self,
        uow: UoWInterface,
        attempt_repo: AttemptRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        self._uow = uow
        self._attempt_repo = attempt_repo
        self._user_repo = user_repo


class _CourseAttemptUserRepoRelatedInteractor(_AttemptUserRepoRelatedInteractor):
    def __init__(
        self,
        uow: UoWInterface,
        course_repo: CourseRepositoryInterface,
        attempt_repo: AttemptRepositoryInterface,
        user_repo: UserRepositoryInterface
    ):
        super().__init__(uow, attempt_repo, user_repo)
        self._course_repo = course_repo
