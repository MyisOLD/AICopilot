import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from chat_window import MultiChatWindow  # 新文件名

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序级别的字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MultiChatWindow()
    window.show()
    sys.exit(app.exec())