from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, Float
)
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship

from domain.entities import TestCases

from .base import metadata, id_, TestCaseJSONBType

problems = Table(
    "problems", metadata,
    id_,
    Column[str]('name', String(100), nullable=True),
    Column[str]('description', String(1024), nullable=False),
    Column[int]('course_id', ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    Column[TestCases]('test_cases', TestCaseJSONBType(), nullable=True)
)
