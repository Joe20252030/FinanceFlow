import sys
import os

# 保证 src 目录在 sys.path
src_dir = os.path.dirname(os.path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from budget_app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

