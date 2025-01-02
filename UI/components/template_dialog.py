from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox


class TemplateDialog(QDialog):
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