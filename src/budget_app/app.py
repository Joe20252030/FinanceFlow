#!/usr/bin/env python3
"""FinanceFlow application entrypoint.

This module locates and imports the GUI `MainWindow`, creates the root
window (preferring `ttkbootstrap.Window` when available), instantiates
the main window UI and starts the Tk event loop.

Usage (development):
    PYTHONPATH=src .venv/bin/python -m budget_app.app
    or
    .venv/bin/python -m src.budget_app.app

When packaged with PyInstaller, this file can be used as the entrypoint.
"""

from __future__ import annotations

import sys
import traceback


def _import_mainwindow():
    """Import MainWindow from the package using several fallbacks.

    Attempts (in order):
    - package-relative import (when run as a package)
    - top-level package import (when PYTHONPATH contains 'src')
    - src-based absolute import (when running as module)
    """
    # 1) relative import (when executed as package: python -m budget_app.app)
    try:
        from .ui.main_window import MainWindow  # type: ignore
        return MainWindow
    except Exception:
        pass

    # 2) top-level package import (when PYTHONPATH=src)
    try:
        from budget_app.ui.main_window import MainWindow  # type: ignore
        return MainWindow
    except Exception:
        pass

    # 3) src absolute path import (when invoked as python -m src.budget_app.app)
    try:
        from src.budget_app.ui.main_window import MainWindow  # type: ignore
        return MainWindow
    except Exception:
        pass

    raise ImportError("Could not import MainWindow from src.budget_app.ui.main_window")


def _create_root():
    """Create a Tk root window, preferring ttkbootstrap if available.

    Returns the root window object. The caller is responsible for calling
    mainloop() or otherwise running the event loop.
    """
    try:
        import ttkbootstrap as tb  # optional dependency

        # tb.Window offers theming and behaves like Tk root
        return tb.Window(themename="flatly")
    except Exception:
        import tkinter as tk

        return tk.Tk()


def main(argv: list[str] | None = None) -> None:
    argv = list(argv or sys.argv[1:])
    try:
        MainWindow = _import_mainwindow()

        # Some MainWindow implementations expect no args (they create their
        # own root), while others accept a parent/root argument. Try no-arg
        # instantiation first, fall back to creating a root and passing it.
        ui = None
        try:
            ui = MainWindow()
        except TypeError:
            # Try passing an explicit root
            root = _create_root()
            root.title("FinanceFlow")
            try:
                root.geometry("1000x700")
            except Exception:
                pass
            ui = MainWindow(root)

        # Prefer a run() method if present; otherwise prefer ui.mainloop();
        # if ui doesn't offer mainloop but we created a root, run root.mainloop().
        if hasattr(ui, "run") and callable(getattr(ui, "run")):
            ui.run()  # type: ignore
        elif hasattr(ui, "mainloop") and callable(getattr(ui, "mainloop")):
            ui.mainloop()  # type: ignore
        elif 'root' in locals():
            root.mainloop()
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
