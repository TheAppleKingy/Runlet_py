from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Index
)
from .base import metadata

favourites = Table(
    "favourites",
    metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    Index("favourites_pkey_reverse", "course_id", "user_id")
)
