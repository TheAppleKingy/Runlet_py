from sqlalchemy import (
    Table, Column,
    String, Boolean,
    ForeignKey
)
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship

from .base import metadata, id_

users = Table(
    "users", metadata,
    id_,
    Column[str]('name', String(100), nullable=False),
    Column[str]('email', EmailType(100), unique=True, nullable=False),
    Column[bool]('is_active', Boolean, default=False, nullable=False),
    Column[str]('password', String('255'), nullable=False)

)

tags = Table(
    "tags", metadata,
    id_,
    Column[str]('name', String(100), nullable=False, unique=False)
)

users_tags = Table(
    "users_tags", metadata,
    Column[int]('user_id', ForeignKey('users.id', ondelete="CASCADE"),
                nullable=False, primary_key=True),
    Column[int]('tag_id', ForeignKey("tags.id", ondelete="CASCADE"),
                nullable=False, primary_key=True)
)
