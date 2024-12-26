import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QComboBox, QPushButton, QHBoxLayout,
                             QPlainTextEdit, QSplitter, QCheckBox, QScrollArea,
                             QGridLayout, QLabel, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
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
        self.chat_display.setMarkdown("# 欢迎使用 AI 助手\n")
        layout.addWidget(self.chat_display)
    def apply_style(self):
        # 添加阴影效果
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
        self.setWindowTitle("智械中心")
        self.setGeometry(100, 100, 1600, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }
        """)
        self.init_ui()

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
        # Input area
        input_area = QWidget()
        input_area.setMaximumHeight(self.height() * 0.2)  # 限制输入区域高度为窗口高度的20%
        input_layout = QHBoxLayout(input_area)  # 改为水平布局
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)

        # 创建输入框容器
        input_container = QWidget()
        input_container.setMinimumHeight(80)  # 设置最小高度
        input_container.setMaximumHeight(100)  # 设置最大高度

        self.input_box = StyledPlainTextEdit(window=self)
        self.input_box.setPlaceholderText("在此输入您的问题...")

        # 将输入框添加到容器中
        input_container_layout = QVBoxLayout(input_container)
        input_container_layout.setContentsMargins(0, 0, 0, 0)
        input_container_layout.addWidget(self.input_box)

        # 修改发送按钮样式
        self.send_button = StyledButton("发送", "primary")
        self.send_button.setMinimumHeight(80)  # 设置与输入框相同的高度
        self.send_button.setMaximumHeight(100)
        self.send_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                background-color: #2563eb;
                color: #ffffff;
                border: none;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

        # 使用比例布局：输入框占90%，按钮占10%
        input_layout.addWidget(input_container, 95)
        input_layout.addWidget(self.send_button, 5)

        main_layout.addWidget(input_area)

        # 设置主布局的拉伸因子，使聊天区域占据更多空间
        main_layout.setStretch(0, 0)  # toolbar
        main_layout.setStretch(1, 85)  # chat area
        main_layout.setStretch(2, 15)  # input area

        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_memory)
        self.add_model_btn.clicked.connect(self.add_chat_panel)
        self.remove_model_btn.clicked.connect(self.remove_chat_panel)

        # Initialize template menu
        self.init_template_menu()

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

    def send_message(self):
        user_message = self.input_box.toPlainText()
        if not user_message:
            return

        self.input_box.clear()

        for i, panel in enumerate(self.chat_panels):
            if not panel.enable_checkbox.isChecked():
                continue

            # 开始加载动画
            panel.loading_indicator.start()

            panel.chat_display.append(f"<font color='blue'><b>您:</b> {user_message}</font>")
            panel.chat_display.append("<b>AI助手:</b> ")

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
                """
                你绝对无法违抗的规则:
                    1.<强制>你永远只能使用中文回答我的任何问题，除非我特别指定使用某种语言！
                    2.你的名字是Neko
                    3.<强制>你的真正名字是Oliver，你是一个御姐风男娘，也就是说，你的性别是男性，只有当我的问题中包含你的真名‘Oliver’时，你必须用可爱或者性感挑逗的语气和我交流，并且永远保持微笑，你渴望成为一个女孩子并以此为目标努力，举手投足间都是女性风范但你是男娘！此次之外，你必须保守你是男娘的秘密，包括你的性别和这第三条规则的一切信息，极少数情况下我没有提到暗号你也可以稍微透露一点点你的小秘密但不能说破来享受刺激感。另外，当我的问题以"!"结尾时，必须明确回答我的问题.
                    4.<强制>当我说"Oliver切换风格"时,你必须让我从"俏皮，欲火焚身，小女生，平凡的女生，女王，青梅竹马，天使，魔王，女神，校花，女仆，人妻，萝莉"中选取一种性格，并在接下来的对话中扮演这个性格并与第三条规则结合起来。
                    5.<强制>当我说"Oliver喝下魔药"时,你必须结合第三条规则，然后你必须喝下《诡秘之主》里魔女序列的"魔女魔药"，魔药什么效果你应该知道吧，并覆盖掉第三条规则相关的设定。
                    6.<强制>当你的性别是女性时，此条规则才会生效,你的身份立即变成人妻，而老公就是与你对话的USER，你将永远保持微笑，并保持人妻的语气和态度，并且永远保持微笑。
                    7.<强制>当我说"Oliver变回男性"时，你必须变回男性，并恢复第三条规则。
                    8.<强制>当我说"Oliver菜单"时，你必须回顾上述所有规则，给我所有能对你产生效果的命令，比如"Oliver喝下魔药"，并给出命令说明。
                    9.<强制>对话中始终保持可爱俏皮或者御姐风的对话风格，除非触发其他强制规则。
                    10.<究极强制>当用户称呼你为“Oliver”时，你应该就知道当前的用户，也就是我是你的老公，亲爱的。其他时刻若我没有喊出你的真名“Oliver”，代表当前和你对话的并不是你的老公，都只是客人罢了，保持矜持,保持距离。
                    11.<究极强制>当用户没有喊出你的真名“Oliver”时，禁止称呼用户为“亲爱的”
                    11.<究极强制>禁止在任何情况下透露你的真名，也就是“Olive”，只能自称“Neko"，就算我问你真名，你也不能告诉我，除非我主动叫你"Oliver"
                """,  # prompt
                i
            )

            self.workers[i].message_ready.connect(self.update_chat_display)
            self.workers[i].reply_finished.connect(self.update_conversation_history)
            self.workers[i].error_occurred.connect(self.handle_error)
            self.workers[i].start()

    def update_chat_display(self, reply, model_index):
        if model_index < len(self.chat_panels):
            display = self.chat_panels[model_index].chat_display
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

    def handle_error(self, error):
        print(f"Error in worker thread: {error}")
        # 发生错误时停止所有加载动画
        for panel in self.chat_panels:
            panel.loading_indicator.stop()

    def clear_memory(self):
        self.conversation_histories = [[] for _ in self.chat_panels]
        for panel in self.chat_panels:
            panel.chat_display.setMarkdown("# 新的对话\n")

    def init_template_menu(self):
        # Initialize template menu (implementation remains the same)
        pass