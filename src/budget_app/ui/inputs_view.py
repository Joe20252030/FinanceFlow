import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk, ImageFont
import cairosvg

class InputsView(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        style = tb.Style()
        style.configure("Custom.TFrame", background="#F0F0F0")

        # 滚动区（双向滚动条）
        canvas = tb.Canvas(self, bg="#F0F0F0", highlightthickness=0)
        vscroll = tb.Scrollbar(self, orient="vertical", command=canvas.yview)
        hscroll = tb.Scrollbar(self, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")
        scroll_frame = tb.Frame(canvas, style="Custom.TFrame")
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=scroll_frame, anchor="nw")

        # 错误提示区
        self.error_label = tb.Label(scroll_frame, text="", bootstyle=DANGER)
        self.error_label.pack(fill="x", pady=2)

        # 收入输入区
        income_frame = tb.LabelFrame(scroll_frame, text="收入输入", bootstyle=INFO)
        income_frame.pack(fill="x", pady=10)
        self.income_entries = []
        self.add_income_entry(income_frame)
        add_income_btn = tb.Button(income_frame, text="添加收入来源", command=lambda: self.add_income_entry(income_frame), bootstyle=SECONDARY)
        add_income_btn.pack(side="right", padx=10, pady=5)

        # 固定支出区
        fixed_frame = tb.LabelFrame(scroll_frame, text="固定支出", bootstyle=WARNING)
        fixed_frame.pack(fill="x", pady=10)
        self.fixed_entries = []
        for label in ["房租", "水电", "电话", "保险"]:
            self.add_fixed_entry(fixed_frame, label)

        # 预算偏好区
        prefs_frame = tb.LabelFrame(scroll_frame, text="预算偏好", bootstyle=SUCCESS)
        prefs_frame.pack(fill="x", pady=10)
        self.pref_entries = []
        for label in ["餐饮", "购物", "交通", "储蓄"]:
            self.add_pref_entry(prefs_frame, label)
        self.percent_total_label = tb.Label(prefs_frame, text="总分配: 0%", bootstyle=INFO)
        self.percent_total_label.pack(side="right", padx=10)

        # 约束区
        constraint_frame = tb.LabelFrame(scroll_frame, text="约束设置", bootstyle=DANGER)
        constraint_frame.pack(fill="x", pady=10)
        self.constraint_entries = []
        for label in ["餐饮", "购物", "交通", "储蓄"]:
            self.add_constraint_entry(constraint_frame, label)
        add_constraint_btn = tb.Button(constraint_frame, text="添加约束类别", command=lambda: self.add_constraint_entry(constraint_frame, "新类别"), bootstyle=SECONDARY)
        add_constraint_btn.pack(side="right", padx=10, pady=5)

        # 提交与重置
        btn_frame = tb.Frame(scroll_frame)
        btn_frame.pack(fill="x", pady=15)
        submit_btn = tb.Button(btn_frame, text="生成计划", bootstyle=PRIMARY, command=self.submit)
        submit_btn.pack(side="left", padx=10)
        reset_btn = tb.Button(btn_frame, text="重置", bootstyle=SECONDARY, command=self.reset)
        reset_btn.pack(side="right", padx=10)

        # 鼠标滚轮事件绑定（上下滚动，Shift+滚轮左右滚动）
        def _on_mousewheel(event):
            # macOS: event.delta is ±1, Windows/Linux: ±120
            delta = event.delta
            if abs(delta) < 10:
                delta = delta * 120  # 兼容 macOS
            if event.state & 0x0001:  # Shift 键按下
                canvas.xview_scroll(int(-1 * (delta / 120)), "units")
            else:
                canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def add_income_entry(self, parent):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=2)
        src_entry = tb.Entry(frame, width=12)
        src_entry.pack(side="left", padx=5)
        period_combo = tb.Combobox(frame, values=["月", "周"], width=5)
        period_combo.set("月")
        period_combo.pack(side="left", padx=5)
        amt_entry = tb.Entry(frame, width=10)
        amt_entry.pack(side="left", padx=5)
        del_btn = tb.Button(frame, text="删除", bootstyle=DANGER, command=lambda: self._del_income_entry(frame))
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
        self.percent_total_label.config(text=f"总分配: {total}%")
        if total != 100:
            self.error_label.config(text="预算分配总和必须为100%")
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
        del_btn = tb.Button(frame, text="删除", bootstyle=DANGER, command=lambda: self._del_constraint_entry(frame))
        del_btn.pack(side="left", padx=5)
        self.constraint_entries.append((frame, label, min_spin, max_spin))

    def _del_constraint_entry(self, frame):
        for entry in self.constraint_entries:
            if entry[0] == frame:
                entry[0].destroy()
                self.constraint_entries.remove(entry)
                break

    def submit(self):
        # 收集所有输入数据，校验并传递给 planner
        data = {
            "income": [],
            "fixed": {},
            "prefs": {},
            "constraints": {}
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
        for label, spin in self.pref_entries:
            try:
                percent = int(spin.get())
            except ValueError:
                percent = 0
            data["prefs"][label] = percent
        for _, label, min_spin, max_spin in self.constraint_entries:
            try:
                minv = int(min_spin.get())
                maxv = int(max_spin.get())
            except ValueError:
                minv, maxv = 0, 100
            data["constraints"][label] = {"min": minv, "max": maxv}
        # 校验
        self.update_percent_total()
        if self.error_label.cget("text") != "":
            return
        # TODO: 传递 data 给 planner
        print("提交数据:", data)

    def reset(self):
        # 清空所有输入
        for _, src, period, amt in self.income_entries:
            src.delete(0, "end")
            period.set("月")
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
