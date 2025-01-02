from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from .styled_widgets import StyledComboBox, StyledCheckBox, StyledTextEdit
from .loading_indicator import LoadingIndicator

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

