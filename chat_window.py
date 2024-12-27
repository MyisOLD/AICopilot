import json
import os
import re
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QComboBox, QPushButton, QHBoxLayout,
                             QPlainTextEdit, QSplitter, QCheckBox, QScrollArea,
                             QGridLayout, QLabel, QFrame, QGraphicsOpacityEffect, QDialog, QLineEdit, QDialogButtonBox,
                             QMenu, QMessageBox)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSettings
from config import get_models, get_prompt_templates
from api_handler import send_request
import time
import markdown2


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


class AnimatedButton(QPushButton):
    def __init__(self, text, variant="default"):
        super().__init__(text)
        self.variant = variant
        self.apply_style()

        # 添加点击动画效果
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 添加悬停效果
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


class MyPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent=None, window=None):
        super().__init__(parent)
        self.window = window

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            self.window.send_message()
        else:
            super().keyPressEvent(event)


class AddTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加自定义模板")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Template name input
        layout.addWidget(QLabel("模板名称:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Template content input
        layout.addWidget(QLabel("提示词内容:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(200)
        layout.addWidget(self.prompt_input)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class StreamWorker(QThread):
    message_ready = pyqtSignal(str, int)
    reply_finished = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)

    def __init__(self, conversation_history, user_message, api_url, model_name, api_key, prompt, model_index):
        super().__init__()
        self.conversation_history = conversation_history
        self.user_message = user_message
        self.api_url = api_url
        self.model_name = model_name
        self.api_key = api_key
        self.prompt = prompt
        self.model_index = model_index
        self.reply = ''

    def run(self):
        try:
            response = send_request(self.conversation_history, self.user_message,
                                    self.api_url, self.model_name, self.api_key, self.prompt)
            if isinstance(response, str):
                self.message_ready.emit(response, self.model_index)
                return

            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        self.reply += content
                        self.message_ready.emit(content, self.model_index)
                        time.sleep(0.01)

            self.reply_finished.emit(self.reply, self.model_index)
            self.reply = ''
        except Exception as e:
            print(f"Streaming error: {str(e)}")
            self.error_occurred.emit(str(e))


class ChatPanel(QFrame):
    def __init__(self, model_index, models, parent=None):
        super().__init__(parent)
        self.model_index = model_index
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.loading_indicator = LoadingIndicator(self)
        self.apply_style()
        self.init_ui(models)
        self.current_response = ""  # Store current streaming response

    def init_ui(self, models):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header section
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(f"模型 {self.model_index + 1}")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #111827;
        """)

        self.model_combo = StyledComboBox()
        self.model_combo.addItems([model['name'] for model in models])

        self.enable_checkbox = StyledCheckBox("启用")
        self.enable_checkbox.setChecked(True)

        header_layout.addWidget(title)
        header_layout.addWidget(self.model_combo)
        header_layout.addWidget(self.enable_checkbox)
        layout.addWidget(header)

        # Chat display
        self.chat_display = StyledTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        self.chat_display.setHtml("""
            <html>
            <head>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
                    pre { background-color: #f3f4f6; padding: 12px; border-radius: 6px; }
                    code { font-family: Consolas, Monaco, "Courier New", monospace; }
                    blockquote { border-left: 4px solid #e5e7eb; margin: 0; padding-left: 16px; }
                    p { line-height: 1.6; }
                </style>
            </head>
            <body>
                <h1>欢迎使用 AI 助手</h1>
            </body>
            </html>
        """)
        layout.addWidget(self.chat_display)

    def apply_style(self):
        self.setStyleSheet("""
            ChatPanel {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                margin: 8px;
            }
            ChatPanel:hover {
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                           0 2px 4px -1px rgba(0, 0, 0, 0.06);
                transition: box-shadow 0.3s ease-in-out;
            }
        """)


class MultiChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.models = get_models()
        self.chat_panels = []
        self.conversation_histories = []
        self.workers = []
        self.current_template = ""  # Store selected template
        self.templates = self.load_templates()  # Load templates first

        self.setWindowTitle("智械中心")
        self.setGeometry(100, 100, 1600, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }
        """)
        self.init_ui()
        self.init_template_menu()  # Initialize template menu after UI
        self.init_theme()
        self.init_history()


    def init_history(self):
        # 检查是否存在历史记录文件，并提示用户是否恢复会话
        if os.path.exists('history.json'):
            reply = QMessageBox.question(self, '恢复会话', '是否恢复上次的会话？',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Yes:
                self.load_conversation_history()
            else:
                self.conversation_histories = [[] for _ in self.chat_panels]
        else:
            self.conversation_histories = [[] for _ in self.chat_panels]

        # 添加清除历史记录的菜单选项
        self.clear_history_action = QAction("清除历史记录", self)
        self.settings_menu.addAction(self.clear_history_action)
        self.clear_history_action.triggered.connect(self.clear_history)

        # 定时保存历史记录
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_conversation_history)
        self.save_timer.start(60000)  # 每分钟保存一次

    def save_conversation_history(self):
        """保存对话历史到文件"""
        with open('history.json', 'w') as f:
            json.dump(self.conversation_histories, f)

    def load_conversation_history(self):
        """从文件加载对话历史"""
        try:
            with open('history.json', 'r') as f:
                histories = json.load(f)
            for i, panel in enumerate(self.chat_panels):
                if i < len(histories):
                    self.conversation_histories[i] = histories[i]
                    # 加载对话到 chat_display
                    for message in histories[i]:
                        if message["role"] == "user":
                            panel.chat_display.append(
                                f'<div style="color: #2563eb; margin: 8px 0;"><b>您:</b> {message["content"]}</div>')
                        else:
                            panel.chat_display.append(
                                f'<div style="margin: 8px 0;"><b>AI助手:</b> {message["content"]}</div>')
        except Exception as e:
            print(f"加载历史记录失败: {e}")

    def clear_history(self):
        """清除所有历史记录"""
        reply = QMessageBox.question(self, '清除历史记录', '确定要清除所有历史记录吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.conversation_histories = [[] for _ in self.chat_panels]
            with open('history.json', 'w') as f:
                json.dump([], f)
            for panel in self.chat_panels:
                panel.chat_display.clear()
    def init_theme(self):
        # 定义白天和黑夜模式的样式表
        self.day_style = """
            QMainWindow { background-color: #f3f4f6; }
            QTextEdit { background-color: white; color: #111827; }
            QPushButton { background-color: #f3f4f6; color: #111827; }
            QComboBox { background-color: white; color: #111827; }
            QCheckBox { color: #111827; }
            QMenu { background-color: white; color: #111827; }
        """
        self.night_style = """
            QMainWindow { background-color: #1e1e1e; }
            QTextEdit { background-color: #2d2d2d; color: #ffffff; }
            QPushButton { background-color: #333333; color: #ffffff; }
            QComboBox { background-color: #333333; color: #ffffff; }
            QCheckBox { color: #ffffff; }
            QMenu { background-color: #333333; color: #ffffff; }
        """

        # 创建主题菜单
        self.menu_bar = self.menuBar()
        self.settings_menu = self.menu_bar.addMenu("设置")
        self.theme_menu = self.settings_menu.addMenu("主题")

        self.day_action = QAction("白天模式", self)
        self.night_action = QAction("黑夜模式", self)
        self.theme_menu.addAction(self.day_action)
        self.theme_menu.addAction(self.night_action)

        # 连接主题切换动作
        self.day_action.triggered.connect(lambda: self.set_style(self.day_style))
        self.night_action.triggered.connect(lambda: self.set_style(self.night_style))

        # 读取保存的主题设置
        settings = QSettings("MyCompany", "ChatApp")
        theme = settings.value("theme", "day")
        if theme == "night":
            self.setStyleSheet(self.night_style)
        else:
            self.setStyleSheet(self.day_style)

    def set_style(self, style):
        """设置样式并保存主题选择"""
        self.setStyleSheet(style)
        settings = QSettings("MyCompany", "ChatApp")
        settings.setValue("theme", "day" if style == self.day_style else "night")


    def init_ui(self):
        # Main container
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        self.setCentralWidget(main_widget)

        # Top toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # Styled buttons
        self.add_model_btn = StyledButton("➕ 添加模型")
        self.remove_model_btn = StyledButton("➖ 移除模型")
        self.template_button = StyledButton("📝 插入提示词")
        self.clear_button = StyledButton("🧹 清空记忆")

        toolbar_layout.addWidget(self.add_model_btn)
        toolbar_layout.addWidget(self.remove_model_btn)
        toolbar_layout.addWidget(self.template_button)
        toolbar_layout.addWidget(self.clear_button)
        toolbar_layout.addStretch()

        main_layout.addWidget(toolbar)

        # Chat panels container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        self.chat_container = QWidget()
        self.chat_layout = QGridLayout(self.chat_container)
        self.chat_layout.setSpacing(16)
        scroll.setWidget(self.chat_container)

        # Add initial chat panels
        self.add_chat_panel()
        self.add_chat_panel()

        main_layout.addWidget(scroll)

        # Input area
        input_area = QWidget()
        input_area.setMaximumHeight(self.height() * 0.2)
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)

        # 创建输入框容器
        input_container = QWidget()
        input_container.setMinimumHeight(80)
        input_container.setMaximumHeight(100)

        self.input_box = StyledPlainTextEdit(window=self)
        self.input_box.setPlaceholderText("在此输入您的问题...")

        # 将输入框添加到容器中
        input_container_layout = QVBoxLayout(input_container)
        input_container_layout.setContentsMargins(0, 0, 0, 0)
        input_container_layout.addWidget(self.input_box)

        # 修改发送按钮样式
        self.send_button = StyledButton("发送", "primary")
        self.send_button.setMinimumHeight(80)
        self.send_button.setMaximumHeight(100)

        # 使用比例布局：输入框占90%，按钮占10%
        input_layout.addWidget(input_container, 95)
        input_layout.addWidget(self.send_button, 5)

        main_layout.addWidget(input_area)

        # 设置主布局的拉伸因子
        main_layout.setStretch(0, 0)  # toolbar
        main_layout.setStretch(1, 85)  # chat area
        main_layout.setStretch(2, 15)  # input area

        self.template_button.clicked.connect(self.show_template_menu)
        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_memory)
        self.add_model_btn.clicked.connect(self.add_chat_panel)
        self.remove_model_btn.clicked.connect(self.remove_chat_panel)

    def add_chat_panel(self):
        panel_index = len(self.chat_panels)
        panel = ChatPanel(panel_index, self.models)

        # 计算网格位置
        row = panel_index // 2
        col = panel_index % 2

        self.chat_layout.addWidget(panel, row, col)
        self.chat_panels.append(panel)
        self.conversation_histories.append([])
        self.workers.append(None)

        # 更新移除按钮状态
        self.remove_model_btn.setEnabled(len(self.chat_panels) > 1)

    def remove_chat_panel(self):
        if len(self.chat_panels) > 1:
            panel = self.chat_panels.pop()
            self.conversation_histories.pop()
            self.workers.pop()
            panel.deleteLater()

            # 重新排列现有面板
            for i, panel in enumerate(self.chat_panels):
                row = i // 2
                col = i % 2
                self.chat_layout.addWidget(panel, row, col)

            # 更新移除按钮状态
            self.remove_model_btn.setEnabled(len(self.chat_panels) > 1)

    def load_templates(self):
        try:
            with open('prompts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"templates": []}

    def save_templates(self):
        with open('prompts.json', 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=4, ensure_ascii=False)

    def init_template_menu(self):
        # Create menu for template button
        self.template_menu = QMenu(self)
        self.template_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f3f4f6;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e5e7eb;
                margin: 4px 0;
            }
        """)

        # Add predefined templates
        for template in self.templates['templates']:
            action = self.template_menu.addAction(template['name'])
            action.triggered.connect(
                lambda checked, t=template: self.select_template(t)
            )

        # Add separator and custom template option
        self.template_menu.addSeparator()
        add_custom = self.template_menu.addAction("➕ 添加自定义模板")
        add_custom.triggered.connect(self.add_custom_template)

        # Connect menu to button using clicked signal
        self.template_button.clicked.connect(self.show_template_menu)

    def show_template_menu(self):
        # Calculate position to show menu below the button
        print("显示模板菜单")
        # self.init_template_menu()  # 重新初始化模板菜单
        pos = self.template_button.mapToGlobal(
            self.template_button.rect().bottomLeft()
        )
        self.template_menu.exec(pos)

    def select_template(self, template):
        self.current_template = template['prompt']
        # Optional: Show a small notification or update button text
        self.template_button.setText(f"📝 当前模板: {template['name']}")

    def add_custom_template(self):
        dialog = AddTemplateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_template = {
                "name": dialog.name_input.text(),
                "prompt": dialog.prompt_input.toPlainText()
            }
            self.templates['templates'].append(new_template)
            self.save_templates()

            # Refresh template menu
            self.template_menu.clear()
            self.init_template_menu()

    def send_message(self):
        user_message = self.input_box.toPlainText()
        if not user_message:
            return

        self.input_box.clear()

        for i, panel in enumerate(self.chat_panels):
            if not panel.enable_checkbox.isChecked():
                continue

            panel.loading_indicator.start()
            panel.current_response = ""

            # Add user message with HTML formatting
            panel.chat_display.append(
                f'<div style="color: #2563eb; margin: 8px 0;"><b>您:</b> {user_message}</div>'
            )
            panel.chat_display.append('<div style="margin: 8px 0;"><b>AI助手:</b> ')

            selected_model = self.models[panel.model_combo.currentIndex()]

            self.conversation_histories[i].append({"role": "user", "content": user_message})

            if self.workers[i] and self.workers[i].isRunning():
                self.workers[i].terminate()
                self.workers[i].wait()

            self.workers[i] = StreamWorker(
                self.conversation_histories[i].copy(),
                user_message,
                selected_model['url'],
                selected_model['model'],
                selected_model.get('key', ''),
                self.current_template,  # Use selected template
                i
            )

            self.workers[i].message_ready.connect(self.update_chat_display)
            self.workers[i].reply_finished.connect(self.render_final_response)
            self.workers[i].error_occurred.connect(self.handle_error)
            self.workers[i].start()

    def update_chat_display(self, reply, model_index):
        if model_index < len(self.chat_panels):
            panel = self.chat_panels[model_index]
            panel.current_response += reply

            display = panel.chat_display
            cursor = display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(reply)
            display.setTextCursor(cursor)
            display.ensureCursorVisible()

    def update_conversation_history(self, reply, model_index):
        if model_index < len(self.conversation_histories):
            self.conversation_histories[model_index].append({"role": "assistant", "content": reply})
            # 停止加载动画
            self.chat_panels[model_index].loading_indicator.stop()

    import re

    def render_final_response(self, reply, model_index):
        if model_index < len(self.conversation_histories):
            panel = self.chat_panels[model_index]

            # 检测是否存在 Markdown 语法
            has_markdown = re.search(
                r'(^#+\s|^[-*]\s|^\d+\.\s|\*\*.*\*\*|__.*__|\*.*\*|_.*_|`[^`]*`|```[\s\S]*?```|\[.*\]\(.*\)|!\[.*\]\(.*\)|^>|^---|^\*\*\*)',
                panel.current_response,
                re.MULTILINE
            )

            if has_markdown:
                # 将 Markdown 转换为 HTML
                html_content = markdown2.markdown(
                    panel.current_response,
                    extras=['fenced-code-blocks', 'tables', 'break-on-newline']
                )

                # 替换流式输出的文本为渲染后的 HTML
                cursor = panel.chat_display.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.movePosition(cursor.MoveOperation.StartOfBlock, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()

                # 插入带有样式的 HTML
                styled_html = f"""
                    <div style="margin: 8px 0;">
                        <b>AI助手:</b>
                        <div style="margin-top: 4px;">{html_content}</div>
                    </div>
                """
                cursor.insertHtml(styled_html)
            else:
                # 如果没有 Markdown 语法，则保持原有内容不变
                pass

            # 更新对话历史
            self.conversation_histories[model_index].append({
                "role": "assistant",
                "content": panel.current_response
            })

            # 重置当前响应并停止加载指示器
            panel.current_response = ""
            panel.loading_indicator.stop()

            # 自动滚动到底部
            scrollbar = panel.chat_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def handle_error(self, error):
        print(f"Error in worker thread: {error}")
        # 发生错误时停止所有加载动画
        for panel in self.chat_panels:
            panel.loading_indicator.stop()

    def clear_memory(self):
        self.conversation_histories = [[] for _ in self.chat_panels]
        for panel in self.chat_panels:
            panel.chat_display.setHtml("""
                <html>
                <head>
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
                        pre { background-color: #f3f4f6; padding: 12px; border-radius: 6px; }
                        code { font-family: Consolas, Monaco, "Courier New", monospace; }
                        blockquote { border-left: 4px solid #e5e7eb; margin: 0; padding-left: 16px; }
                        p { line-height: 1.6; }
                    </style>
                </head>
                <body>
                    <h1>新的对话</h1>
                </body>
                </html>
            """)

    def closeEvent(self, event):
        """在关闭窗口时保存主题设置"""
        settings = QSettings("MyCompany", "ChatApp")
        theme = "day" if self.styleSheet() == self.day_style else "night"
        settings.setValue("theme", theme)
        self.save_conversation_history()
        super().closeEvent(event)