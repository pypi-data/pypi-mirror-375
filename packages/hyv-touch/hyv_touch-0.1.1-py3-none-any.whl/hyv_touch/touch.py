from __future__ import annotations

from typing import Optional, Any

from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text
from rich.traceback import Traceback
from rich.protocol import is_renderable  # ← correct detection

# Touch utilities
from hyv_touch.feel import feel
from hyv_touch.tickle import tickle
from hyv_touch.source import source
from hyv_touch.embrace import embrace, release
from hyv_touch.edit import edit
from hyv_touch.retouch import retouch
from hyv_touch.shared import console, get_scope, set_scope


EXEC_MODE_TAG = "$exec"


def touch(_globals: dict[str, Any], _locals: dict[str, Any] = {}) -> None:
    """
    Minimal interactive REPL:
      - Default: eval expressions
      - Use [exec] tag to run statements
      - Persistent environment across inputs
      - Rich panels, pretty results, rich tracebacks
      - Exit with: exit / quit / Ctrl+D / Ctrl+C

    # Utilities
        - feel(obj)        — inspect objects / pretty debug
        - source(obj)      — view source code of functions, classes, modules
        - embrace(fn)      — decorate every function in scope with debug_wrap / debugger
        - release(fn)      — remove embrace wrappers, restore originals
        - edit(obj)        — open in editor, auto-reload on save
        - retouch(module)  — add new symbols to scope
        - tickle(main_file)  — re-interpret main file, update scope new symbols only
    """
    console.clear()
    console.print(
        Panel.fit(
            Text.from_markup(
                "[note]Type 'exit' or 'quit' to leave.\n"
                "[b]Touch Mode[/b]\n"
                "Default is [b]eval[/b]; include [b]$exec[/b] to run statements.[/note]"
            ),
            title="Touch",
            border_style="border",
        )
    )

    # panel explanation of utilities
    console.print(
        Panel.fit(
            Text.from_markup(
                "[note]Utilities:\n"
                "[b]feel(obj)[/b]        — inspect objects / pretty debug\n"
                "[b]source(obj)[/b]      — view source code of functions, classes, modules\n"
                "[b]embrace(fn)[/b]      — decorate every function in scope with debug_wrap / debugger\n"
                "[b]release(fn)[/b]      — remove embrace wrappers, restore originals\n"
                "[b]edit(obj)[/b]        — open in editor, auto-reload on save\n"
                "[b]retouch(module)[/b]  — add new symbols to scope\n"
                "[b]tickle(main_file)[/b]  — re-interpret main file, update scope with new symbols only[/note]"
            ),
            title="Utilities",
            border_style="border",
        )
    )

    # Build the live environment and publish it to the package
    env: dict[str, object] = {**_globals, **_locals}
    env.update(
        {
            # Handy builtins for Touch users
            "feel": feel,
            "source": source,
            "embrace": embrace,
            "release": release,
            "edit": edit,
            "retouch": retouch,
            "tickle": tickle,
        }
    )
    set_scope(env)

    while True:
        try:
            prompt = Text("Touch> ", style="prompt")
            q: Optional[str] = console.input(prompt)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[ok]Exiting Touch.[/]")
            return

        if not q:
            continue
        q = q.strip()
        if q.lower() in {"exit", "quit"}:
            console.print("[ok]Bye.[/]")
            return
        
        # re-blend scope because it can be mutated by retouch/tickle
        env.update(**get_scope())

        exec_mode = EXEC_MODE_TAG in q
        if exec_mode:
            code = q.replace(EXEC_MODE_TAG, "").strip()
            if not code:
                continue
            try:
                exec(code, env, env)
                console.print(Panel.fit("[ok]✓ Executed[/]", border_style="ok"))
            except Exception as e:
                tb = Traceback.from_exception(type(e), e, e.__traceback__)
                console.print(
                    Panel(tb, title="[err]Execution Error[/]", border_style="err")
                )
            continue

        # Eval mode
        try:
            result = eval(q, env, env)
            env["_"] = result  # assign convenience reference

            # Render smartly: native Rich renderables as-is, else pretty panel
            if is_renderable(result):
                console.print(result)
            else:
                body = Pretty(result, expand_all=False)
                console.print(Panel(body, title="Result", border_style="ok"))
        except Exception as e:
            tb = Traceback.from_exception(type(e), e, e.__traceback__)
            console.print(
                Panel(tb, title="[err]Evaluation Error[/]", border_style="err")
            )


if __name__ == "__main__":
    touch(globals(), locals())
