# chat_app/ui/components/styled_widgets.py
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QPushButton, QComboBox, QCheckBox, QTextEdit,
                             QPlainTextEdit, QGraphicsOpacityEffect, QMenu)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal


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
    quote_requested = pyqtSignal(str)  # 新增信号用于传递引用文本
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
        self.setup_context_menu()

    def setup_context_menu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu(self)

        # 只有在有选中文本时才添加引用动作
        cursor = self.textCursor()
        if cursor.hasSelection():
            quote_action = QAction("引用选中文本", self)
            quote_action.setShortcut("Ctrl+Q")
            quote_action.triggered.connect(self.handle_quote_request)
            menu.addAction(quote_action)
            menu.addSeparator()

        # 使用标准上下文菜单的动作
        standard_menu = self.createStandardContextMenu()
        for action in standard_menu.actions():
            new_action = QAction(action.text(), self)
            new_action.setShortcut(action.shortcut())
            new_action.setEnabled(action.isEnabled())
            new_action.triggered.connect(action.trigger)
            menu.addAction(new_action)

        # 在调用前释放标准菜单
        standard_menu.deleteLater()

        menu.exec(self.mapToGlobal(pos))

    def handle_quote_request(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            # 发射信号，传递选中的文本
            self.quote_requested.emit(selected_text)

    def keyPressEvent(self, event):
        # 添加快捷键支持
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.handle_quote_request()
        else:
            super().keyPressEvent(event)


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

    def insert_quote(self, text):
        # 在当前光标位置插入引用文本
        quoted_text = "\n".join(f"> {line}" for line in text.split("\n"))
        current_text = self.toPlainText()

        if current_text:
            # 如果输入框已有内容，添加换行符
            quoted_text = "\n" + quoted_text

        # 在末尾添加一个换行，方便用户继续输入
        quoted_text += "\n"

        cursor = self.textCursor()
        cursor.insertText(quoted_text)
        self.setFocus()  # 将焦点设置到输入框

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            self.window.send_message()
        else:
            super().keyPressEvent(event)