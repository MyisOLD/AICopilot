# chat_app/ui/components/loading_indicator.py

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QTimer

class LoadingIndicator(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_dot = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._rotate)
        self.setVisible(False)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #2563eb;
                font-size: 18px;
            }
        """)

    def start(self):
        self.setVisible(True)
        self.timer.start(80)

    def stop(self):
        self.timer.stop()
        self.setVisible(False)

    def _rotate(self):
        self.setText(self.dots[self.current_dot])
        self.current_dot = (self.current_dot + 1) % len(self.dots)