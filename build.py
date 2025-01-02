import PyInstaller.__main__
import os
import shutil


def create_exe():
    # 确保输出目录存在
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    args = [
        'main.py',  # 主程序入口
        '--name=AICopilotV2',  # 可执行文件名
        '--windowed',  # 无控制台窗口
        # '--onefile',  # 打包成单个文件
        '--icon=assets/app_icon.ico',  # 应用图标（如果有）
        f'--add-data=configFiles/config_example.json{os.pathsep}.',  # 添加配置文件
        f'--add-data=configFiles/prompts_example.json{os.pathsep}.',  # 添加提示词模板
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
    ]

    # 运行PyInstaller
    PyInstaller.__main__.run(args)


if __name__ == '__main__':
    create_exe()