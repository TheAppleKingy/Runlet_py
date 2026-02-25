from sqlalchemy import (
    Table, Column, String,
    ForeignKey, Boolean
)

from .base import metadata, id_


courses = Table(
    'courses', metadata,
    id_(),
    Column("name", String(100), nullable=False),
    Column('description', String(512), nullable=True),
    Column('teacher_id', ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("is_private", Boolean, nullable=False),
    Column("notify_request_sub", Boolean, default=False, nullable=False)
)
