from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

# Load the PowerFx assemblies and types needed for type marshalling from FormulaValue to Python native types.
from powerfx._loader import load

load()

from Microsoft.PowerFx.Types import (  # type: ignore  # noqa: E402
    BlankValue,
    BooleanValue,
    ColorValue,
    DateTimeValue,
    DateValue,
    DecimalValue,
    FormulaValue,
    GuidValue,
    NumberValue,
    RecordValue,
    StringValue,
    TableValue,
    TimeValue,
    VoidValue,
)


def _formulavalue_to_python(val: FormulaValue):
    if val is None:
        return None

    if isinstance(val, BlankValue | VoidValue):
        return None

    if isinstance(val, BooleanValue):
        return bool(val.Value)

    if isinstance(val, StringValue):
        return str(val.Value)

    if isinstance(val, NumberValue | DecimalValue):
        d = Decimal(str(val.Value))
        return int(d) if d == d.to_integral_value() else float(d)

    if isinstance(val, DateValue):
        dt = val.Value
        return date(dt.Year, dt.Month, dt.Day)

    if isinstance(val, DateTimeValue):
        dt = val.Value
        return datetime(dt.Year, dt.Month, dt.Day, dt.Hour, dt.Minute, dt.Second, dt.Millisecond * 1000)

    if isinstance(val, TimeValue):
        ts = val.Value
        micros = ts.Milliseconds * 1000
        return time(ts.Hours % 24, ts.Minutes, ts.Seconds, micros)

    if isinstance(val, ColorValue):
        argb = int(val.Value)
        a = (argb >> 24) & 0xFF
        r = (argb >> 16) & 0xFF
        g = (argb >> 8) & 0xFF
        b = (argb >> 0) & 0xFF
        return (r, g, b, a)

    # NEW: GUID → uuid.UUID
    if isinstance(val, GuidValue):
        g = val.Value  # System.Guid
        return UUID(str(g))  # normalize to canonical Python UUID

    if isinstance(val, RecordValue):
        out = {}
        for field in val.Fields:
            out[field.Name] = _formulavalue_to_python(field.Value)

        # Optional: flatten Dataverse-style choice/lookup records
        # if set(out) == {"Label", "Value"}: return out["Label"]
        return out

    if isinstance(val, TableValue):
        rows = []
        for row in val.Rows:
            rows.append(_formulavalue_to_python(row.Value) if row.IsValue else None)
        if rows and all(isinstance(r, dict) and len(r) == 1 for r in rows if r is not None):
            rows = [next(iter(r.values())) if r is not None else None for r in rows]
        return rows

    raise TypeError(f"Unsupported FormulaValue type: {type(val)}")
