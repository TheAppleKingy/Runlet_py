from sqlalchemy import Table, Column, String, ForeignKey


from .base import metadata, id_, TestCaseJSONBType

problems = Table(
    "problems", metadata,
    id_(),
    Column('name', String(100), nullable=True),
    Column('description', String(1024), nullable=False),
    Column('course_id', ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
    Column('test_cases', TestCaseJSONBType(), nullable=True)
)
