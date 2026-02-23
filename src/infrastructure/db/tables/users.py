from sqlalchemy import (
    Table,
    Column,
    String,
    Boolean,
    ForeignKey,
    Index
)
from sqlalchemy_utils import EmailType  # type: ignore

from .base import metadata, id_

users = Table(
    "users", metadata,
    id_(),
    Column('email', EmailType(100), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('name', String(100), nullable=True),
    Column('is_active', Boolean, default=False, nullable=False),
    Index(
        'idx_users_name_trgm',
        'name',
        postgresql_using='gin',
        postgresql_ops={'name': 'gin_trgm_ops'}
    )
)

tags = Table(
    "tags", metadata,
    id_(),
    Column('name', String(100), nullable=False, unique=False),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
)

users_tags = Table(
    "users_tags", metadata,
    Column('user_id', ForeignKey('users.id', ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Column('tag_id', ForeignKey("tags.id", ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Index("users_tags_pkey_reverse", "tag_id", "user_id")
)
