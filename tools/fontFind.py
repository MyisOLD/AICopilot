from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QLocale
import sys


def check_chinese_fonts():
    """
    检查系统中支持中文的字体
    """
    font_db = QFontDatabase()
    all_families = font_db.families(QFontDatabase.SimplifiedChinese)

    results = []
    results.append("=== 支持中文的系统字体 ===")
    results.append(f"找到 {len(all_families)} 个支持中文的字体:")

    # 列出每个字体及样例
    for i, family in enumerate(all_families, 1):
        results.append(f"\n{i}. {family}")

        # 获取该字体家族的所有样式
        styles = font_db.styles(family)
        if styles:
            results.append("   可用样式:")
            for style in styles:
                # 获取样式的详细信息
                weight = font_db.weight(family, style)
                italic = font_db.italic(family, style)
                results.append(f"   - {style} (字重: {weight}, 斜体: {italic})")

    # 检查当前应用的字体设置
    app = QApplication.instance()
    current_font = app.font()
    results.append("\n\n=== 当前应用字体设置 ===")
    results.append(f"字体家族: {current_font.family()}")
    results.append(f"字体大小: {current_font.pointSize()}")
    results.append(f"字体样式: {current_font.styleName()}")

    return "\n".join(results)


class ChineseFontCheckerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中文字体检查工具")
        self.setGeometry(100, 100, 800, 600)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建文本显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # 显示字体检查结果
        self.text_edit.setText(check_chinese_fonts())

        # 设置字体预览
        self.set_font_preview()

    def set_font_preview(self):
        """
        设置字体预览
        """
        font_db = QFontDatabase()
        all_families = font_db.families(QFontDatabase.SimplifiedChinese)

        # 添加字体样例文本
        sample_text = "你好世界 Hello World 123"

        # 使用 HTML 格式化预览文本
        html_content = "<h3>字体预览</h3>"

        for family in all_families:
            # 添加字体名称
            html_content += f"<p><b>字体: {family}</b></p>"

            # 获取该字体家族的所有样式
            styles = font_db.styles(family)
            if styles:
                html_content += "<ul>"
                for style in styles:
                    # 获取样式的详细信息
                    weight = font_db.weight(family, style)
                    italic = font_db.italic(family, style)
                    html_content += f"<li>样式: {style} (字重: {weight}, 斜体: {italic})</li>"
                html_content += "</ul>"

            # 添加字体预览
            html_content += f"<p style='font-family: {family}; font-size: 12pt;'>{sample_text}</p>"
            html_content += "<hr>"

        # 设置 HTML 内容
        self.text_edit.setHtml(html_content)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置测试字体
    test_font = QFont("Microsoft YaHei", 10)
    app.setFont(test_font)

    window = ChineseFontCheckerWindow()
    window.show()
    sys.exit(app.exec())