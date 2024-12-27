import PyInstaller.__main__
import os
import shutil


def create_exe():
    # 确保输出目录存在
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # PyInstaller参数
    args = [
        'main.py',  # 主程序入口
        '--name=智械中心V2',  # 可执行文件名
        '--windowed',  # 无控制台窗口
        # '--onefile',  # 打包成单个文件
        '--icon=app_icon.ico',  # 应用图标（如果有）
        # '--add-data=config.json;.',  # 添加配置文件
        # '--add-data=prompts.json;.',  # 添加提示词模板
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
    ]

    # 运行PyInstaller
    PyInstaller.__main__.run(args)


if __name__ == '__main__':
    create_exe()