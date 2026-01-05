from sqlalchemy import (
    Table, Column,
    Integer, Boolean,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from domain.entities import TestCases

from .base import metadata, TestCaseJSONBType


attempts = Table(
    "attempts", metadata,
    Column[int]('user_id', ForeignKey('users.id', ondelete="CASCADE"),
                nullable=False, primary_key=True),
    Column[int]('problem_id', ForeignKey('problems.id', ondelete="CASCADE"),
                nullable=False, primary_key=True),
    Column[int]('amount', Integer, nullable=False, default=0),
    Column[bool]('passed', Boolean, nullable=False, default=False),
    Column[TestCases]('test_cases', TestCaseJSONBType(), nullable=True),
    CheckConstraint("amount >= 0", name="ck_attempts_amount_non_negative")
)
