from warm.core.comparator import Comparator

def test_comparator_simple():
    base = {"a": 1, "b": 2}
    target = {"a": 1, "b": 3}
    diff = Comparator.diff(base, target)
    assert diff["a"]["match"] is True
    assert diff["b"]["match"] is False

