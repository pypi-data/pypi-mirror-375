__version__ = "1.0.2"

# Make intra-package imports like `from core ...` and `from ui ...` work after packaging.
try:
    import sys as _sys
    from . import core as _core
    from . import ui as _ui
    from . import installer as _installer
    _sys.modules.setdefault("core", _core)
    _sys.modules.setdefault("ui", _ui)
    _sys.modules.setdefault("installer", _installer)
    del _sys, _core, _ui, _installer
except Exception:
    # Non-fatal during certain tooling/import scenarios
    pass
