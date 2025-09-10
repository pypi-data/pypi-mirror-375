import os
import sys
from pathlib import Path

_loaded_key = "_powerfx_loaded"


def load() -> None:
    """
    Ensure Microsoft.PowerFx assemblies are loadable via pythonnet (CoreCLR).

    Precedence for dll_dir:
    - explicit arg
    - env var POWERFX_DLL_DIR
    - <pkg>/runtime (optional fallback)
    """
    if getattr(sys.modules[__name__], _loaded_key, False):
        return

    # Resolve and validate base path
    raw = os.getenv("POWERFX_DLL_DIR")
    if not raw:
        raise RuntimeError("Power Fx DLL directory not found. Set POWERFX_DLL_DIR environment variable.")

    base = Path(raw).expanduser().resolve()
    if not base.is_dir():
        raise RuntimeError(
            f"Power Fx DLL directory '{base}' does not exist. Check your POWERFX_DLL_DIR environment variable."
        )

    # Select CoreCLR BEFORE any clr import
    import pythonnet  # type: ignore

    pythonnet.load("coreclr")

    import clr  # type: ignore

    # Make sure PowerFx DLL folder is in probing paths
    if base not in sys.path:
        sys.path.append(str(base))

    # Load ONLY the PowerFx assemblies you ship; let CoreCLR resolve System.* deps.
    for name in ("Microsoft.PowerFx.Core", "Microsoft.PowerFx.Interpreter"):
        try:
            clr.AddReference(name)
        except Exception as ex:
            # Fallback to explicit path if name load fails
            print(f"Failed to load '{name}' by name, trying explicit path. Exception: {ex}")
            raise

    setattr(sys.modules[__name__], _loaded_key, True)
