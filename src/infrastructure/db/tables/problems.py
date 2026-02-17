from sqlalchemy import Table, Column, String, ForeignKey, Boolean, Integer


from .base import metadata, id_, TestCaseJSONBType, ExamplesJSONBType

problems = Table(
    "problems", metadata,
    id_(),
    Column('name', String(100), nullable=False, unique=False),  # control on business rules layer
    Column('description', String(1024), nullable=True, unique=False),
    Column('module_id', ForeignKey("modules.id", ondelete="CASCADE"), nullable=False),
    Column("auto_pass", Boolean, default=False, nullable=False),
    Column('test_cases', TestCaseJSONBType(), nullable=False, unique=False),
    Column("show_test_cases", Boolean, default=False, nullable=False),
    Column("examples", ExamplesJSONBType(), nullable=False, unique=False)
)


modules = Table(
    "modules", metadata,
    id_(),
    Column("name", String(100), unique=False, nullable=False),
    Column("order", Integer, unique=False, nullable=False),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
)
