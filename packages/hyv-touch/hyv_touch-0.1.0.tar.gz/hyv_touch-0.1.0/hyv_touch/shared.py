from __future__ import annotations
import builtins
import os
from rich.theme import Theme
from rich.console import Console

THEME = Theme(
    {
        "banner": "bold magenta",
        "prompt": "bold cyan",
        "note": "italic dim",
        "ok": "bold green",
        "err": "bold red",
        "border": "magenta",
    }
)

console = Console(theme=THEME)


from typing import Any, Dict, Optional

_current: Optional[Dict[str, Any]] = None


def set_scope(scope: Dict[str, Any]) -> None:
    """Set the current interactive scope dictionary (globals/locals mashup)."""
    global _current
    _current = scope


def get_scope() -> Dict[str, Any]:
    """Get the current interactive scope; falls back to this module's globals()."""
    default = globals()
    default["get_scope"] = get_scope
    default["set_scope"] = set_scope

    return _current if _current is not None else default
