# ────────────────────────────────────────────────────────────────────────────
# Editing helpers (terminal & VS Code) — unchanged behavior, safer scope usage
# ────────────────────────────────────────────────────────────────────────────


import ast
import inspect
import os
import shutil
import subprocess
import tempfile
import textwrap
from types import ModuleType
from typing import Any, Callable, Dict, Optional
from .shared import get_scope, set_scope

from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text


class VSCodeNotFound(RuntimeError): ...


class EditError(RuntimeError): ...


def _which_code() -> str:
    exe = shutil.which("code")
    if exe:
        return exe
    if os.name == "nt":
        exe = shutil.which("code.cmd")
        if exe:
            return exe
    raise VSCodeNotFound(
        "VS Code CLI not found. Install it and ensure 'code' is on PATH "
        "(VS Code: Command Palette → Shell Command: Install 'code' command)."
    )


def _extract_function_names(src: str) -> list[str]:
    try:
        tree = ast.parse(src)
        return [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    except Exception:
        return []


def _edit_in_terminal(func: Callable) -> Callable:
    src = inspect.getsource(func)
    src = textwrap.dedent(src)
    name = func.__name__
    file = inspect.getsourcefile(func) or "<memory>"

    editor = os.environ.get("EDITOR")
    if editor:
        import tempfile, subprocess, pathlib

        with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
            tf.write(src)
            tf.flush()
            path = tf.name
        try:
            subprocess.call([editor, path])
            edited = pathlib.Path(path).read_text(encoding="utf-8")
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass
    else:
        console = Console()
        console.print(
            Panel(
                Syntax(src, "python", theme="ansi_dark", line_numbers=True),
                title=f"edit: {name}",
            )
        )
        console.print(
            Text(
                "Enter edited function source. End with a single '.' line.", style="dim"
            )
        )
        lines = []
        while True:
            line = input()
            if line.strip() == ".":
                break
            lines.append(line)
        edited = "\n".join(lines)

    g = func.__globals__
    code = compile(edited, file, "exec")
    ns: Dict[str, Any] = {}
    exec(code, g, ns)
    new_fn = ns.get(name) or next(
        (v for v in ns.values() if inspect.isfunction(v)), None
    )
    if not callable(new_fn):
        raise ValueError("Edited code did not define a callable.")
    return new_fn


def _edit_in_vscode(
    func: Callable,
    *,
    in_place: bool = False,
    reuse_window: bool = True,
    new_window: bool = False,
) -> Callable:
    code_cli = _which_code()
    name = getattr(func, "__name__", "edited")
    orig_file = inspect.getsourcefile(func) or inspect.getfile(func)
    orig_line = (
        getattr(func, "__code__", None).co_firstlineno # type: ignore
        if hasattr(func, "__code__")
        else None
    )
    src = textwrap.dedent(inspect.getsource(func))

    if in_place:
        if (
            not orig_file
            or not os.path.exists(orig_file)
            or not isinstance(inspect.getmodule(func), ModuleType)
        ):
            raise EditError("Cannot edit in-place: source file or module not found.")
        args = [code_cli, "--wait", "--goto", f"{orig_file}:{orig_line or 1}"]
        if new_window:
            args.append("--new-window")
        elif reuse_window:
            args.append("--reuse-window")
        subprocess.run(args, check=False)
        mod = importlib.reload(inspect.getmodule(func))  # type: ignore[arg-type]
        new_fn = getattr(mod, name, None)
        if not callable(new_fn):
            raise EditError(f"Edited file didn't define callable '{name}'.")
        return new_fn

    header = (
        "# Edit the function below. You may rename it; the version with the original\n"
        f"# name '{name}' will be preferred on import. Save & close VS Code to apply.\n"
        "from __future__ import annotations\n\n"
    )
    temp_dir = tempfile.mkdtemp(prefix=f"edit_{name}_")
    temp_path = os.path.join(temp_dir, f"{name}_edit.py")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(src)
        f.write("\n")

    args = [code_cli, "--wait", temp_path]
    if new_window:
        args.append("--new-window")
    elif reuse_window:
        args.append("--reuse-window")
    subprocess.run(args, check=False)

    with open(temp_path, "r", encoding="utf-8") as f:
        edited = f.read()

    g = get_scope()
    g.update(func.__globals__ if hasattr(func, "__globals__") else {})
    
    ns: Dict[str, Any] = {}
    try:
        compiled = compile(edited, temp_path, "exec")
        exec(compiled, g, ns)
    except Exception as e:
        raise EditError(f"Edited code failed to compile/exec:\n{e}")

    new_fn = ns.get(name)
    if not callable(new_fn):
        defs = _extract_function_names(edited)
        for candidate in defs:
            if callable(ns.get(candidate)):
                new_fn = ns[candidate]
                break
    if not callable(new_fn):
        for v in ns.values():
            if inspect.isfunction(v):
                new_fn = v
                break
    if not callable(new_fn):
        raise EditError("Edited code did not define a callable function.")
    new_fn.__name__ = getattr(new_fn, "__name__", name)
    return new_fn


def edit(
    func: Callable, scope: Optional[Dict[str, Any]] = None, terminal: bool = False
) -> str:
    """
    Edit a function, then rebind it in:
      1) the Touch scope (interactive env)
      2) the function's defining module globals (so other functions see it)
      3) if it's a bound method, patch the owner class too
    """
    scope = scope or get_scope()
    if not scope:
        return "No scope available to patch the function."

    # produce new_fn via your existing editors
    new_func = _edit_in_terminal(func) if terminal else _edit_in_vscode(func)
    name = getattr(func, "__name__", None) or "edited"

    # 1) Interactive scope
    scope[name] = new_func

    # 2) Function's home module globals
    try:
        func.__globals__[name] = new_func
    except Exception:
        pass

    # 3) If it was a bound method, patch class attribute
    try:
        if (
            inspect.ismethod(func)
            and hasattr(func, "__self__")
            and hasattr(func.__self__, "__class__")
        ):
            owner = func.__self__.__class__
            setattr(owner, name, new_func)
    except Exception:
        pass

    set_scope(scope)

    return f"Function '{name}' edited successfully."
