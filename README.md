# FinanceFlow
A budget management system using AI to plan and organize daily spend

# Overview
Budget UI is a desktop application for planning and visualizing personal budgets.
It provides an intuitive interface built with PySide6 (Qt for Python) and a clean, validated backend powered by Pydantic.

The app lets users:
-Input income, fixed expenses, and spending preferences
-Automatically generate a recommended allocation plan
-View results in a dynamic table
-Export plans as CSV or PDF

The business logic is fully separated from the user interface for easy testing and future extension.

# Project Structure
budget_ui/
├─ README.md
├─ pyproject.toml               # dependencies: pyside6, pydantic
├─ assets/                      # icons, stylesheets
│  └─ styles.qss
├─ src/
│  └─ budget_app/
│     ├─ app.py                 # Qt entry point
│     ├─ core/                  # pure data & logic layer
│     │  ├─ models.py           # Pydantic models for inputs/outputs
│     │  ├─ planner.py          # budget allocation engine
│     │  └─ defaults.py         # default categories & settings
│     ├─ ui/                    # PySide6 widgets, dialogs, windows
│     │  ├─ main_window.py
│     │  ├─ inputs_view.py
│     │  ├─ plan_view.py
│     │  └─ export_dialog.py
│     └─ utils/
│        ├─ money.py            # precise Decimal/Money helpers
│        └─ export.py           # CSV/PDF export utilities
├─ examples/
│  └─ input_min.json            # minimal example input
└─ tests/
   └─ test_planner.py           # unit tests for planner logic

# Requirements
-Python 3.10+
-PySide6
-Pydantic v2
-(optional) reportlab for PDF export
-(optional) pytest for testing

# Installation
1. Clone the repository
    git clone https://github.com/<yourusername>/budget_ui.git
    cd budget_ui

2. Create and activate a virtual environment
    python3 -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # or
    .venv\Scripts\activate     # Windows

3. Install dependencies
    pip install -e .
If you don’t use pyproject.toml yet:
    pip install pyside6 pydantic reportlab pytest

# Running the App
python -m budget_app.app
or (if app.py has a main() function):
python src/budget_app/app.py

This launches the Qt main window. You can load an example input via:
examples/input_min.json

# Development Notes
-Core is pure logic — no Qt imports. Testable with pytest.
-UI uses PySide6 (Qt Widgets). Stylesheets are in assets/styles.qss.
-Money values are Decimal-based for accurate rounding.
-Planner produces a PlanResult object summarizing allocations, totals, and warnings.
-Export supports CSV (always) and PDF (if reportlab installed).

# Testing
pytest
Example output:
tests/test_planner.py::test_basic_plan PASSED

# Packaging
    pip install pyinstaller
    pyinstaller src/budget_app/app.py --noconsole --name BudgetUI

# Roadmap
-Add pie chart visualization for spending ratios
-Support multi-month projections
-Add language/localization support
-Cloud sync for multiple profiles

# License
