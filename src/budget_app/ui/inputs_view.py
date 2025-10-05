import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk, ImageFont
import cairosvg

LANGUAGES = {
    'en': {
        'income_input': 'Income Input',
        'add_income': 'Add Income Source',
        'fixed_costs': 'Fixed Costs',
        'budget_prefs': 'Budget Preferences',
        'submit': 'Generate Plan',
        'reset': 'Reset',
        'delete': 'Delete',
        'error_percent': 'Total allocation must be 100%',
        'period_month': 'Month',
        'period_week': 'Week',
        'categories': ['Dining', 'Shopping', 'Transport', 'Savings'],
        'fixed_labels': ['Rent', 'Utilities', 'Phone', 'Insurance'],
    },
    'zh': {
        'income_input': '收入输入',
        'add_income': '添加收入来源',
        'fixed_costs': '固定支出',
        'budget_prefs': '预算偏好',
        'submit': '生成计划',
        'reset': '重置',
        'delete': '删除',
        'error_percent': '预算分配总和必须为100%',
        'period_month': '月',
        'period_week': '周',
        'categories': ['餐饮', '购物', '交通', '储蓄'],
        'fixed_labels': ['房租', '水电', '电话', '保险'],
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

        # 滚动区（双向滚动条）
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
        # 只在鼠标悬停时绑定滚轮事件
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # 错误提示区
        self.error_label = tb.Label(self.scroll_frame, text="", bootstyle=DANGER)
        self.error_label.pack(pady=2, anchor="center")
        # 收入输入区
        self.income_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['income_input'], bootstyle=INFO)
        self.income_frame.pack(pady=10, anchor="center")
        self.income_entries = []
        self.add_income_entry(self.income_frame)
        self.add_income_btn = tb.Button(self.income_frame, text=LANGUAGES[self.lang]['add_income'], command=lambda: self.add_income_entry(self.income_frame), bootstyle=SECONDARY)
        self.add_income_btn.pack(side="right", padx=10, pady=5)

        # 固定支出区
        self.fixed_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['fixed_costs'], bootstyle=WARNING)
        self.fixed_frame.pack(pady=10, anchor="center")
        self.fixed_entries = []
        for label in LANGUAGES[self.lang]['fixed_labels']:
            self.add_fixed_entry(self.fixed_frame, label)

        # 预算偏好区
        self.prefs_frame = tb.LabelFrame(self.scroll_frame, text=LANGUAGES[self.lang]['budget_prefs'], bootstyle=SUCCESS)
        self.prefs_frame.pack(pady=10, anchor="center")
        self.pref_entries = []
        for label in LANGUAGES[self.lang]['categories']:
            self.add_pref_entry(self.prefs_frame, label)
        self.add_pref_btn = tb.Button(self.prefs_frame, text="+" + ("添加预算类别" if self.lang == "zh" else "Add Category"), bootstyle=SECONDARY, command=lambda: self.add_pref_entry(self.prefs_frame))
        self.add_pref_btn.pack(side="right", padx=10, pady=5)

        # 提交与重置（已移除底部按钮）
        # btn_frame = tb.Frame(self.scroll_frame)
        # btn_frame.pack(pady=15, anchor="center")
        # self.submit_btn = tb.Button(btn_frame, text=LANGUAGES[self.lang]['submit'], bootstyle=PRIMARY, command=self.submit)
        # self.submit_btn.pack(side="left", padx=10)
        # self.reset_btn = tb.Button(btn_frame, text=LANGUAGES[self.lang]['reset'], bootstyle=SECONDARY, command=self.reset)
        # self.reset_btn.pack(side="right", padx=10)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # 居中 scroll_frame
        canvas_width = event.width
        frame_width = self.scroll_frame.winfo_reqwidth()
        x = max((canvas_width - frame_width) // 2, 0)
        self.canvas.coords(self.window_id, x, 0)

    def _on_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120  # macOS 兼容
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
        # 更新所有区块标题和按钮文本
        self.income_frame.config(text=LANGUAGES[lang]['income_input'])
        self.add_income_btn.config(text=LANGUAGES[lang]['add_income'])
        self.fixed_frame.config(text=LANGUAGES[lang]['fixed_costs'])
        self.prefs_frame.config(text=LANGUAGES[lang]['budget_prefs'])
        # self.submit_btn.config(text=LANGUAGES[lang]['submit'])
        # self.reset_btn.config(text=LANGUAGES[lang]['reset'])
        self.error_label.config(text="")
        # 更新各项label
        for i, (label, amt_entry) in enumerate(self.fixed_entries):
            # fixed_entries 存储的是 (label, amt_entry)，label 是字符串，amt_entry 是 Entry
            # 需要找到对应的 Label 控件
            frame = amt_entry.master
            lbl = frame.winfo_children()[0]
            lbl.config(text=LANGUAGES[lang]['fixed_labels'][i])
        for i, (frame, src_entry, period_combo, amt_entry) in enumerate(self.income_entries):
            period_combo.config(values=[LANGUAGES[lang]['period_month'], LANGUAGES[lang]['period_week']])
            period_combo.set(LANGUAGES[lang]['period_month'])
        for i, (frame, cat_entry, percent_entry) in enumerate(self.pref_entries):
            cat_entry.delete(0, 'end')
            if i < len(LANGUAGES[lang]['categories']):
                cat_entry.insert(0, LANGUAGES[lang]['categories'][i])

        self.add_pref_btn.config(text="+" + ("添加预算类别" if lang == "zh" else "Add Category"))

    def get_total_income(self):
        total = 0.0
        for frame, src_entry, period_combo, amt_entry in self.income_entries:
            try:
                val = float(amt_entry.get())
            except ValueError:
                continue
            period = period_combo.get()
            if period == LANGUAGES[self.lang]['period_month']:
                total += val
            elif period == LANGUAGES[self.lang]['period_week']:
                total += val * 4
            else:
                total += val  # fallback, treat as monthly
        return total

    def add_income_entry(self, parent):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        src_entry = tb.Entry(frame, width=14)
        src_entry.pack(side="left", padx=4)
        period_combo = ttk.Combobox(frame, width=7, state="readonly")
        period_combo.pack(side="left", padx=4)
        period_combo.config(values=[LANGUAGES[self.lang]['period_month'], LANGUAGES[self.lang]['period_week']])
        period_combo.set(LANGUAGES[self.lang]['period_month'])
        amt_entry = tb.Entry(frame, width=10)
        amt_entry.pack(side="left", padx=4)
        # 删除amt_entry.bind('<KeyRelease>', self._on_income_change)
        # --- Hover notices ---
        def show_src_hint(event):
            hint = "Enter the name of your income source." if self.lang == "en" else "输入收入来源名称。"
            self.controller.button_hint_label.config(text=hint)
        def show_period_hint(event):
            hint = "Select if this income is monthly or weekly." if self.lang == "en" else "选择收入周期（月/周）。"
            self.controller.button_hint_label.config(text=hint)
        def show_amt_hint(event):
            hint = "Enter the amount for this income source." if self.lang == "en" else "输入该收入的金额。"
            self.controller.button_hint_label.config(text=hint)
        def clear_hint(event):
            self.controller.button_hint_label.config(text="")
        src_entry.bind("<Enter>", show_src_hint)
        src_entry.bind("<Leave>", clear_hint)
        period_combo.bind("<Enter>", show_period_hint)
        period_combo.bind("<Leave>", clear_hint)
        amt_entry.bind("<Enter>", show_amt_hint)
        amt_entry.bind("<Leave>", clear_hint)
        # --- End hover notices ---
        self.income_entries.append((frame, src_entry, period_combo, amt_entry))
        return frame

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

    def add_pref_entry(self, parent, label=None):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        cat_entry = tb.Entry(frame, width=14)
        cat_entry.pack(side="left", padx=4)
        if label:
            cat_entry.insert(0, label)
        percent_entry = tb.Entry(frame, width=6)
        percent_entry.pack(side="left", padx=4)
        del_btn = tb.Button(frame, text=LANGUAGES[self.lang]['delete'], bootstyle=DANGER, command=lambda: self._del_pref_entry(frame))
        del_btn.pack(side="left", padx=4)
        def show_cat_hint(event):
            hint = "Enter budget category name." if self.lang == "en" else "输入预算类别名称。"
            self.controller.button_hint_label.config(text=hint)
        def show_percent_hint(event):
            hint = "Enter budget percentage for this category." if self.lang == "en" else "输入该类别的预算百分比。"
            self.controller.button_hint_label.config(text=hint)
        def clear_hint(event):
            self.controller.button_hint_label.config(text="")
        cat_entry.bind("<Enter>", show_cat_hint)
        cat_entry.bind("<Leave>", clear_hint)
        percent_entry.bind("<Enter>", show_percent_hint)
        percent_entry.bind("<Leave>", clear_hint)
        # ---
        self.pref_entries.append((frame, cat_entry, percent_entry))
        return frame

    def _del_pref_entry(self, frame):
        idx = None
        for i, entry in enumerate(self.pref_entries):
            if entry[0] == frame:
                idx = i
                break
        if idx is not None:
            entry = self.pref_entries.pop(idx)
            entry[0].destroy()

    def submit(self):
        # 收集所有输入数据，校验并传递给 planner
        data = {
            "income": [],
            "fixed": {},
            "prefs": {},
        }
        for _, src, period, amt in self.income_entries:
            name = src.get().strip()
            per = period.get()
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0
            if name and amount > 0:
                data["income"].append({"name": name, "period": per, "amount": amount})
        for label, amt in self.fixed_entries:
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0
            data["fixed"][label] = amount
        for i, (frame, cat_entry, percent_entry) in enumerate(self.pref_entries):
            label = cat_entry.get().strip()
            try:
                percent = int(percent_entry.get())
            except ValueError:
                percent = 0
            if label:
                data["prefs"][label] = percent
        # 校验
        if self.error_label.cget("text") != "":
            return
        # TODO: 传递 data 给 planner
        print("提交数据:", data)

    def reset(self):
        # 清空所有输入
        for _, src, period, amt in self.income_entries:
            src.delete(0, "end")
            period.set(LANGUAGES[self.lang]['period_month'])
            amt.delete(0, "end")
        for _, amt in self.fixed_entries:
            amt.delete(0, "end")
        self.reset_pref_entries()
        self.error_label.config(text="")

    def reset_pref_entries(self):
        for i, (frame, cat_entry, percent_entry) in enumerate(self.pref_entries):
            cat_entry.delete(0, 'end')
            percent_entry.delete(0, 'end')
            percent_entry.insert(0, "0")

    def get_all_input_data(self):
        # 收集所有输入数据，返回标准格式
        data = {
            "income_input": [],
            "fixed_costs": [],
            "budget_preference": []
        }
        for _, src, period, amt in self.income_entries:
            name = src.get().strip()
            per = period.get()
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0
            if name and amount > 0:
                data["income_input"].append({"name": name, "period": per, "amount": amount})
        for label, amt in self.fixed_entries:
            try:
                amount = float(amt.get())
            except ValueError:
                amount = 0
            data["fixed_costs"].append({"name": label, "amount": amount})
        for _, cat_entry, percent_entry in self.pref_entries:
            label = cat_entry.get().strip()
            try:
                percent = int(percent_entry.get())
            except ValueError:
                percent = 0
            if label:
                data["budget_preference"].append({"category": label, "percent": percent})
        return data
