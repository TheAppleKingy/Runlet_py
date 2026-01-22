from typing import Optional, NewType


AuthenticatedUserId = NewType("AuthenticatedUserId", int)
AuthenticatedStudentId = NewType("AuthenticatedStudentId", int)
AuthenticatedTeacherId = NewType("AuthenticatedTeacherId", int)
AuthenticatedNotStrictlyUserId = Optional[AuthenticatedUserId]
