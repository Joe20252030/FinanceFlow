# src/budget_app/ui/export_dialog.py
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Try to import reportlab for PDF. If missing, we still allow CSV and
# we show a friendly prompt when the user chooses PDF.
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    _HAS_REPORTLAB = True
except Exception:
    _HAS_REPORTLAB = False


def _export_plan_to_csv(plan: dict, path: str) -> None:
    """Write a simple CSV: metadata at top, then a Category/Amount table."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Period", plan.get("period", "")])
        w.writerow(["Total income", plan.get("total_income", "")])
        w.writerow(["Fixed costs", plan.get("total_fixed", "")])
        w.writerow(["Variable pool", plan.get("variable_pool", "")])
        w.writerow([])  # blank line
        w.writerow(["Category", "Amount"])
        for cat, amt in (plan.get("categories") or {}).items():
            w.writerow([cat, amt])
        w.writerow(["Leftover", plan.get("leftover", "")])


def _export_plan_to_pdf(plan: dict, path: str) -> None:
    """Create a simple, clean PDF using reportlab (if available)."""
    if not _HAS_REPORTLAB:
        raise RuntimeError(
            "PDF export requires the 'reportlab' module.\n\n"
            "Install it with:\n    pip install reportlab"
        )

    doc = SimpleDocTemplate(path, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("FinanceFlow Budget Plan", styles['Title']))
    story.append(Paragraph(f"Period: {plan.get('period','').title()}", styles['Normal']))
    story.append(Paragraph(f"Total income: ${float(plan.get('total_income',0)):.2f}", styles['Normal']))
    story.append(Paragraph(f"Fixed costs: ${float(plan.get('total_fixed',0)):.2f}", styles['Normal']))
    story.append(Paragraph(f"Variable pool: ${float(plan.get('variable_pool',0)):.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    rows = [["Category", "Amount"]]
    for cat, amt in (plan.get("categories") or {}).items():
        rows.append([cat, f"${float(amt):.2f}"])
    rows.append(["Leftover", f"${float(plan.get('leftover',0)):.2f}"])

    table = Table(rows, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eaeaea")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
    ]))
    story.append(table)
    doc.build(story)


class ExportDialog(tk.Toplevel):
    """
    A modal dialog that lets the user choose CSV or PDF and save the current plan.
    Usage:
        dlg = ExportDialog(parent_window, plan_dict)
        # optional: after it closes, check dlg.result for the saved path (or None)
    """
    def __init__(self, parent, plan: dict):
        super().__init__(parent)
        self.title("Export Plan")
        self.resizable(False, False)
        self.plan = plan or {}
        self.result = None  # filled with the saved file path on success

        # Center relative to parent
        self.transient(parent)
        self.grab_set()  # modal

        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Choose format:").grid(row=0, column=0, columnspan=2, sticky="w")

        self.var_fmt = tk.StringVar(value="csv")
        ttk.Radiobutton(frm, text="CSV (Excel/Sheets)", variable=self.var_fmt, value="csv").grid(row=1, column=0, sticky="w")
        pdf_label = "PDF (print-ready)"
        if not _HAS_REPORTLAB:
            pdf_label += " — requires 'reportlab'"
        ttk.Radiobutton(frm, text=pdf_label, variable=self.var_fmt, value="pdf").grid(row=2, column=0, sticky="w")

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=(12,0), sticky="e")

        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=(6,0))
        ttk.Button(btns, text="Save…", command=self._on_save).pack(side="right")

        # Keyboard shortcuts
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._on_save())

        # Basic sizing
        self.update_idletasks()
        self.minsize(self.winfo_width(), self.winfo_height())
        try:
            # place near parent
            px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{px}+{py}")
        except Exception:
            pass

    def _on_save(self):
        fmt = self.var_fmt.get()
        if fmt == "csv":
            path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save as CSV"
            )
            if not path:
                return
            try:
                _export_plan_to_csv(self.plan, path)
                self.result = path
                messagebox.showinfo("Export", "Exported to CSV successfully.")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Export failed", str(e))
        else:
            if not _HAS_REPORTLAB:
                messagebox.showwarning(
                    "PDF export unavailable",
                    "PDF export needs the 'reportlab' module.\n\nInstall it with:\n  pip install reportlab"
                )
                return
            path = filedialog.asksaveasfilename(
                parent=self,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save as PDF"
            )
            if not path:
                return
            try:
                _export_plan_to_pdf(self.plan, path)
                self.result = path
                messagebox.showinfo("Export", "Exported to PDF successfully.")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Export failed", str(e))


# Optional helper if you prefer a function call from MainWindow:
def open_export_dialog(parent, export_dict):
    """
    弹出文件保存对话框，将plan_data导出为CSV，并在末尾总结总支出。
    :param parent: 主窗口
    :param export_dict: {'plan_data': [...]}，每项包含category, amount, percent
    """
    plan_data = export_dict.get('plan_data', [])
    if not plan_data:
        messagebox.showerror("导出失败", "没有可导出的预算数据。", parent=parent)
        return
    # 选择保存路径
    file_path = filedialog.asksaveasfilename(
        parent=parent,
        title="导出预算为CSV",
        defaultextension=".csv",
        filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
    )
    if not file_path:
        return  # 用户取消
    try:
        total_amount = 0.0
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Amount", "Percent"])
            for item in plan_data:
                amount = item.get("amount", 0)
                try:
                    amount_float = float(amount)
                except Exception:
                    amount_float = 0.0
                total_amount += amount_float
                writer.writerow([
                    item.get("category", ""),
                    f"{amount_float:.2f}",
                    item.get("percent", "")
                ])
            # 总支出统计行
            writer.writerow(["Total", f"{total_amount:.2f}", ""])
        messagebox.showinfo("导出成功", f"预算已成功导出到：\n{file_path}", parent=parent)
    except Exception as e:
        messagebox.showerror("导出失败", f"导出CSV时出错：{e}", parent=parent)
