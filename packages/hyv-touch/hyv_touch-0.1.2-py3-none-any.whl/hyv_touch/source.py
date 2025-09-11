from typing import Any, Optional, Tuple
import os
import inspect as pyinspect
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


def _unwrap_target(obj: Any) -> Tuple[Any, Optional[str]]:
    """
    Return the most informative target to show source for:
    - unwraps functools.wraps chains
    - normalizes bound methods to functions
    - extracts function from staticmethod/classmethod/property
    - for callable instances, shows __call__ (unwrapped)
    Returns (target, note) where note describes unwrapping, if any.
    """
    note_parts = []

    # Bound method -> function
    if pyinspect.ismethod(obj):
        note_parts.append("bound method → function")
        obj = obj.__func__

    # classmethod/staticmethod descriptors
    if isinstance(obj, (staticmethod, classmethod)):
        note_parts.append(f"{type(obj).__name__} → function")
        obj = obj.__func__

    # property: show fget
    if isinstance(obj, property):
        if obj.fget is not None:
            note_parts.append("property → fget")
            obj = obj.fget

    # Plain function or class: keep as-is, but unwrap decorated functions
    if pyinspect.isfunction(obj):
        try:
            unwrapped = pyinspect.unwrap(obj)
            if unwrapped is not obj:
                note_parts.append("unwrapped decorated function")
            return unwrapped, "; ".join(note_parts) or None
        except Exception:
            return obj, "; ".join(note_parts) or None

    # Classes: show class body
    if pyinspect.isclass(obj):
        return obj, "; ".join(note_parts) or None

    # Modules: show module body
    if pyinspect.ismodule(obj):
        return obj, "; ".join(note_parts) or None

    # Callable instance: show __call__ (unwrapped)
    if callable(obj) and hasattr(obj, "__call__"):
        call = obj.__call__
        if pyinspect.ismethod(call):
            call = call.__func__
        try:
            unwrapped = pyinspect.unwrap(call)
            note_parts.append(
                "__call__" + (" (unwrapped)" if unwrapped is not call else "")
            )
            return unwrapped, "; ".join(note_parts) or None
        except Exception:
            note_parts.append("__call__")
            return call, "; ".join(note_parts) or None

    # Otherwise, no inspectable source
    return obj, "; ".join(note_parts) or None


def source(value: Any, context: int = 8, theme: str = "ansi_dark") -> Panel:
    """
    Pretty source viewer.

    - Functions/methods/classes/modules: shows a syntax-highlighted snippet of the
      source file around the object's definition, with the definition line highlighted.
    - For decorated/wrapped callables, resolves to the original via functools.wraps chain.
    - Callable instances show the __call__ implementation.
    - Other values: returns an 'Unknown source' panel.

    Args:
        value: target to inspect
        context: lines of context before/after the definition block
        theme: Rich syntax theme (e.g., 'ansi_dark', 'monokai', 'github-dark')
    """
    try:
        target, unwrap_note = _unwrap_target(value)

        # Builtins/C-extensions won't have Python source
        if pyinspect.isbuiltin(target):
            raise RuntimeError("builtin or C-extension, no Python source")

        # Resolve file path
        file = pyinspect.getsourcefile(target) or pyinspect.getfile(target)
        if not file or not os.path.exists(file):
            raise RuntimeError("no source file found")

        # Lines and anchor
        src_lines, start_line = pyinspect.getsourcelines(target)
        total_obj_lines = len(src_lines)

        # Read full file for a clean window
        try:
            with open(file, "r", encoding="utf-8", errors="replace") as fh:
                all_lines = fh.readlines()
        except Exception:
            raise RuntimeError("unable to read source file")

        # Compute snippet window
        anchor = max(1, int(start_line))
        pre = max(0, int(context))
        post = max(0, int(context))
        start = max(1, anchor - pre)
        end = min(len(all_lines), anchor + total_obj_lines - 1 + post)
        snippet = "".join(all_lines[start - 1 : end])

        # Column: indentation at anchor line
        try:
            first_line_text = all_lines[anchor - 1]
            col = len(first_line_text) - len(first_line_text.lstrip()) + 1
        except Exception:
            col = 1

        # Choose lexer from extension (default python)
        ext = os.path.splitext(file)[1].lower()
        lexer = "python" if ext in {".py", ".pyi", ".pyx"} else "python"

        syntax = Syntax(
            snippet,
            lexer,
            theme=theme,
            line_numbers=True,
            start_line=start,
            word_wrap=False,
            indent_guides=True,
            highlight_lines={anchor},
        )

        # Titles
        try:
            rel = os.path.relpath(file, os.getcwd())
        except Exception:
            rel = file

        title = Text(f"source: {rel}", style="bold")
        subtitle_bits = [f"line {anchor}, col {col}"]
        if unwrap_note:
            subtitle_bits.append(f"({unwrap_note})")
        subtitle = " · ".join(subtitle_bits)

        return Panel(syntax, title=title, subtitle=subtitle, border_style="cyan")

    except Exception as e:
        msg = Text(f"Unknown source ({e})", style="dim")
        return Panel(msg, title="source", border_style="red")
