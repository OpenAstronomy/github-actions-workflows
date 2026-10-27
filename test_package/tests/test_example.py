import pytest


def test_simple():
    assert True


@pytest.mark.failing_test
def test_fail():
    assert False
