from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from UI.main_window import MultiChatWindow
import sys


def main():
    app = QApplication(sys.argv)
    font = QFont("阿里巴巴普惠体 R", 10)
    app.setFont(font)

    window = MultiChatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()