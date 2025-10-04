import os
import sys
import ttkbootstrap as tb
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageTk
import cairosvg

# Robust import logic for both direct and module execution
if __package__ is None or __package__ == "":
    # Running as a script: insert src directory at sys.path[0] and use absolute imports
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from budget_app.ui.export_dialog import open_export_dialog
        from budget_app.ui.inputs_view import InputsView
        from budget_app.ui.plan_view import PlanView
    except ModuleNotFoundError as e:
        raise ImportError("Could not import budget_app modules. Please run with 'python -m budget_app.ui.main_window' from the src directory.") from e
else:
    # Running as a module: use relative imports
    from .export_dialog import open_export_dialog
    from .inputs_view import InputsView
    from .plan_view import PlanView

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

class MainWindow(tb.Window):
    # === UI与后端数据交互接口（统一入口） ===
    def generate_plan(self, data=None):
        """
        接收 InputsView 的预算输入数据，调用后端 planner 生成预算方案，并更新 PlanView。
        :param data: dict, 预算输入数据（由 InputsView.submit 传入）
        """
        # TODO: 调用 planner 计算预算方案
        # 例如: plan_data, notes = self.planner.generate(data)
        # self.plan_view.update_plan(plan_data, notes)
        print("[接口] 生成预算方案: ", data)

    def export_plan(self, export_data=None):
        """
        接收导出请求，调用后端导出逻辑（如 export.py），完成文件保存。
        :param export_data: dict, 导出相关数据（由 ExportDialog 传入）
        """
        # TODO: 调用后端导出逻辑
        print("[接口] 导出预算方案: ", export_data)

    def reset_all(self):
        """
        重置所有输入和结果，通知 InputsView 和 PlanView 清空内容。
        """
        # TODO: 调用 InputsView/PlanView 的重置方法
        print("[接口] 重置所有输入和结果")
        if hasattr(self, 'inputs_view'):
            self.inputs_view.reset()
        if hasattr(self, 'plan_view'):
            self.plan_view.update_plan([], notes="")

    def create_language_menu(self):
        import tkinter as tk
        menubar = tk.Menu(self)
        # Language menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        lang_menu.add_command(label="English", command=lambda: self.set_language('en'))
        lang_menu.add_command(label="简体中文", command=lambda: self.set_language('zh'))
        menubar.add_cascade(label="Language", menu=lang_menu)
        # Operations menu
        op_menu = tk.Menu(menubar, tearoff=0)
        op_labels = {
            'en': ["Generate Plan", "Reset All", "Export"],
            'zh': ["生成计划", "重置所有", "导出"]
        }
        op_cmds = [self.generate_plan, self.reset_all, self.open_export_dialog]
        for label, cmd in zip(op_labels[self.language], op_cmds):
            op_menu.add_command(label=label, command=cmd)
        menubar.add_cascade(label="操作" if self.language == "zh" else "Operations", menu=op_menu)
        self.config(menu=menubar)
        self._menubar = menubar  # Save reference for language switching

    def __init__(self):
        super().__init__(themename="minty")  # 更现代圆角主题
        self.language = CURRENT_LANG
        self.title("FinanceFlow Budget Planner")
        self.geometry("900x600")
        self.resizable(True, True)
        self.configure(bg="#f7f8fa")  # 苹果风浅灰背景
        self.create_language_menu()  # 确保菜单栏在窗口初始化时创建

        # 字体路径
        font_dir = os.path.join(os.path.dirname(__file__), '../../assets/fonts')
        self.questrial_regular = tkfont.Font(family="Questrial", size=22, weight="normal")
        self.questrial_label = tkfont.Font(family="Questrial", size=13, weight="normal")
        self.questrial_button = tkfont.Font(family="Questrial", size=13, weight="normal")
        # 主标题（沉稳深蓝色，加粗）
        self.questrial_bold = tkfont.Font(family="Questrial", size=24, weight="bold")

        self.create_widgets()


    def set_language(self, lang):
        global CURRENT_LANG
        CURRENT_LANG = lang
        self.language = lang
        # 更新主窗口标题栏和分区标题
        self.title("FinanceFlow Budget Planner" if lang == "en" else "财务流预算规划器")
        # 左侧输入区标题
        if hasattr(self, 'inputs_title'):
            self.inputs_title.config(text="Input Form Area" if lang == "en" else "输入表单区")
        # 右侧计划区标题
        if hasattr(self, 'plan_title'):
            self.plan_title.config(text="Budget Allocation Display Area" if lang == "en" else "预算分配展示区")
        # 右侧计划区 PlanView 语言切换
        if hasattr(self, 'plan_view'):
            self.plan_view.set_language(lang)
        # 清空按钮提示
        if hasattr(self, 'button_hint_label'):
            self.button_hint_label.config(text="")
        if hasattr(self, 'inputs_view'):
            self.inputs_view.set_language(lang)
        # 刷新菜单栏
        self.create_language_menu()
        # ...可扩展其他UI刷新...

    def create_widgets(self):
        # 顶部主标题栏
        self.title_label = tb.Label(self, text="FinanceFlow Budget Planner", font=self.questrial_bold, foreground="#223A5E")
        self.title_label.pack(pady=(30, 10))

        # 主内容区域背景（圆角白色）
        content_canvas = tb.Canvas(self, bg="white", highlightthickness=0)
        content_canvas.pack(fill="both", expand=True, padx=40, pady=(0, 0))
        # 内容Frame嵌入Canvas，强制背景白色
        content_frame = ttk.Frame(content_canvas, style="TFrame")
        content_frame.configure(style="TFrame")
        content_window_id = content_canvas.create_window(0, 0, window=content_frame, anchor="nw")

        def redraw_canvas(event=None):
            content_canvas.delete("bg")
            w = content_canvas.winfo_width()
            h = content_canvas.winfo_height()
            r = 32
            pad = 24
            # 圆角区域缩小到内容Frame内部
            x0, y0, x1, y1 = pad, pad, w-pad, h-pad
            content_canvas.create_rectangle(x0+r, y0, x1-r, y1, fill="white", outline="white", tags="bg")
            content_canvas.create_rectangle(x0, y0+r, x1, y1-r, fill="white", outline="white", tags="bg")
            content_canvas.create_oval(x0, y0, x0+2*r, y0+2*r, fill="white", outline="white", tags="bg")
            content_canvas.create_oval(x1-2*r, y0, x1, y0+2*r, fill="white", outline="white", tags="bg")
            content_canvas.create_oval(x0, y1-2*r, x0+2*r, y1, fill="white", outline="white", tags="bg")
            content_canvas.create_oval(x1-2*r, y1-2*r, x1, y1, fill="white", outline="white", tags="bg")
            # 居中内容Frame
            content_canvas.coords(content_window_id, pad, pad)
            content_frame.config(width=w-2*pad, height=h-2*pad)
            content_canvas.itemconfig(content_window_id, width=w-2*pad, height=h-2*pad)
        content_canvas.bind("<Configure>", redraw_canvas)
        redraw_canvas()

        # 主内容区域（自适应布局）
        paned = ttk.PanedWindow(content_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # 左侧输入区域
        left_frame = ttk.Frame(paned, style="TFrame")
        left_frame.configure(style="TFrame")
        paned.add(left_frame, weight=1)
        self.inputs_title = tb.Label(left_frame, text="Input Form Area", font=self.questrial_bold, foreground="#333", background="white")
        self.inputs_title.pack(padx=8, pady=(0, 8))
        self.inputs_view = InputsView(left_frame, self)
        self.inputs_view.pack(fill="both", expand=True, padx=8, pady=4)

        # 右侧计划展示区域
        right_frame = ttk.Frame(paned, style="TFrame")
        right_frame.configure(style="TFrame")
        paned.add(right_frame, weight=2)
        self.plan_title = tb.Label(right_frame, text="Budget Allocation Display Area", font=self.questrial_bold, foreground="#333", background="white")
        self.plan_title.pack(padx=8, pady=(0, 8))
        self.plan_view = PlanView(right_frame, self)
        self.plan_view.pack(fill="both", expand=True, padx=8, pady=4)

        # 底部按钮区域（用SVG图片按钮，无文字）
        button_canvas = tb.Canvas(self, width=320, height=100, bg="#f7f8fa", highlightthickness=0)
        button_canvas.pack(pady=(10, 24))
        self._draw_image_buttons(button_canvas)
        self.button_hint_label = tb.Label(self, text="", font=self.questrial_label, background="#f7f8fa")
        self.button_hint_label.pack(side="bottom", pady=(0, 8))

    def _draw_image_buttons(self, canvas):
        btns = [
            {"img": "add_circle_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.generate_plan, "x": 35, "hint_en": "Generate Plan", "hint_zh": "生成计划"},
            {"img": "autorenew_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.reset_all, "x": 135, "hint_en": "Reset All", "hint_zh": "重置所有"},
            {"img": "output_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.open_export_dialog, "x": 235, "hint_en": "Export", "hint_zh": "导出"}
        ]
        self.tk_btn_imgs = []
        btn_width, btn_height = 48, 48
        y = 16
        for btn in btns:
            img_path = os.path.join(os.path.dirname(__file__), '../../../assets/images/' + btn["img"])
            img_path = os.path.abspath(img_path)
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Button image not found: {img_path}")
            from io import BytesIO
            try:
                png_bytes = cairosvg.svg2png(url=img_path, output_width=btn_width, output_height=btn_height)
                img = Image.open(BytesIO(png_bytes)).convert("RGBA")
            except ImportError:
                raise ImportError("cairosvg is required for SVG support. Please install with 'pip install cairosvg'.")
            tk_img = ImageTk.PhotoImage(img)
            self.tk_btn_imgs.append(tk_img)
            btn_id = canvas.create_image(btn["x"], y, anchor="nw", image=tk_img)
            canvas.tag_bind(btn_id, '<Button-1>', lambda e, cb=btn["callback"]: cb())
            # 悬停提示
            def make_enter_leave(hint_en, hint_zh):
                def on_enter(event):
                    self.button_hint_label.config(text=hint_en if self.language == "en" else hint_zh)
                def on_leave(event):
                    self.button_hint_label.config(text="")
                return on_enter, on_leave
            on_enter, on_leave = make_enter_leave(btn["hint_en"], btn["hint_zh"])
            canvas.tag_bind(btn_id, '<Enter>', on_enter)
            canvas.tag_bind(btn_id, '<Leave>', on_leave)

    def open_export_dialog(self):
        # 获取当前计划数据
        plan_data = []
        if hasattr(self, 'plan_view') and hasattr(self.plan_view, 'table'):
            for row in self.plan_view.table.get_children():
                values = self.plan_view.table.item(row)['values']
                # values: [category, amount, percent]
                plan_data.append({
                    'category': values[0],
                    'amount': values[1],
                    'percent': values[2]
                })
        # 调用导出对话框，修正参数类型为 dict
        export_dict = {'plan_data': plan_data}
        open_export_dialog(self, export_dict)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()