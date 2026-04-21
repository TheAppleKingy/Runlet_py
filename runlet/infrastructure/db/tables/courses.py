from sqlalchemy import (
    Table, Column, String,
    ForeignKey, Boolean, DateTime
)

from .base import metadata, id_


courses = Table(
    'courses', metadata,
    id_(),
    Column("name", String, nullable=False),
    Column('description', String, nullable=True),
    Column('teacher_id', ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Column("is_private", Boolean, nullable=False),
    Column("notify_request_sub", Boolean, default=False, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, unique=False)
)
