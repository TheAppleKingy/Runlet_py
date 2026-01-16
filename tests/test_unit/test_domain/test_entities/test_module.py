import pytest


from src.domain.entities import Module, Problem
from src.domain.entities.exceptions import HasNoDirectAccessError


@pytest.fixture
def module():
    m = Module(name="Basics", course_id=1)
    m.id = 1
    return m


@pytest.fixture
def problem_factory():
    def _make(name, pid=None):
        p = Problem(name=name, description="desc", module_id=1)
        p.id = pid
        return p
    return _make


def test_module_add_problems_appends_unique(module, problem_factory):
    p1 = problem_factory("P1", pid=1)
    p2 = problem_factory("P2", pid=2)

    module.add_problems([p1, p2])

    assert module.problems == [p1, p2]


def test_module_add_problems_skips_existing(module, problem_factory):
    p1 = problem_factory("P1", pid=1)
    p2 = problem_factory("P2", pid=2)

    module.add_problems([p1])
    module.add_problems([p1, p2])  # p1 уже есть

    assert module.problems == [p1, p2]


def test_module_delete_problems_by_id(module, problem_factory):
    p1 = problem_factory("P1", pid=1)
    p2 = problem_factory("P2", pid=2)
    p3 = problem_factory("P3", pid=3)
    module.add_problems([p1, p2, p3])

    module.delete_problems([1, 3])

    assert module.problems == [p2]


def test_module_problems_property_is_read_only(module, problem_factory):
    with pytest.raises(HasNoDirectAccessError):
        module.problems = []  # setter должен кидать исключение
