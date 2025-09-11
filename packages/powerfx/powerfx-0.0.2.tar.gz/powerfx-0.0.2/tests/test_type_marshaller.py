import uuid
from datetime import date, datetime, time

import pytest

from powerfx import Engine  # type: ignore


@pytest.fixture(scope="module")
def engine():
    return Engine()


# ---------- Numbers / Decimal ----------
@pytest.mark.parametrize(
    "expr,expected",
    [
        ("1+1", 2),
        ("2*3", 6),
        ("10/4", 2.5),  # non-integer -> float
    ],
)
def test_numbers(engine, expr, expected):
    assert engine.eval(expr) == expected


# ---------- Booleans ----------
@pytest.mark.parametrize(
    "expr,expected",
    [
        ("true", True),
        ("false", False),
        ("1<2", True),
        ("5=6", False),
    ],
)
def test_booleans(engine, expr, expected):
    assert engine.eval(expr) is expected


# ---------- Strings ----------
@pytest.mark.parametrize(
    "expr,expected",
    [
        ('"hello"', "hello"),
        ('Concatenate("A","B")', "AB"),
    ],
)
def test_strings(engine, expr, expected):
    assert engine.eval(expr) == expected


# ---------- Date ----------
def test_date(engine):
    d = engine.eval("Today()")
    assert isinstance(d, date)


# ---------- DateTime ----------
def test_datetime(engine):
    dt = engine.eval("Now()")
    assert isinstance(dt, datetime)


# ---------- Time ----------
def test_time(engine):
    t = engine.eval("Time(12,30,15)")
    assert isinstance(t, time)
    assert (t.hour, t.minute, t.second) == (12, 30, 15)


# ---------- Record ----------
def test_record(engine):
    rec = engine.eval('{x: 1, y: "abc"}')
    assert isinstance(rec, dict)
    assert rec["x"] == 1 and rec["y"] == "abc"


# ---------- Table ----------
def test_table_flat_single_column(engine):
    tbl = engine.eval("[1,2,3]")
    assert isinstance(tbl, list)
    assert tbl == [1, 2, 3]


# ---------- Blank ----------
def test_blank(engine):
    assert engine.eval("Blank()") is None


# ---------- GUID (optional but recommended) ----------
def test_guid(engine):
    g = engine.eval('GUID("6F9619FF-8B86-D011-B42D-00C04FC964FF")')
    assert isinstance(g, uuid.UUID)
    assert str(g).upper() == "6F9619FF-8B86-D011-B42D-00C04FC964FF"
