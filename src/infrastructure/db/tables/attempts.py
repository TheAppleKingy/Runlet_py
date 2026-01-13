from datetime import datetime, timezone

from sqlalchemy import (
    Table, Column,
    Integer, Boolean,
    ForeignKey, CheckConstraint, DateTime
)

from .base import metadata, TestCaseJSONBType


attempts = Table(
    "attempts", metadata,
    Column('user_id', ForeignKey('users.id', ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Column('problem_id', ForeignKey('problems.id', ondelete="CASCADE"),
           nullable=False, primary_key=True, unique=True),
    Column('amount', Integer, nullable=False, default=0),
    Column('passed', Boolean, nullable=False, default=False),
    Column('test_cases', TestCaseJSONBType(), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=False,
           default=lambda: datetime.now(timezone.utc)),
    CheckConstraint("amount >= 0", name="ck_attempts_amount_non_negative")
)
