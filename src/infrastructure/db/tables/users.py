from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, Float,
)
from sqlalchemy_utils import EmailType
from sqlalchemy.orm import relationship

metadata = MetaData()

users = Table(
    "users", metadata,
    Column[int]('id', Integer, primary_key=True, autoincrement=True),
    Column[str]('name', String(100), nullable=False),
    Column[str]('email', EmailType(100), unique=True, nullable=False),
)
