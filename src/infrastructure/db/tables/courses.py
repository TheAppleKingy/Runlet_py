from sqlalchemy import (
    Table, Column, String,
    ForeignKey
)

from .base import metadata, id_


courses = Table(
    'courses', metadata,
    id_(),
    Column("name", String(100), nullable=False),
    Column('description', String(512), nullable=True),
    Column('teacher_id', ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
)
