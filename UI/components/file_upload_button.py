# chat_app/ui/components/file_upload_button.py
import os

from PyQt6.QtWidgets import QPushButton, QMessageBox, QFileDialog, QLabel, QHBoxLayout, QWidget, QVBoxLayout, \
    QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt

from services.file_service import FileService


class FileUploadStatus(QWidget):
    file_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.files = {}
        self.setVisible(False)

    def init_ui(self):
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(4, 0, 4, 0)

        # 创建一个固定容器来包含所有文件
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 把 main_layout 设置给这个容器
        self.main_layout = QHBoxLayout(container)
        self.main_layout.setContentsMargins(4, 0, 4, 0)
        self.main_layout.setSpacing(4)

        # 把容器添加到外层布局
        outer_layout.addWidget(container)
        outer_layout.addStretch()

    def add_file(self, file_name, content):
        """添加新文件"""
        if file_name not in self.files:
            file_widget = QWidget()
            h_layout = QHBoxLayout(file_widget)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(8)

            # 文件图标
            icon_label = QLabel("📄")
            icon_label.setStyleSheet("font-size: 16px;")

            # 文件名标签
            name_label = QLabel(file_name)
            name_label.setStyleSheet("""
                color: #3B82F6;  /* 使用蓝色 */
                font-size: 13px;
                font-weight: 500;
            """)
            name_label.setFixedWidth(name_label.sizeHint().width())

            # 删除按钮
            delete_btn = QPushButton("✖")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #DB2777;
                    padding: 2px 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: #EF4444;
                }
            """)
            delete_btn.clicked.connect(lambda: self.remove_file(file_name))

            h_layout.addWidget(icon_label)
            h_layout.addWidget(name_label)
            h_layout.addWidget(delete_btn)
            h_layout.addStretch()

            self.main_layout.addWidget(file_widget)
            self.files[file_name] = {
                'content': content,
                'widget': file_widget
            }

            self.setVisible(True)

    def remove_file(self, file_name):
        """删除指定文件"""
        if file_name in self.files:
            self.files[file_name]['widget'].deleteLater()
            del self.files[file_name]
            self.file_removed.emit(file_name)

            if not self.files:
                self.setVisible(False)

    def get_all_files(self):
        """获取所有文件内容"""
        return {name: data['content'] for name, data in self.files.items()}

class FileUploadButton(QPushButton):
    file_content_ready = pyqtSignal(str)  # 信号：文件内容准备好

    def __init__(self, parent=None):
        super().__init__("📄上传文件", parent)
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                background-color: #35b796;
                color: #111827;
                border: 1px solid #e5e7eb;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.clicked.connect(self.handle_upload)
        self.file_service = FileService()

    def handle_upload(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择文件",
                "",
                "代码和文本文件 (*.txt *.md *.py *.java *.cpp *.c *.js *.html *.css *.json *.xml *.yaml *.sql);;所有文件 (*.*)"
            )

            if not file_path:
                return

            # 保存文件路径用于获取文件名
            self.setProperty("last_file_path", file_path)

            if not self.file_service.is_file_size_valid(file_path):
                QMessageBox.warning(
                    self,
                    "文件过大",
                    "文件大小不能超过10MB。"
                )
                return

            content = self.file_service.read_file(file_path)
            if content:
                self.file_content_ready.emit(content)
                QMessageBox.information(
                    self,
                    "上传成功",
                    f"文件 {os.path.basename(file_path)} 已成功读取，\n您现在可以发送消息了。"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"读取文件时出错：{str(e)}"
            )

