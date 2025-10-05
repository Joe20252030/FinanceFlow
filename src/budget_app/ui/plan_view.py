import ttkbootstrap as tb
from tkinter import ttk
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlanView(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.language = getattr(main_window, 'language', 'en')
        self.chart_canvas = None
        self._init_scrollable_ui()

    def _init_scrollable_ui(self):
        # 主滚动容器 Canvas+Frame
        self.canvas = tk.Canvas(self, borderwidth=0, background="#fff")
        self.scroll_frame = ttk.Frame(self.canvas)
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.window_id = self.canvas.create_window((0,0), window=self.scroll_frame, anchor="n")
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # 只在鼠标悬停时绑定滚轮事件
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self._init_ui(self.scroll_frame)

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

    def _on_shift_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120
        self.canvas.xview_scroll(int(-1*(delta/120)), "units")

    def _init_ui(self, parent):
        self.title_label = tb.Label(parent, text=self._get_text('plan_title'), font=self.main_window.questrial_bold, foreground="#333")
        self.title_label.pack(padx=8, pady=(0, 8), anchor="center")
        # 表格区
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="x", padx=8, pady=4)
        self.table = ttk.Treeview(table_frame, columns=("category", "amount", "percent"), show="headings", height=6)
        self.table.heading("category", text=self._get_text('category'))
        self.table.heading("amount", text=self._get_text('amount'))
        self.table.heading("percent", text=self._get_text('percent'))
        self.table.column("category", width=120)
        self.table.column("amount", width=100)
        self.table.column("percent", width=80)
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<MouseWheel>", self._on_table_mousewheel)
        self.table.bind("<Shift-MouseWheel>", self._on_table_shift_mousewheel)
        # 提示区
        self.notes_label = tb.Label(parent, text="", font=self.main_window.questrial_label, foreground="#C33")
        self.notes_label.pack(padx=8, pady=(4, 8), anchor="center")
        # 图表区（matplotlib嵌入）
        self.chart_frame = ttk.Frame(parent)
        self.chart_frame.pack(padx=8, pady=(4, 8), anchor="center", fill="both", expand=True)

    def _on_table_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120
        self.canvas.yview_scroll(int(-1*(delta/120)), "units")
        return "break"

    def _on_table_shift_mousewheel(self, event):
        delta = event.delta
        if abs(delta) < 10:
            delta *= 120
        self.canvas.xview_scroll(int(-1*(delta/120)), "units")
        return "break"

    def set_language(self, lang):
        self.language = lang
        self.title_label.config(text=self._get_text('plan_title'))
        self.table.heading("category", text=self._get_text('category'))
        self.table.heading("amount", text=self._get_text('amount'))
        self.table.heading("percent", text=self._get_text('percent'))
        self.chart_placeholder.config(text="(Chart Area)" if lang == "en" else "（图表区）")

    def update_plan(self, plan_data, notes=None):
        """
        重新实现表格逻辑：
        - 自动清空表格
        - 统计总金额
        - 按 category/amount 展示所有项
        - 自动计算百分比
        - 支持金额为0或缺失时的健壮处理
        """
        for row in self.table.get_children():
            self.table.delete(row)
        # 统计总金额（只统计正数）
        total_amount = sum(float(item.get("amount", 0)) for item in plan_data if float(item.get("amount", 0)) > 0)
        # 按顺序插入所有项
        for item in plan_data:
            category = item.get("category", "")
            try:
                amt = float(item.get("amount", 0))
            except Exception:
                amt = 0
            percent = round(amt / total_amount * 100, 2) if total_amount > 0 else 0
            self.table.insert("", "end", values=(category, amt, percent))
        self.notes_label.config(text=notes or "")
        # --- 英文柱状图总结 ---
        self._draw_bar_chart(plan_data)

    def _draw_bar_chart(self, plan_data):
        # 清除旧图表
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        # 收集数据
        categories = [item.get("category", "") for item in plan_data if float(item.get("amount", 0)) > 0]
        amounts = [float(item.get("amount", 0)) for item in plan_data if float(item.get("amount", 0)) > 0]
        if not categories or not amounts:
            lbl = tb.Label(self.chart_frame, text="(No data for chart)", font=self.main_window.questrial_label, foreground="#888")
            lbl.pack()
            return
        fig = Figure(figsize=(5, 2.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(categories, amounts, color="#4A90E2")
        ax.set_title("Budget Allocation Summary", fontsize=12)
        ax.set_xlabel("Category", fontsize=10)
        ax.set_ylabel("Amount", fontsize=10)
        ax.tick_params(axis='x', labelrotation=30)
        fig.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _get_text(self, key):
        texts = {
            'en': {
                'plan_title': 'Budget Allocation',
                'category': 'Category',
                'amount': 'Amount',
                'percent': 'Percent',
            },
            'zh': {
                'plan_title': '预算分配',
                'category': '类别',
                'amount': '金额',
                'percent': '百分比',
            }
        }
        return texts.get(self.language, texts['en']).get(key, key)
