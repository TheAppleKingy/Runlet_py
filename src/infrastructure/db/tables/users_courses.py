from sqlalchemy import Table, Column, ForeignKey

from .base import metadata

users_courses = Table(
    "users_courses", metadata,
    Column("student_id", ForeignKey("users.id", ondelete="CASCADE"),
           nullable=False, primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"),
           nullable=False, primary_key=True)
)
