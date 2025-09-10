#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_install.py

Auto-install missing Python dependencies at runtime or preflight.

Usage:
    - Import this module at the top of your script:
        import check_install
        check_install.install_hooks_and_preflight()

    - If any import fails or is missing, it will attempt to install it via pip,
      then re-exec your script.

Notes:
    - Meant to be used in development or throwaway scripts, not production.
    - Requires 'rich' for colored output, but gracefully degrades if absent.
"""

from __future__ import annotations

import ast
import os
import sys
import subprocess
import time
import traceback
import importlib.util
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, NoReturn

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.text import Text
    from rich.rule import Rule

    RICH = True
    console = Console()
except Exception:
    RICH = False
    console = None  # type: ignore

# Maps common import names to their actual PyPI package names.
# Used to resolve discrepancies between import paths and installable package names.
# This ensures auto-install works for packages like 'PIL' → 'pillow', 'sklearn' → 'scikit-learn', etc.
NAME_MAP: Dict[str, str] = {
    "Crypto": "pycryptodome",
    "IPython": "ipython",
    "OpenGL": "PyOpenGL",
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "firebase_admin": "firebase-admin",
    "flask_sqlalchemy": "Flask-SQLAlchemy",
    "jinja2": "Jinja2",
    "mpl_toolkits": "matplotlib",
    "mysql": "mysqlclient",
    "psycopg2": "psycopg2-binary",
    "pymysql": "PyMySQL",
    "skimage": "scikit-image",
    "sklearn": "scikit-learn",
    "wx": "wxPython",
    "yaml": "PyYAML",
    "zope": "zope.interface",
}


ENV_ATTEMPTED = "AUTOINSTALL_ATTEMPTED"
ENV_PREFLIGHT_DONE = "PREFLIGHT_DONE"


def _clear() -> None:
    """Clear the terminal screen (cross-platform)."""
    try:
        subprocess.run(["cls" if os.name == "nt" else "clear"], check=False)
    except Exception:
        pass


def _in_virtualenv() -> bool:
    """Detect if running inside a virtual environment."""
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def get_root_module(name: str) -> str:
    """Return the top-level module of a dotted import string."""
    return name.split(".", 1)[0] if "." in name else name


def map_to_pypi(name: str) -> str:
    """Map an import name to its PyPI package name."""
    return NAME_MAP.get(name, name)


def _already_attempted(names: Iterable[str]) -> bool:
    """Check if a module was already attempted to install."""
    attempted = set(filter(None, os.environ.get(ENV_ATTEMPTED, "").split(",")))
    return any(n in attempted for n in names)


def _record_attempt(names: Iterable[str]) -> None:
    """Record an attempted install to prevent infinite retry loops."""
    attempted = set(filter(None, os.environ.get(ENV_ATTEMPTED, "").split(",")))
    attempted.update(names)
    os.environ[ENV_ATTEMPTED] = ",".join(sorted(attempted))


def _pip_install(package: str) -> Tuple[bool, str]:
    """Try to install the given package via pip and return success + output."""
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.returncode == 0, proc.stdout


def _restart() -> NoReturn:
    """Restart the current Python script with the same arguments."""
    os.execv(sys.executable, [sys.executable] + sys.argv)


def _infer_from_msg(msg: str) -> Optional[str]:
    """Try to extract a missing module name from an exception string."""
    if "'" in msg:
        parts = msg.split("'")
        if len(parts) >= 2 and parts[1]:
            return parts[1]
    return None


def _context() -> None:
    """Display interpreter and environment context info."""
    if RICH:
        t = Text()
        t.append("Interpreter: ", style="bold")
        t.append(sys.executable)
        t.append("\nIn venv: ", style="bold")
        t.append(str(_in_virtualenv()))
        console.print(Panel(t, title="Context", expand=False))
        return
    print(f"\nInterpreter: {sys.executable}\nIn venv:     {_in_virtualenv()}")


def _heading(s: str) -> None:
    """Display a visual section heading."""
    if RICH:
        console.print(Rule(s))
    else:
        print(f"\n=== {s} ===")


def _show_missing(pairs: Sequence[Tuple[str, str]]) -> None:
    """Show a list of missing modules and their corresponding PyPI packages."""
    if RICH:
        table = Table(title="Missing Dependencies", show_lines=False)
        table.add_column("Import name", style="cyan")
        table.add_column("PyPI package")
        for mod, pkg in pairs:
            table.add_row(mod, pkg if mod == pkg else f"{pkg}  (from '{mod}')")
        console.print(table)
    else:
        print("\nMissing dependencies:")
        for mod, pkg in pairs:
            print(f" - {mod} -> {pkg}")


def _failures(failures: Sequence[Tuple[str, str]]) -> None:
    """Display a failure report and exit the program."""
    _clear()
    if RICH:
        table = Table(title="Installation Failures")
        table.add_column("PyPI package", style="bold red")
        table.add_column("pip output (tail)")
        for pkg, out in failures:
            tail = "\n".join((out or "").strip().splitlines()[-12:]) or "No output."
            table.add_row(pkg, tail)
        console.print(table)
        cmds = "\n".join(f"- pip install {p}" for p, _ in failures)
        console.print(
            f"\n[bold]Next steps[/]: try manual installation, check network/proxy, or use a virtual environment.\n\n[bold]Manual commands:[/]\n{cmds}"
        )
    else:
        print("\nInstall failures:")
        for pkg, out in failures:
            print(f" - {pkg}\n" + "\n".join((out or "").splitlines()[-12:]))
        print("\nManual commands:")
        for pkg, _ in failures:
            print(f"  pip install {pkg}")
    sys.exit(1)


def _ast_imports(path: str) -> List[str]:
    """Parse the file and return a list of top-level imports."""
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)

    names: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    names.add(get_root_module(alias.name))
        elif isinstance(node, ast.ImportFrom):
            if not node.level and node.module:
                names.add(get_root_module(node.module))

    names.discard("__main__")
    return sorted(names)


def _scan_missing(path: str) -> List[str]:
    """Return list of missing modules from a script."""
    return sorted({n for n in _ast_imports(path) if importlib.util.find_spec(n) is None})


def _runtime_hook(exc_type, exc, tb):
    """Exception hook for ModuleNotFoundError – install and restart if needed."""
    if exc_type is not ModuleNotFoundError:
        return sys.__excepthook__(exc_type, exc, tb)

    miss = getattr(exc, "name", None) or _infer_from_msg(str(exc)) or "UNKNOWN"
    top = get_root_module(miss)
    pkg = map_to_pypi(top)
    last = traceback.extract_tb(tb)[-1] if tb else None

    _clear()

    if RICH:
        hdr = Text()
        hdr.append("Required dependency not found: ", style="bold")
        hdr.append(top, style="bold red")
        if last:
            hdr.append("\nFailure site: ")
            hdr.append(f"{last.filename}:{last.lineno}", style="italic")
        console.print(Panel(hdr, title="Missing Dependency", expand=False))
    else:
        print("\n❌ Required dependency not found!")
        print(f"   → '{top}' is missing.")
        if last:
            print(f"   Failure site: {last.filename}:{last.lineno}")

    _context()

    if _already_attempted([top]):
        _failures([(pkg, "Import still failing after attempted installation.")])

    if RICH:
        proceed = Confirm.ask(
            f"Attempt to auto-install missing package '[bold]{pkg}[/]' now with [italic]{os.path.basename(sys.executable)} -m pip[/]?",
            default=True,
            show_default=True,
        )
    else:
        proceed = input(
            f"\nAttempt to auto-install missing package '{pkg}' now with '{sys.executable} -m pip'? [Y/n]: "
        ).strip().lower() in ("", "y", "yes")

    _clear()

    if not proceed:
        if RICH:
            console.print(Panel(f"Manual install:\n\npip install {pkg}", title="Installation Skipped", expand=False))
        else:
            print(f"\nTry: pip install {pkg}\n")
        sys.exit(1)

    _record_attempt([top])
    ok, out = _pip_install(pkg)

    if ok:
        if RICH:
            console.print(Panel(f"Installed {pkg} successfully.\nRestarting…", expand=False))
        else:
            print(f"\nInstalled {pkg} successfully. Restarting…\n")
        _restart()

    _failures([(pkg, out or "No pip output")])


def install_hooks_and_preflight() -> None:
    """Enable runtime hook and perform AST-based preflight dependency check."""
    sys.excepthook = _runtime_hook

    if os.environ.get(ENV_PREFLIGHT_DONE) == "1":
        return

    script = sys.argv[0] if sys.argv and sys.argv[0] else ""
    if not (script and os.path.exists(script)):
        return

    missing = _scan_missing(os.path.abspath(script))
    if not missing:
        return

    pairs = [(m, map_to_pypi(m)) for m in missing]

    _clear()
    _heading("Missing Dependencies Detected")
    _show_missing(pairs)
    _context()

    names = [m for m, _ in pairs]
    if _already_attempted(names):
        return

    if RICH:
        proceed = Confirm.ask(f"Attempt to auto-install missing {len(pairs)} package(s) now?", default=True, show_default=True)
    else:
        proceed = input(
            f"\nAttempt to auto-install missing {len(pairs)} package(s) now? [Y/n]: "
        ).strip().lower() in ("", "y", "yes")

    _clear()

    if not proceed:
        if RICH:
            cmds = "\n".join(f"- pip install {map_to_pypi(n)}" for n in names)
            console.print(Panel(f"Manual install commands:\n\n{cmds}", title="Installation Skipped", expand=False))
        else:
            print("\nManual install commands:")
            for n in names:
                print(f"  pip install {map_to_pypi(n)}")
        sys.exit(1)

    _record_attempt(names)
    failures: List[Tuple[str, str]] = []

    for _, pkg in pairs:
        ok, out = _pip_install(pkg)
        if not ok:
            failures.append((pkg, out))

    if failures:
        _failures(failures)

    os.environ[ENV_PREFLIGHT_DONE] = "1"

    app_name = os.path.basename(script) or "application"

    if RICH:
        console.print(Panel(f"All required packages installed successfully.\nRestarting {app_name}…", expand=False))
    else:
        print(f"\nAll required packages installed successfully. Restarting {app_name}...\n")

    time.sleep(2)
    _clear()
    _restart()

