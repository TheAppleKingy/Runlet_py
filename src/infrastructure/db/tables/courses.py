from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, Float
)
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship
from .base import metadata, id_


courses = Table(
    'courses', metadata,
    id_,
    Column[str]("name", String(100), nullable=False),
    Column[str]('description', String(512), nullable=True),
    Column[int]('teacher_id', ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
)
