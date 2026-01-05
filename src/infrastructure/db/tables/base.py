from sqlalchemy import MetaData, Column, Integer, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from domain.entities import TestCases

metadata = MetaData()

id_ = Column[int]('id', Integer, primary_key=True, autoincrement=True)


class TestCaseJSONBType(TypeDecorator):
    impl = JSONB

    def process_bind_param(self, value, dialect):
        if isinstance(value, TestCases):
            return value.as_dict()
        elif value is None:
            return None
        else:
            raise TypeError(f"Undefined type: {type(value)}. Should be TestCases")

    def process_result_value(self, value, dialect):
        if value is None:
            return TestCases()
        test_cases = TestCases()
        return test_cases.from_dict(value)

    def copy(self, **kw):
        return self.__class__()
