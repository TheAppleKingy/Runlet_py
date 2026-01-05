from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, Float
)
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship
from .base import metadata, id_

users_courses = Table(
    "users_courses", metadata,
    Column[int]("student_id", ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False, primary_key=True),
    Column[int]("course_id", ForeignKey("courses.id", ondelete="CASCADE"),
                nullable=False, primary_key=True)
)
