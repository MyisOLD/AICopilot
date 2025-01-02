import PyInstaller.__main__
import os
import shutil
import platform
import sys


def create_exe(platform_name, arch):
    # 确保输出目录存在
    dist_dir = f"dist/{platform_name}_{arch}"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists('build'):
        shutil.rmtree('build')

    args = [
        'main.py',  # 主程序入口
        '--name=AICopilotV2',  # 可执行文件名
        '--windowed',  # 无控制台窗口
        # '--onefile',  # 打包成单个文件
        '--icon=assets/app_icon.ico',  # 应用图标（如果有）
        f'--add-data=configFiles/config.json{os.pathsep}.',  # 添加配置文件
        f'--add-data=configFiles/prompts.json{os.pathsep}.',  # 添加提示词模板
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
        f'--distpath={dist_dir}',  # 指定输出目录
    ]

    # 运行PyInstaller
    PyInstaller.__main__.run(args)

    # 重命名生成的文件（可选）
    if platform_name == "linux":
        if os.path.exists(f"{dist_dir}/AICopilotV2"):
            os.rename(f"{dist_dir}/AICopilotV2", f"{dist_dir}/AICopilotV2.bin")
    elif platform_name == "windows":
        if os.path.exists(f"{dist_dir}/AICopilotV2.exe"):
            os.rename(f"{dist_dir}/AICopilotV2.exe", f"{dist_dir}/AICopilotV2_{arch}.exe")


if __name__ == '__main__':
    # 获取当前平台和架构
    platform_name = platform.system().lower()
    arch = platform.machine().lower()

    # 支持的平台和架构
    supported_platforms = ["linux", "windows"]
    supported_archs = ["x86_64", "x86"]

    if platform_name not in supported_platforms:
        print(f"Unsupported platform: {platform_name}")
        sys.exit(1)
    if arch not in supported_archs:
        print(f"Unsupported architecture: {arch}")
        sys.exit(1)

    # 打包
    create_exe(platform_name, arch)
