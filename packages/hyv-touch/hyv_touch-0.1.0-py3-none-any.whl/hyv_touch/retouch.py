import os, tempfile, subprocess, shutil, textwrap, traceback
from typing import Any, Dict, Optional

from .shared import get_scope, set_scope


def retouch(
    scope: Optional[Dict[str, Any]] = None,
    seed: str | None = None,
    name_hint: str = "snippet",
    reuse_window: bool = True,
    new_window: bool = False,
    public_only: bool = False,
    dry_run: bool = False,
) -> str:
    """
    * retouch: open a temporary file in VS Code, let the user write functions/classes/values,
      then import the definitions into `scope` when the editor closes.

    @param scope        Dict-like namespace to inject into (e.g., globals()).
    @param seed         Optional starter code written into the temp file.
    @param name_hint    Used for the temp filename/title.
    @param reuse_window Pass '--reuse-window' to VS Code (default True).
    @param new_window   Pass '--new-window' to VS Code (overrides reuse_window).
    @param public_only  If True, the summary only lists names not starting with '_' (injection still occurs for all).
    @param dry_run      If True, compile and validate but do not inject into `scope`.

    @returns            Summary string listing added/changed names.

    ! Safety: we snapshot `scope` before exec; on any exception we restore it wholesale.
    ? Why exec into `scope` directly:
      So newly created functions bind their __globals__ to the live environment
      (imports and shared state resolve correctly at call time), not to a dead temp dict.
    """

    # Fallback exception types if user didn't define them elsewhere
    class _VSCodeNotFound(RuntimeError): ...

    class _EditError(RuntimeError): ...

    # locate 'code' CLI; use user's helper if available, else best-effort
    def _find_code_cli() -> str:
        try:
            return _which_code()  # type: ignore[name-defined]
        except Exception:
            exe = shutil.which("code") or (
                shutil.which("code.cmd") if os.name == "nt" else None
            )
            if not exe:
                raise _VSCodeNotFound(
                    "VS Code CLI not found. Install 'code' on PATH or use your editor via EDITOR."
                )
            return exe

    # ── prepare file contents ────────────────────────────────────────────────
    header = (
        "# retouch: temporary workspace\n"
        "# Write any functions, classes, or values below. Save & close to apply.\n"
        "# Names are injected into the active scope on success.\n"
        "from __future__ import annotations\n\n"
    )
    if seed is None:
        seed = (
            "def example(x: int) -> int:\n"
            '    """Sample function. Replace or delete me."""\n'
            "    return x + 1\n"
        )

    code_cli = _find_code_cli()
    temp_dir = tempfile.mkdtemp(prefix=f"retouch_{name_hint}_")
    temp_path = os.path.join(temp_dir, f"{name_hint}.py")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(textwrap.dedent(seed))
        f.write("\n")

    # ── open VS Code and wait ────────────────────────────────────────────────
    args = [code_cli, "--wait", temp_path]
    if new_window:
        args.append("--new-window")
    elif reuse_window:
        args.append("--reuse-window")
    subprocess.run(args, check=False)

    # ── read + compile ───────────────────────────────────────────────────────
    with open(temp_path, "r", encoding="utf-8") as f:
        edited = f.read()
        
    compiled = compile(edited, temp_path, "exec")

    # ── snapshot/rollback guards ─────────────────────────────────────────────

    scope = scope or get_scope()

    before = dict(scope)  # full snapshot for rollback
    before_keys = set(scope.keys())  # to report added/changed
    try:
        if dry_run:
            return "Syntax OK (dry run); no changes applied."
        # exec into the LIVE scope so newly defined functions close over the real globals
        exec(compiled, scope, scope)
    except Exception as e:
        scope.clear()
        scope.update(before)
        raise _EditError(
            f"retouch failed; scope restored.\n{traceback.format_exc()}"
        ) from e
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

    # ── diff & summary ───────────────────────────────────────────────────────
    after_keys = set(scope.keys())

    def _vis(name: str) -> bool:
        return (not public_only) or (name and not name.startswith("_")) # type: ignore

    added = [k for k in (after_keys - before_keys) if _vis(k)]
    changed = [
        k
        for k in (after_keys & before_keys)
        if scope.get(k) is not before.get(k) and _vis(k)
    ]

    set_scope(scope)

    def _fmt(lst):
        return ", ".join(sorted(lst)) if lst else "—"

    return f"retouch applied. added: [{_fmt(added)}]; changed: [{_fmt(changed)}]"
