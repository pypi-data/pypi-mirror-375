from typing import Any, Iterable
import os
import inspect
import traceback as tb

from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.table import Table
from rich.syntax import Syntax
from rich.traceback import Traceback


def feel(value: Any) -> Panel:
    """
    Pretty debugger for values.

    - Exception instance  -> rich header + highlighted offending line + full traceback + attrs
    - Exception class     -> like class view, labeled as 'exception class'
    - Function            -> "[async] func_name(args) -> [ReturnType]" + docstring
    - Class               -> "class Name([Bases])" + docstring + class attrs + signatures
    - Instance            -> "instance of ClassName" + instance attrs (+ class quick view)
    """
    # Exception instance
    if isinstance(value, BaseException):
        return _render_exception(value)

    # Exception class
    if inspect.isclass(value) and issubclass(value, BaseException):
        return _render_exception_class(value)

    # Regular class / function / method
    if inspect.isclass(value):
        return _render_class(value)
    if inspect.isfunction(value) or inspect.ismethod(value) or inspect.isbuiltin(value):
        return _render_function(value)

    # instance or plain value
    return _render_instance(value)


# ── exception helpers ───────────────────────────────────────────────────────


def _read_snippet(path: str, line: int, context: int = 8) -> tuple[str, int] | None:
    """Read a head/tail snippet around 1-based line number; returns (text, start_line)."""
    if not path or not os.path.exists(path) or line <= 0:
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            all_lines = fh.readlines()
    except Exception:
        return None
    start = max(1, line - max(0, int(context)))
    end = min(len(all_lines), line + max(0, int(context)))
    text = "".join(all_lines[start - 1 : end])
    return text, start


def _public_exception_fields(exc: BaseException) -> list[tuple[str, str, str]]:
    """
    Extract public, non-callable attributes from the exception for debugging.
    Includes .args and PEP 678 __notes__ if present.
    """
    rows: list[tuple[str, str, str]] = []

    # args first, if meaningful
    try:
        if getattr(exc, "args", ()):
            rows.append(("args", "tuple", _short_repr(exc.args, 120)))
    except Exception:
        pass

    # PEP 678 notes
    try:
        notes = getattr(exc, "__notes__", None)
        if notes:
            rows.append(("__notes__", "list[str]", _short_repr(notes, 160)))
    except Exception:
        pass

    # other public attributes
    seen = {"args", "__notes__", "with_traceback", "add_note"}
    for name in sorted(dir(exc)):
        if name.startswith("_") or name in seen:
            continue
        try:
            val = getattr(exc, name)
        except Exception:
            continue
        if callable(val):
            continue
        rows.append((name, _short_type(type(val)), _short_repr(val, 160)))
    return rows


def _render_exception(exc: BaseException) -> Panel:
    etype = type(exc)
    title = Text.assemble(("exception", "bold red"))

    head = Text()
    head.append(etype.__name__, style="bold")
    msg = str(exc)
    if msg:
        head.append(": ", style="bold")
        head.append(msg)

    parts: list[Any] = [head]

    # Try to show failing line (last frame) with context
    last_file = None
    last_line = None
    tb_obj = exc.__traceback__
    extracted = tb.extract_tb(tb_obj) if tb_obj else []
    if extracted:
        last = extracted[-1]
        last_file = last.filename
        last_line = last.lineno
        snippet = _read_snippet(last_file, last_line, context=8) # type: ignore
        if snippet:
            text, start_line = snippet
            try:
                rel = os.path.relpath(last_file, os.getcwd())
            except Exception:
                rel = last_file
            syntax = Syntax(
                text,
                "python",
                theme="ansi_dark",
                line_numbers=True,
                start_line=start_line,
            highlight_lines={last_line}, # type: ignore
                word_wrap=False,
                indent_guides=True,
            )
            parts.append(Text(f"\n{rel}:{last_line}", style="dim"))
            parts.append(syntax)

    # Full rich traceback (handles cause/context chaining)
    try:
        rb = Traceback.from_exception(
            type(exc), exc, exc.__traceback__, show_locals=False
        )
        parts.append(rb)
    except Exception:
        pass

    # Attributes table
    attrs = _public_exception_fields(exc)
    if attrs:
        t = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        t.add_column("Field", style="bold")
        t.add_column("Type", style="cyan")
        t.add_column("Value", style="dim")
        for k, typ, val in attrs:
            t.add_row(k, typ, val)
        parts.append(Text("\n[Attributes]", style="bold magenta"))
        parts.append(t)

    return Panel(Group(*parts), title=title, border_style="red")


def _render_exception_class(cls: type[BaseException]) -> Panel:
    bases = [
        b.__name__
        for b in getattr(cls, "__mro__", [])[1:]
        if b is not BaseException and b is not object
    ] or []
    header = Text.assemble(
        ("exception class ", "bold magenta"),
        (cls.__name__, "bold"),
        ("(", "bold magenta"),
        (", ".join(bases), "cyan"),
        (")", "bold magenta"),
    )
    parts = [header, _doc_block(cls)]
    return Panel(Group(*parts), title="exception class", border_style="red")


# ── existing helpers (kept, with tiny tweaks) ───────────────────────────────


def _short_type(tp: Any) -> str:
    if tp is inspect._empty:
        return "Any"
    try:
        if isinstance(tp, type):
            return tp.__name__
        s = str(tp)
        return s.replace("typing.", "")
    except Exception:
        return repr(tp)


def _short_repr(obj: Any, maxlen: int = 80) -> str:
    try:
        s = repr(obj)
    except Exception:
        s = f"<{type(obj).__name__}>"
    if len(s) > maxlen:
        s = s[: maxlen - 1] + "…"
    return s


def _format_signature(func: Any, drop_first: bool = False) -> str:
    try:
        sig = inspect.signature(func)
    except Exception:
        return "() -> [Any]"

    params = list(sig.parameters.values())
    if drop_first and params:
        params = params[1:]

    parts = []
    saw_kw_only = False
    for p in params:
        if p.kind is inspect.Parameter.KEYWORD_ONLY and not saw_kw_only:
            parts.append("*")
            saw_kw_only = True

        name = p.name
        if p.kind is inspect.Parameter.VAR_POSITIONAL:
            name = "*" + name
        elif p.kind is inspect.Parameter.VAR_KEYWORD:
            name = "**" + name

        piece = name
        if p.annotation is not inspect._empty:
            piece += f": {_short_type(p.annotation)}"
        if p.default is not inspect._empty:
            piece += f" = {_short_repr(p.default)}"
        parts.append(piece)

    ret = _short_type(sig.return_annotation)
    return f"({', '.join(parts)}) -> [{ret}]"


def _doc_block(obj: Any) -> Text:
    doc = inspect.getdoc(obj) or ""
    if not doc:
        return Text('""', style="dim")
    t = Text()
    t.append('"', style="dim")
    t.append(doc)
    t.append('"', style="dim")
    return t


def _render_function(func: Any) -> Panel:
    name = getattr(func, "__name__", getattr(func, "__qualname__", "<?>"))
    is_async = inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)
    sig = _format_signature(func, drop_first=False)
    head = Text()
    if is_async:
        head.append("[async] ", style="bold magenta")
    head.append(name, style="bold")
    head.append(sig, style="cyan")

    body = Group(head, _doc_block(func))
    return Panel(body, title="function", border_style="green")


def _render_class(cls: type) -> Panel:
    bases = [
        b.__name__ for b in getattr(cls, "__mro__", [])[1:] if b is not object
    ] or []
    header = Text.assemble(
        ("class ", "bold magenta"),
        (cls.__name__, "bold"),
        ("(", "bold magenta"),
        (", ".join(bases), "cyan"),
        (")", "bold magenta"),
    )

    # Class attributes (non-callable, non-dunder)
    attrs = []
    for k, v in cls.__dict__.items():
        if k.startswith("_"):
            continue
        if callable(v) or isinstance(v, (staticmethod, classmethod, property)):
            continue
        attrs.append((k, _short_type(type(v)), _short_repr(v)))
    attrs.sort()

    attr_table = None
    if attrs:
        attr_table = Table(
            show_header=True, header_style="bold", box=None, pad_edge=False
        )
        attr_table.add_column("Attribute", style="bold")
        attr_table.add_column("Type", style="cyan")
        attr_table.add_column("Value", style="dim")
        for k, typ, val in attrs:
            attr_table.add_row(k, typ, val)

    # Methods: init first, then public methods
    rows = []
    init = cls.__dict__.get("__init__")
    if init:
        sig = _format_signature(getattr(init, "__func__", init), drop_first=True)
        rows.append(("__init__", sig))

    methods = []
    for k, v in cls.__dict__.items():
        if k.startswith("_"):
            continue
        fn = None
        if isinstance(v, (staticmethod, classmethod)):
            fn = v.__func__
        elif inspect.isfunction(v):
            fn = v
        elif inspect.ismethod(v):
            fn = v.__func__
        if fn is not None:
            methods.append((k, _format_signature(fn, drop_first=True)))
    methods.sort(key=lambda x: x[0])

    meth_table = None
    if methods:
        meth_table = Table(
            show_header=True, header_style="bold", box=None, pad_edge=False
        )
        meth_table.add_column("Method", style="bold")
        meth_table.add_column("Signature", style="cyan")
        for name, sig in methods:
            meth_table.add_row(name, sig)

    parts = [header, _doc_block(cls)]
    if attr_table:
        parts.append(Text("\n[Class Attributes]", style="bold magenta"))
        parts.append(attr_table)  # type: ignore
    if meth_table:
        parts.append(Text("\n[Methods]", style="bold magenta"))
        parts.append(meth_table)  # type: ignore

    return Panel(Group(*parts), title="class", border_style="blue")


def _render_instance(obj: Any) -> Panel:
    cls = obj.__class__
    head = Text.assemble(("instance of ", "bold magenta"), (cls.__name__, "bold"))

    # instance attributes
    inst = []
    try:
        inst_dict = vars(obj)
        if isinstance(inst_dict, dict):
            for k, v in inst_dict.items():
                if k.startswith("_"):
                    continue
                inst.append((k, _short_type(type(v)), _short_repr(v)))
    except Exception:
        pass
    inst.sort()

    inst_table = None
    if inst:
        inst_table = Table(
            show_header=True, header_style="bold", box=None, pad_edge=False
        )
        inst_table.add_column("Attribute", style="bold")
        inst_table.add_column("Type", style="cyan")
        inst_table.add_column("Value", style="dim")
        for k, typ, val in inst:
            inst_table.add_row(k, typ, val)

    # tiny class peek (bases and __init__)
    bases = [
        b.__name__ for b in getattr(cls, "__mro__", [])[1:] if b is not object
    ] or []
    class_line = Text.assemble(
        ("class ", "bold magenta"),
        (cls.__name__, "bold"),
        ("(", "bold magenta"),
        (", ".join(bases), "cyan"),
        (")", "bold magenta"),
    )
    init = getattr(cls, "__init__", None)
    init_sig = (
        _format_signature(getattr(init, "__func__", init), drop_first=True)
        if init
        else "() -> [Any]"
    )

    parts = [head]
    if inst_table:
        parts.append(inst_table)  # type: ignore
    parts.append(Text("\n[Class]", style="bold magenta"))
    parts.append(Group(class_line, Text(f"__init__{init_sig}", style="cyan")))  # type: ignore
    return Panel(Group(*parts), title="instance", border_style="magenta")
