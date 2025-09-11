import pytest

from powerfx import Engine  # type: ignore


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("1+1", 2),
        ("Sum(1,2,3)", 6),
        ("With({x:1}, x+2)", 3),
        ("If(true, 10, 20)", 10),
        ("Filter([1,2,3,4], Value > 2)", [3, 4]),
        ("First([1,2,3,5])", {"Value": 1}),
    ],
)
def test_engine_eval(expr, expected):
    engine = Engine()
    result = engine.eval(expr)
    assert result == expected
