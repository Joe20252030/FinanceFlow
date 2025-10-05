import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk, ImageFont

# cairosvg can require native cairo libs; import lazily where needed
try:
    import cairosvg
    _CAIROSVG_AVAILABLE = True
except Exception:
    cairosvg = None
    _CAIROSVG_AVAILABLE = False

LANGUAGES = {
    'en': {
        'income_input': 'Income Input',
        'add_income': 'Add Income Source',
        'fixed_costs': 'Fixed Costs',
        'budget_prefs': 'Budget Preferences',
        'constraint_settings': 'Constraints',
        'add_constraint': 'Add Constraint Category',
        'plan_total': 'Total Allocation: {percent}%',
        'submit': 'Generate Plan',
        'reset': 'Reset',
        'delete': 'Delete',
        'error_percent': 'Total allocation must be 100%',
        'period_month': 'Month',
        'period_week': 'Week',
        'categories': ['Dining', 'Shopping', 'Transport', 'Savings'],
        'fixed_labels': ['Rent', 'Utilities', 'Phone', 'Insurance'],
        'constraint_labels': ['Dining', 'Shopping', 'Transport', 'Savings'],
    },
    'zh': {
        'income_input': '收入输入',
        'add_income': '添加收入来源',
        'fixed_costs': '固定支出',
        'budget_prefs': '预算偏好',
        'constraint_settings': '约束设置',
        'add_constraint': '添加约束类别',
        'plan_total': '总分配: {percent}%',
        'submit': '生成计划',
        'reset': '重置',
        'delete': '删除',
        'error_percent': '预算分配总和必须为100%',
        'period_month': '月',
        'period_week': '周',
        'categories': ['餐饮', '购物', '交通', '储蓄'],
        'fixed_labels': ['房租', '水电', '电话', '保险'],
        'constraint_labels': ['餐饮', '购物', '交通', '储蓄'],
    }
}
CURRENT_LANG = 'en'

class InputsView(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.lang = CURRENT_LANG
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        style = tb.Style()
        style.configure("Custom.TFrame", background="#F0F0F0")

    # Scrollable area (vertical and horizontal scrollbars)
        self.canvas = tb.Canvas(self, bg="#F0F0F0", highlightthickness=0)
        self.scroll_frame = tb.Frame(self.canvas, style="Custom.TFrame")
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.window_id = self.canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    # Only bind mouse-wheel events while the cursor is over the canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    # Error message area
        self.error_label = tb.Label(self.scroll_frame, text="", bootstyle=DANGER)
        self.error_label.pack(pady=2, anchor="center")
    # Income input area
        self.income_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['income_input'], bootstyle=INFO)
        self.income_frame.pack(pady=10, anchor="center")
        self.income_entries = []
        self.add_income_entry(self.income_frame)
        self.add_income_btn = tb.Button(self.income_frame, text=LANGUAGES[self.lang]['add_income'], command=lambda: self.add_income_entry(self.income_frame), bootstyle=SECONDARY)
        self.add_income_btn.pack(side="right", padx=10, pady=5)

    # Fixed expense area
        self.fixed_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['fixed_costs'], bootstyle=WARNING)
        self.fixed_frame.pack(pady=10, anchor="center")
        self.fixed_entries = []
        for label in LANGUAGES[self.lang]['fixed_labels']:
            self.add_fixed_entry(self.fixed_frame, label)

    # Budget preferences area
        self.prefs_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['budget_prefs'], bootstyle=SUCCESS)
        self.prefs_frame.pack(pady=10, anchor="center")
        self.pref_entries = []
        for label in LANGUAGES[self.lang]['categories']:
            self.add_pref_entry(self.prefs_frame, label)
        self.percent_total_label = tb.Label(self.prefs_frame, text=LANGUAGES[self.lang]['plan_total'].format(percent=0), bootstyle=INFO)
        self.percent_total_label.pack(side="right", padx=10)

    # Constraints area
        self.constraint_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['constraint_settings'], bootstyle=DANGER)
        self.constraint_frame.pack(pady=10, anchor="center")
        self.constraint_entries = []
        for label in LANGUAGES[self.lang]['constraint_labels']:
            self.add_constraint_entry(self.constraint_frame, label)
        self.add_constraint_btn = tb.Button(self.constraint_frame, text=LANGUAGES[self.lang]['add_constraint'], command=lambda: self.add_constraint_entry(self.constraint_frame, LANGUAGES[self.lang]['constraint_labels'][0]), bootstyle=SECONDARY)
        self.add_constraint_btn.pack(side="right", padx=10, pady=5)

    # Submit and reset controls
        btn_frame = tb.Frame(self.scroll_frame)
        btn_frame.pack(pady=15, anchor="center")
        self.submit_btn = tb.Button(btn_frame, text=LANGUAGES[self.lang]['submit'], bootstyle=PRIMARY, command=self.submit)
        self.submit_btn.pack(side="left", padx=10)
        self.reset_btn = tb.Button(btn_frame, text=LANGUAGES[self.lang]['reset'], bootstyle=SECONDARY, command=self.reset)
        self.reset_btn.pack(side="right", padx=10)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Center the scroll_frame inside the canvas
        canvas_width = event.width
        frame_width = self.scroll_frame.winfo_reqwidth()
        x = max((canvas_width - frame_width) // 2, 0)
        self.canvas.coords(self.window_id, x, 0)

    def _on_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120  # macOS compatibility
        self.canvas.yview_scroll(int(-1*(delta/120)), "units")
        return "break"

    def _on_shift_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120
        self.canvas.xview_scroll(int(-1*(delta/120)), "units")
        return "break"

    def set_language(self, lang):
        self.lang = lang
        # Update all section titles and button texts
        self.income_frame.config(text=LANGUAGES[lang]['income_input'])
        self.add_income_btn.config(text=LANGUAGES[lang]['add_income'])
        self.fixed_frame.config(text=LANGUAGES[lang]['fixed_costs'])
        self.prefs_frame.config(text=LANGUAGES[lang]['budget_prefs'])
        self.percent_total_label.config(text=LANGUAGES[lang]['plan_total'].format(percent=self.get_percent_total()))
        self.constraint_frame.config(text=LANGUAGES[lang]['constraint_settings'])
        self.add_constraint_btn.config(text=LANGUAGES[lang]['add_constraint'])
        self.submit_btn.config(text=LANGUAGES[lang]['submit'])
        self.reset_btn.config(text=LANGUAGES[lang]['reset'])
        self.error_label.config(text="")
        # 更新各项label
        for i, (label, amt_entry) in enumerate(self.fixed_entries):
            # fixed_entries stores tuples (label, amt_entry): label is a string, amt_entry is the Entry widget
            # find the corresponding Label widget and update its text
            frame = amt_entry.master
            lbl = frame.winfo_children()[0]
            lbl.config(text=LANGUAGES[lang]['fixed_labels'][i])
        for i, (frame, src_entry, period_combo, amt_entry) in enumerate(self.income_entries):
            period_combo.config(values=[LANGUAGES[lang]['period_month'], LANGUAGES[lang]['period_week']])
            period_combo.set(LANGUAGES[lang]['period_month'])
        for i, (label, spin) in enumerate(self.pref_entries):
            lbl = spin.master.winfo_children()[0]
            lbl.config(text=LANGUAGES[lang]['categories'][i])
        for i, (frame, label, min_spin, max_spin) in enumerate(self.constraint_entries):
            lbl = frame.winfo_children()[0]
            lbl.config(text=LANGUAGES[lang]['constraint_labels'][i % len(LANGUAGES[lang]['constraint_labels'])])
            del_btn = frame.winfo_children()[-1]
            del_btn.config(text=LANGUAGES[lang]['delete'])

    def get_percent_total(self):
        total = 0
        for _, spin in self.pref_entries:
            try:
                total += int(spin.get())
            except ValueError:
                pass
        return total

    def add_income_entry(self, parent):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        src_entry = tb.Entry(frame, width=12)
        src_entry.pack(side="left", padx=5)
        period_combo = tb.Combobox(frame, values=[LANGUAGES[self.lang]['period_month'], LANGUAGES[self.lang]['period_week']], width=5)
        period_combo.set(LANGUAGES[self.lang]['period_month'])
        period_combo.pack(side="left", padx=5)
        amt_entry = tb.Entry(frame, width=10)
        amt_entry.pack(side="left", padx=5)
        del_btn = tb.Button(frame, text=LANGUAGES[self.lang]['delete'], bootstyle=DANGER, command=lambda: self._del_income_entry(frame))
        del_btn.pack(side="left", padx=5)
        self.income_entries.append((frame, src_entry, period_combo, amt_entry))

    def _del_income_entry(self, frame):
        for entry in self.income_entries:
            if entry[0] == frame:
                entry[0].destroy()
                self.income_entries.remove(entry)
                break

    def add_fixed_entry(self, parent, label):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        lbl = tb.Label(frame, text=label, width=10)
        lbl.pack(side="left", padx=5)
        amt_entry = tb.Entry(frame, width=10)
        amt_entry.pack(side="left", padx=5)
        self.fixed_entries.append((label, amt_entry))

    def add_pref_entry(self, parent, label):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        lbl = tb.Label(frame, text=label, width=10)
        lbl.pack(side="left", padx=5)
        percent_spin = tb.Spinbox(frame, from_=0, to=100, width=5, command=self.update_percent_total)
        percent_spin.pack(side="left", padx=5)
        self.pref_entries.append((label, percent_spin))

    def update_percent_total(self):
        total = 0
        for _, spin in self.pref_entries:
            try:
                total += int(spin.get())
            except ValueError:
                pass
        self.percent_total_label.config(text=LANGUAGES[self.lang]['plan_total'].format(percent=total))
        if total != 100:
            self.error_label.config(text=LANGUAGES[self.lang]['error_percent'])
        else:
            self.error_label.config(text="")

    def add_constraint_entry(self, parent, label):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        lbl = tb.Label(frame, text=label, width=10)
        lbl.pack(side="left", padx=5)
        min_spin = tb.Spinbox(frame, from_=0, to=100, width=5)
        min_spin.pack(side="left", padx=5)
        max_spin = tb.Spinbox(frame, from_=0, to=100, width=5)
        max_spin.pack(side="left", padx=5)
        del_btn = tb.Button(frame, text=LANGUAGES[self.lang]['delete'], bootstyle=DANGER, command=lambda: self._del_constraint_entry(frame))
        del_btn.pack(side="left", padx=5)
        # Hover hints
        def show_min_hint(event):
            hint = "Minimum budget" if self.lang == "en" else "最小预算"
            self.controller.button_hint_label.config(text=hint)
        def show_max_hint(event):
            hint = "Maximum budget" if self.lang == "en" else "最大预算"
            self.controller.button_hint_label.config(text=hint)
        def clear_hint(event):
            self.controller.button_hint_label.config(text="")
        min_spin.bind("<Enter>", show_min_hint)
        min_spin.bind("<Leave>", clear_hint)
        max_spin.bind("<Enter>", show_max_hint)
        max_spin.bind("<Leave>", clear_hint)
        self.constraint_entries.append((frame, label, min_spin, max_spin))

    def _del_constraint_entry(self, frame):
        for entry in self.constraint_entries:
            if entry[0] == frame:
                entry[0].destroy()
                self.constraint_entries.remove(entry)
                break

    def submit(self):
        # Collect all inputs, validate and pass to planner
        # Build a PlanningInput from UI values and call the main window's planner
        try:
            from src.budget_app.core.defaults import starter_input
            from src.budget_app.core.models import Income, FixedExpense
            from src.budget_app.utils.money import Money
        except Exception:
            # fallback to package imports if running as module
            from ..core.defaults import starter_input
            from ..core.models import Income, FixedExpense
            from ..utils.money import Money

        # Start from starter input and overwrite incomes/fixed with user values
        plan_input = starter_input()

        # collect incomes
        incomes = []
        for _, src, period, amt in self.income_entries:
            name = src.get().strip()
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0.0
            if name and amount > 0:
                incomes.append(Income(name=name, amount=Money(str(amount))))
        if incomes:
            plan_input.incomes = incomes

        # collect fixed expenses
        fixed = []
        for label, amt in self.fixed_entries:
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0.0
            fixed.append(FixedExpense(name=label, amount=Money(str(amount)), essential=True))
        if fixed:
            plan_input.fixed = fixed

        # simple validation: percent total must be 100
        self.update_percent_total()
        if self.error_label.cget("text") != "":
            return

        # Pass the PlanningInput object to the main window to generate plan
        if hasattr(self.controller, 'generate_plan'):
            self.controller.generate_plan(plan_input)

    def reset(self):
        # Clear all inputs
        for _, src, period, amt in self.income_entries:
            src.delete(0, "end")
            period.set(LANGUAGES[self.lang]['period_month'])
            amt.delete(0, "end")
        for _, amt in self.fixed_entries:
            amt.delete(0, "end")
        for _, spin in self.pref_entries:
            spin.delete(0, "end")
            spin.insert(0, "0")
        for _, _, min_spin, max_spin in self.constraint_entries:
            min_spin.delete(0, "end")
            min_spin.insert(0, "0")
            max_spin.delete(0, "end")
            max_spin.insert(0, "100")
        self.update_percent_total()
        self.error_label.config(text="")