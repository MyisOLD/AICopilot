# chat_app/ui/components/styled_widgets.py

from PyQt6.QtWidgets import (QPushButton, QComboBox, QCheckBox, QTextEdit, 
                           QPlainTextEdit,QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class StyledButton(QPushButton):
    def __init__(self, text, variant="default"):
        super().__init__(text)
        self.variant = variant
        self.apply_style()

    def apply_style(self):
        base_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """

        variants = {
            "default": """
                background-color: #f3f4f6;
                color: #111827;
                border: 1px solid #e5e7eb;
            """,
            "primary": """
                background-color: #2563eb;
                color: white;
                border: none;
            """,
            "danger": """
                background-color: #dc2626;
                color: white;
                border: none;
            """
        }

        self.setStyleSheet(base_style + variants.get(self.variant, variants["default"]))

class AnimatedButton(QPushButton):
    def __init__(self, text, variant="default"):
        super().__init__(text)
        self.variant = variant
        self.apply_style()

        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

    def enterEvent(self, event):
        animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation.setDuration(200)
        animation.setStartValue(1.0)
        animation.setEndValue(0.8)
        animation.start()

    def leaveEvent(self, event):
        animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation.setDuration(200)
        animation.setStartValue(0.8)
        animation.setEndValue(1.0)
        animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            geo = self.geometry()
            self._animation.setStartValue(geo)
            self._animation.setEndValue(geo.adjusted(2, 2, -2, -2))
            self._animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            geo = self.geometry()
            self._animation.setStartValue(geo)
            self._animation.setEndValue(geo.adjusted(-2, -2, 2, 2))
            self._animation.start()
        super().mouseReleaseEvent(event)

class StyledComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #2563eb;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/chevron-down.png);
                width: 12px;
                height: 12px;
            }
        """)

class StyledCheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border-color: #2563eb;
            }
        """)

class StyledTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
                color: #111827;
                font-size: 14px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #2563eb;
                outline: none;
            }
        """)

class StyledPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None, window=None):
        super().__init__(parent)
        self.window = window
        self.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
                color: #111827;
                font-size: 14px;
                line-height: 1.5;
            }
            QPlainTextEdit:focus {
                border-color: #2563eb;
                outline: none;
            }
        """)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            self.window.send_message()
        else:
            super().keyPressEvent(event)