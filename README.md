# FinanceFlow Budget Planner

A modern cross-platform personal budget planner built with Python, Tkinter, and ttkbootstrap. Supports multi-language UI, CSV export, and visual budget summaries.

## Features
- Modern GUI with ttkbootstrap
- Multi-language support (English/Chinese)
- Income, fixed costs, and budget preference input
- Automatic budget allocation
- Bar chart summary (matplotlib)
- Export budget plan to CSV (with total summary)
- SVG/PNG icon support

## Requirements
- Python 3.8+
- ttkbootstrap
- matplotlib
- pillow
- cairosvg
- reportlab (optional, for PDF export)

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd remake
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install ttkbootstrap matplotlib pillow cairosvg reportlab
   ```

## Usage
Run the app from the main entry point:
```bash
python src/budget_app/app.py
```
Or, if you have a run.py in the root:
```bash
python run.py
```

## Project Structure
```
assets/           # Images, icons, fonts, styles
src/
  budget_app/
    app.py        # Main entry point
    ui/
      main_window.py
      inputs_view.py
      plan_view.py
      export_dialog.py
    core/
      api.py      # Budget logic
    utils/
      export.py   # Export helpers
      money.py    # Money formatting
```


## Credits
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)
- [matplotlib](https://matplotlib.org/)
- [Pillow](https://python-pillow.org/)
- [CairoSVG](https://cairosvg.org/)
- [ReportLab](https://www.reportlab.com/)

