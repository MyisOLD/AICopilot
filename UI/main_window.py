import json
import os
import re

import markdown2
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDialog, QMenu, QHBoxLayout, QGridLayout, QScrollArea, \
    QMessageBox

from services import StreamWorker
from .components.styled_widgets import StyledButton, StyledPlainTextEdit
from .components.chat_panel import ChatPanel
from .components.template_dialog import TemplateDialog
from services.history_service import HistoryService
from services.api_service import APIService
from config import ConfigManager

class MultiChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.models = ConfigManager.get_models()
        self.chat_panels = []
        self.conversation_histories = []
        self.workers = []
        self.current_template = ""  # Store selected template
        self.templates = ConfigManager.get_templates()  # Load templates first

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
        with open('./configFiles/history.json', 'w') as f:
            json.dump(self.conversation_histories, f)


    def load_conversation_history(self):
        """从文件加载对话历史"""
        try:
            with open('./configFiles/history.json', 'r') as f:
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
            with open('./configFiles/history.json', 'w') as f:
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
        dialog = TemplateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_template = {
                "name": dialog.name_input.text(),
                "prompt": dialog.prompt_input.toPlainText()
            }
            self.templates['templates'].append(new_template)
            ConfigManager.save_templates(self.templates)

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
                self.current_template,
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