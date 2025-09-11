from __future__ import annotations

from typing import Any

from powerfx._loader import load
from powerfx._utility import _formulavalue_to_python


class Engine:
    """
    Minimal wrapper around Microsoft.PowerFx RecalcEngine.
    - eval(expr: str) -> Python value
    - set(name: str, value: any) to bind variables
    """

    def __init__(self) -> None:
        # Load CLR + PowerFx assemblies first, using dll_dir or env var.
        load()
        print("Power Fx assemblies loaded successfully.")
        # Import after load so the assemblies are visible.
        from Microsoft.PowerFx import RecalcEngine as _RecalcEngine  # type: ignore

        self._engine = _RecalcEngine()

    def eval(self, expr: str) -> Any:
        """
        Evaluate a Power Fx expression and return a Python-native object where possible.
        """
        if not isinstance(expr, str):
            raise TypeError("expr must be a string")
        result = self._engine.Eval(expr)  # returns FormulaValue
        pyResult = _formulavalue_to_python(result)
        return pyResult
