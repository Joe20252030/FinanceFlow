import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageTk, ImageFont
import cairosvg
# 推荐用 `python -m src.budget_app.ui.main_window` 运行
try:
    from src.budget_app.ui.inputs_view import InputsView
except ImportError:
    from inputs_view import InputsView

class MainWindow(tb.Window):
    def __init__(self):
        super().__init__(themename="minty")  # 更现代圆角主题
        self.title("FinanceFlow Budget Planner")
        self.geometry("900x600")
        self.resizable(True, True)
        self.configure(bg="#f7f8fa")  # 苹果风浅灰背景

        # 字体路径
        font_dir = os.path.join(os.path.dirname(__file__), '../../assets/fonts')
        self.questrial_regular = tkfont.Font(family="Questrial", size=22, weight="normal")
        self.questrial_label = tkfont.Font(family="Questrial", size=13, weight="normal")
        self.questrial_button = tkfont.Font(family="Questrial", size=13, weight="normal")
        # 主标题（沉稳深蓝色，加粗）
        self.questrial_bold = tkfont.Font(family="Questrial", size=24, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        # 顶部标题栏
        title_label = tb.Label(self, text="FinanceFlow Budget Planner", font=self.questrial_bold, bootstyle=PRIMARY, foreground="#223A5E")
        title_label.pack(pady=(30, 10))

        # 主内容区域背景（圆角白色）
        content_canvas = tb.Canvas(self, bg="#f7f8fa", highlightthickness=0)
        content_canvas.pack(fill="both", expand=True, padx=40, pady=(0, 0))
        # 绘制圆角白色矩形（可在窗口缩放时重绘，暂保留原逻辑）
        def redraw_canvas(event=None):
            content_canvas.delete("all")
            w = content_canvas.winfo_width()
            h = content_canvas.winfo_height()
            r = 32
            x0, y0, x1, y1 = 0, 0, w, h
            content_canvas.create_rectangle(x0+r, y0, x1-r, y1, fill="white", outline="white")
            content_canvas.create_rectangle(x0, y0+r, x1, y1-r, fill="white", outline="white")
            content_canvas.create_oval(x0, y0, x0+2*r, y0+2*r, fill="white", outline="white")
            content_canvas.create_oval(x1-2*r, y0, x1, y0+2*r, fill="white", outline="white")
            content_canvas.create_oval(x0, y1-2*r, x0+2*r, y1, fill="white", outline="white")
            content_canvas.create_oval(x1-2*r, y1-2*r, x1, y1, fill="white", outline="white")
        content_canvas.bind("<Configure>", redraw_canvas)
        redraw_canvas()

        # 主内容区域（自适应布局）
        paned = ttk.PanedWindow(content_canvas, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=24, pady=24)

        # 左侧输入区域
        left_frame = ttk.Frame(paned)
        left_frame.configure(style="TFrame")
        paned.add(left_frame, weight=1)
        inputs_title = tb.Label(left_frame, text="Input Form Area", font=self.questrial_bold, foreground="#333")
        inputs_title.pack(padx=8, pady=(0, 8))
        self.inputs_view = InputsView(left_frame, self)
        self.inputs_view.pack(fill="both", expand=True, padx=8, pady=4)

        # 右侧计划展示区域
        right_frame = ttk.Frame(paned)
        right_frame.configure(style="TFrame")
        paned.add(right_frame, weight=2)
        plan_title = tb.Label(right_frame, text="Budget Allocation Display Area", font=self.questrial_bold, foreground="#333")
        plan_title.pack(padx=8, pady=(0, 8))
        plan_placeholder = tb.Label(right_frame, text="📊 (plan_view)", font=self.questrial_label, bootstyle=SUCCESS)
        plan_placeholder.pack(padx=8, pady=4)

        # 底部按钮区域（用SVG图片按钮，无文字）
        button_canvas = tb.Canvas(self, width=320, height=100, bg="#f7f8fa", highlightthickness=0)
        button_canvas.pack(pady=(10, 24))
        self._draw_image_buttons(button_canvas)

    def _draw_image_buttons(self, canvas):
        btns = [
            {"img": "add_circle_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.generate_plan, "x": 35},
            {"img": "autorenew_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.reset_all, "x": 135},
            {"img": "output_26dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg", "callback": self.open_export_dialog, "x": 235}
        ]
        self.tk_btn_imgs = []
        btn_width, btn_height = 48, 48  # 图标缩小为48x48
        y = 16  # 图标略微下移，原为10
        for btn in btns:
            img_path = os.path.join(os.path.dirname(__file__), '../../../assets/images/' + btn["img"])
            img_path = os.path.abspath(img_path)
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Button image not found: {img_path}")
            # SVG to PNG conversion
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

    def generate_plan(self):
        print("Generating budget plan...")

    def open_export_dialog(self):
        print("Opening export dialog...")

    def reset_all(self):
        print("Resetting all inputs and results...")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()