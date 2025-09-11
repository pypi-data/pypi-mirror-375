from __future__ import annotations

import os
import runpy
import sys
from types import ModuleType
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .shared import get_scope, set_scope


def _resolve_main_path(main_file: Optional[str]) -> str:
    # If a path is provided, trust it
    if main_file:
        path = os.path.abspath(main_file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"main_file not found: {path}")
        return path

    # Else try the actual entry script
    main_mod = sys.modules.get("__main__")
    path = (
        getattr(main_mod, "__file__", None)
        if isinstance(main_mod, ModuleType)
        else None
    )
    if not path:
        raise RuntimeError(
            "Cannot determine entry script. Pass main_file='path/to/main.py'."
        )
    return os.path.abspath(path)


def _is_public_export(name: str, obj: Any) -> bool:
    if name == "__builtins__":
        return False
    # skip obvious internals unless explicitly kept
    if name.startswith("_"):
        return False
    # avoid injecting imported modules; users can import as they please
    if isinstance(obj, ModuleType):
        return False
    return True


def tickle(
    main_file: Optional[str] = None,
    *,
    scope: Optional[Dict[str, Any]] = None,
    add_only: bool = True,
    verbose: bool = True,
) -> str:
    """
    Re-interpret the entry script and blend its new symbols into the current REPL scope.

    Args:
        main_file: Optional explicit path to the entry script. If omitted, uses the file that
                   launched __main__.
        scope:     Target environment (defaults to current Touch scope).
        add_only:  If True (default), only add missing names; do NOT overwrite existing ones.
                   If False, also update existing names that changed.
        verbose:   Print a Rich summary panel.

    Returns:
        Summary string of added/changed names.
    """
    console = Console()
    env = scope or get_scope()

    # Resolve and ensure imports can find the script's folder
    path = _resolve_main_path(main_file)
    script_dir = os.path.dirname(path)
    popped = False
    if script_dir and script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        popped = True

    try:
        # Execute the script in isolation, like starting fresh, but don't poison our globals.
        # This will run top-level code (side effects are on you; you asked for "re-run").
        fresh: Dict[str, Any] = runpy.run_path(path_name=path, run_name="__main__")

    finally:
        if popped:
            try:
                sys.path.remove(script_dir)
            except ValueError:
                pass

    # Compute diff
    before_keys = set(env.keys())
    added, updated = [], []

    for name, obj in fresh.items():
        if not _is_public_export(name, obj):
            continue

        if name in env:
            if not add_only and env[name] is not obj:
                env[name] = obj
                updated.append(name)
        else:
            env[name] = obj
            added.append(name)

    # Publish merged scope
    set_scope(env)

    # Be nice and tell the human what happened
    summary = f"tickle: reloaded '{os.path.basename(path)}'; added: {len(added)}, updated: {len(updated) if not add_only else 0}"
    if verbose:
        body = Text()
        body.append(f"entry: {path}\n", style="bold")
        body.append(f"added ({len(added)}): ", style="cyan")
        body.append(", ".join(sorted(added)) if added else "—")
        body.append("\n")
        if not add_only:
            body.append(f"updated ({len(updated)}): ", style="magenta")
            body.append(", ".join(sorted(updated)) if updated else "—")
        console.print(Panel(body, title="tickle", border_style="cyan"))

    return summary
