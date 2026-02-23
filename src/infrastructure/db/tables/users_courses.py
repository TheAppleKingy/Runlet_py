from sqlalchemy import Table, Column, ForeignKey, Index

from .base import metadata

users_courses = Table(
    "users_courses", metadata,
    Column("student_id", ForeignKey("users.id", ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Index("users_courses_pkey_reverse", "course_id", "student_id")
)
