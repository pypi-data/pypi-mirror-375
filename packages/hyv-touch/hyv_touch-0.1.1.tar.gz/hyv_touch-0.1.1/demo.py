# demo_touch.py
# Rich Touch: showcase script
#
# This script demonstrates:
#   1) Pretty value inspection via feel(...)
#   2) Source viewing via source(...)
#   3) Exception rendering with exact failing line
#   4) Debug wrapping via embrace(...)/release(...)
#   5) Interactive REPL session via touch(...)
#   6) Optional: live edit via edit(...) and code injection via retouch(...)
#
# Run:
#   python demo_touch.py                # interactive mode (prints guidance, then opens Touch)
#   python demo_touch.py --demo         # non-interactive showcase (prints all panels once)
#   python demo_touch.py --interactive  # alias for default
#
# Notes:
#   - For edit(...)/retouch(...), VS Code's `code` CLI or $EDITOR should be available for the full experience.
#   - The REPL environment writes through to module globals so edits affect functions used by other functions.

from __future__ import annotations

import argparse
import math
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# Core utilities from the package
from hyv_touch import touch, feel, source, embrace, release, edit, retouch

console = Console()

# ── Sample code under test ─────────────────────────────────────────────────

class Vector2:
    """Minimal 2D vector for demo purposes."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def scale(self, k: float) -> "Vector2":
        return Vector2(self.x * k, self.y * k)

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


def flaky_divide(a: float, b: float) -> float:
    """Division with a silly guard to edit away during the demo."""
    if a < 0:
        raise ValueError("a must be non-negative")
    return a / b


def exercise() -> float:
    """Small driver that calls flaky_divide so edits are observable in callers."""
    return flaky_divide(-1, 5)  # initially raises; after edit(...) it should succeed


# ── Showcase building blocks ───────────────────────────────────────────────

def section(title: str) -> None:
    console.print(Rule(title))

def show_value_panel(title: str, renderable) -> None:
    console.print(Panel(renderable, title=title, border_style="cyan"))

def show_table(title: str, rows: list[tuple[str, Any]]) -> None:
    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    table.add_column("Item", style="bold")
    table.add_column("Value", style="dim")
    for k, v in rows:
        table.add_row(k, str(v))
    console.print(Panel(table, title=title, border_style="cyan"))


# ── Non-interactive demo path ─────────────────────────────────────────────

def run_demo_once() -> None:
    section("1) Value inspection (feel)")
    v = Vector2(3, 4).scale(2)
    show_value_panel("feel(Vector2(3,4).scale(2))", feel(v))

    section("2) Source viewer (source)")
    show_value_panel("source(flaky_divide)", source(flaky_divide))

    section("3) Exception rendering")
    try:
        exercise()
    except Exception as e:
        show_value_panel("feel(exception)", feel(e))

    section("4) Debug wrapping (embrace)")
    orig = embrace(globals())
    # A normal call (traced)
    _ = flaky_divide(10, 2)
    # An exception (traced)
    try:
        flaky_divide(-1, 1)
    except Exception:
        pass
    release(globals(), orig)

    section("5) Live edit & retouch (manual)")
    show_table("Try these in Touch", [
        ("Edit function", "edit(flaky_divide)  # remove the guard, save, return"),
        ("Re-run caller", "exercise()         # should now return -0.2, no exception"),
        ("Inject code",  'retouch(globals(), seed="\\n".join(['
                            '"def twice(x):", "    return x*2"]))'),
        ("Use injected", "twice(21)           # expect 42"),
    ])


# ── Interactive path (guidance + Touch REPL) ──────────────────────────────

def run_interactive() -> None:
    # Guidance
    console.print(Panel.fit(Text.from_markup(
        """[b]Touch demo[/b]

        You will drop into the Touch REPL next.
        Try the following commands:

        [b cyan]# Inspect values[/b cyan]
            feel(Vector2(3,4))
            source(flaky_divide)

        [b cyan]# Pretty exceptions[/b cyan]
            try:
                exercise()
            except Exception as e:
                feel(e)

        [b cyan]# Debug wrapping[/b cyan]
            o = embrace(globals())
            flaky_divide(10, 2)
            try: flaky_divide(-1, 1)
            except: pass
            release(globals(), o)

        [b cyan]# Live edit[/b cyan]
            edit(flaky_divide)   # remove the guard and save
            exercise()           # should now return -0.2

        [b cyan]# Inject new helpers[/b cyan]
            retouch(globals(), seed="def triple(x):\\n    return x*3")
            triple(7)
        """
    ), title="Instructions", border_style="magenta"))

    # Open Touch REPL with write-through globals
    touch(globals(), locals())


# ── Entry point ───────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Hyv Touch showcase")
    ap.add_argument("--demo", action="store_true", help="run non-interactive showcase once")
    ap.add_argument("--interactive", action="store_true", help="force interactive mode")
    args = ap.parse_args()

    if args.interactive and not args.demo:
        run_interactive()
    else:
        run_demo_once()


if __name__ == "__main__":
    main()