from __future__ import annotations

import inspect
import os
import sys
import time
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Optional

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


from .shared import console, get_scope

# ────────────────────────────────────────────────────────────────────────────
# Pretty wrappers
# ────────────────────────────────────────────────────────────────────────────


def _short(v: Any, limit: int = 240) -> str:
    try:
        s = repr(v)
    except Exception:
        s = f"<{type(v).__name__}>"
    if len(s) <= limit:
        return s
    head = int(limit * 0.7)
    tail = int(limit * 0.2)
    return f"{s[:head]} … {s[-tail:]}"


def _sig_str(fn: Callable) -> str:
    try:
        return str(inspect.signature(fn))
    except Exception:
        return "(…)"


def _where(fn: Callable) -> tuple[str, int]:
    try:
        file = inspect.getsourcefile(fn) or inspect.getfile(fn)
        line = fn.__code__.co_firstlineno  # type: ignore[attr-defined]
        return file, line
    except Exception:
        return "<unknown>", 0


def _args_table(args, kwargs) -> Table:
    t = Table.grid(padding=(0, 1))
    t.add_column(style="cyan", no_wrap=True)
    t.add_column(style="dim")
    for i, a in enumerate(args):
        t.add_row(f"arg{i}", _short(a))
    for k, v in kwargs.items():
        t.add_row(str(k), _short(v))
    if not args and not kwargs:
        t.add_row("—", "no arguments")
    return t


def _call_panel(
    title: str, color: str, fn: Callable, args, kwargs, extra: Optional[str] = None
):
    file, line = _where(fn)
    header = Text.assemble(
        (title, f"bold {color}"),
        (" · ", "dim"),
        (getattr(fn, "__name__", "<fn>"), "bold"),
        (_sig_str(fn), "cyan"),
        (" · ", "dim"),
        (os.path.basename(file), "dim"),
        (":", "dim"),
        (str(line), "dim"),
    )
    body = Group(_args_table(args, kwargs))
    if extra:
        body = Group(body, Text(extra, style="dim"))
    return Panel(body, title=header, border_style=color)


def _return_panel(fn: Callable, rv: Any, dur_ms: float, color: str = "green"):
    t = Table.grid(padding=(0, 1))
    t.add_column(style="cyan", no_wrap=True)
    t.add_column(style="dim")
    t.add_row("return", _short(rv))
    t.add_row("type", getattr(type(rv), "__name__", "None"))
    t.add_row("duration", f"{dur_ms:.1f} ms")
    return Panel(t, title=Text("return", style=f"bold {color}"), border_style=color)


def _exception_panel(e: BaseException, dur_ms: float):
    t = Table.grid(padding=(0, 1))
    t.add_column(style="red", no_wrap=True)
    t.add_column()
    t.add_row(type(e).__name__, _short(e, 400))
    t.add_row("duration", f"{dur_ms:.1f} ms")
    return Panel(t, title=Text("exception", style="bold red"), border_style="red")


def _install_trace_for_lines(fn: Callable, line_breaks: set[int]):
    """
    Set a tracer that triggers breakpoint() on selected lines of `fn`.
    Returns a callable that restores the previous tracer.
    """
    code = getattr(fn, "__code__", None)
    if code is None or not line_breaks:
        return lambda: None

    prev = sys.gettrace()

    def tracer(frame, event, arg):
        if event != "line":
            return tracer
        if frame.f_code is code and frame.f_lineno in line_breaks:
            breakpoint()
        return tracer

    sys.settrace(tracer)
    return lambda: sys.settrace(prev)


def debug_wrap(
    fn: Callable,
    *,
    break_on: Iterable[str] = (),
    line_breaks: Iterable[int] = (),
) -> Callable:
    

    break_on = set(break_on or ())
    line_breaks = set(int(x) for x in line_breaks or ())

    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def _aw(*args, **kwargs):
            if "enter" in break_on:
                breakpoint()
            restore = _install_trace_for_lines(fn, line_breaks)
            console.print(_call_panel("call", "yellow", fn, args, kwargs))
            t0 = time.perf_counter()
            try:
                rv = await fn(*args, **kwargs)
                if "exit" in break_on:
                    breakpoint()
                console.print(_return_panel(fn, rv, (time.perf_counter() - t0) * 1000))
                return rv
            except BaseException as e:
                if "exception" in break_on:
                    breakpoint()
                console.print(_exception_panel(e, (time.perf_counter() - t0) * 1000))
                raise
            finally:
                restore()

        return _aw

    if inspect.isasyncgenfunction(fn):

        @wraps(fn)
        async def _ag(*args, **kwargs):
            if "enter" in break_on:
                breakpoint()
            restore = _install_trace_for_lines(fn, line_breaks)
            console.print(
                _call_panel("call[asyncgen]", "yellow", fn, args, kwargs, "yielding...")
            )
            t0 = time.perf_counter()
            try:
                async for item in fn(*args, **kwargs):
                    console.print(
                        Panel(Text(f"yield {_short(item)}"), border_style="blue")
                    )
                    yield item
                if "exit" in break_on:
                    breakpoint()
                console.print(
                    _return_panel(
                        fn,
                        "<exhausted>",
                        (time.perf_counter() - t0) * 1000,
                        color="blue",
                    )
                )
            except BaseException as e:
                if "exception" in break_on:
                    breakpoint()
                console.print(_exception_panel(e, (time.perf_counter() - t0) * 1000))
                raise
            finally:
                restore()

        return _ag

    if inspect.isgeneratorfunction(fn):

        @wraps(fn)
        def _g(*args, **kwargs):
            if "enter" in break_on:
                breakpoint()
            restore = _install_trace_for_lines(fn, line_breaks)
            console.print(
                _call_panel("call[gen]", "yellow", fn, args, kwargs, "yielding...")
            )
            t0 = time.perf_counter()
            try:
                for item in fn(*args, **kwargs):
                    console.print(
                        Panel(Text(f"yield {_short(item)}"), border_style="blue")
                    )
                    yield item
                if "exit" in break_on:
                    breakpoint()
                console.print(
                    _return_panel(
                        fn,
                        "<exhausted>",
                        (time.perf_counter() - t0) * 1000,
                        color="blue",
                    )
                )
            except BaseException as e:
                if "exception" in break_on:
                    breakpoint()
                console.print(_exception_panel(e, (time.perf_counter() - t0) * 1000))
                raise
            finally:
                restore()

        return _g

    @wraps(fn)
    def _w(*args, **kwargs):
        if "enter" in break_on:
            breakpoint()
        restore = _install_trace_for_lines(fn, line_breaks)
        console.print(_call_panel("call", "yellow", fn, args, kwargs))
        t0 = time.perf_counter()
        try:
            rv = fn(*args, **kwargs)
            if "exit" in break_on:
                breakpoint()
            console.print(_return_panel(fn, rv, (time.perf_counter() - t0) * 1000))
            return rv
        except BaseException as e:
            if "exception" in break_on:
                breakpoint()
            console.print(_exception_panel(e, (time.perf_counter() - t0) * 1000))
            raise
        finally:
            restore()

    return _w


# ────────────────────────────────────────────────────────────────────────────
# Embrace / release for a scope
# ────────────────────────────────────────────────────────────────────────────


def embrace(
    scope: Dict[str, Any],
    *,
    include: Optional[Callable[[str, Any], bool]] = None,
    exclude: Optional[Callable[[str, Any], bool]] = None,
    break_on: Iterable[str] = (),
    line_breaks: Iterable[int] = (),
) -> Dict[str, Callable]:
    """
    Wrap functions in a scope with debug_wrap.
    Skips builtins, modules, and classes; preserves __wrapped__ for sane inspection.
    """

    def default_include(n, o):
        return inspect.isfunction(o) and o.__module__ != "builtins"

    include = include or default_include
    originals: Dict[str, Callable] = {}
    for name, obj in list(scope.items()):
        if not include(name, obj):
            continue
        if exclude and exclude(name, obj):
            continue
        try:
            wrapped = debug_wrap(
                obj,  break_on=break_on, line_breaks=line_breaks
            )
        except Exception:
            continue
        originals[name] = obj
        scope[name] = wrapped
    return originals


def release(scope: Dict[str, Any], originals: Dict[str, Callable]) -> None:
    """Restore previously wrapped functions by name."""
    for name, fn in originals.items():
        scope[name] = fn


