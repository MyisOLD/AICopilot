# build.py
import time

import PyInstaller.__main__
import os
import shutil
import platform
import sys
import logging
from pathlib import Path
import json

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class BuildError(Exception):
    """自定义构建错误类"""
    pass


def check_required_files():
    """检查必需的文件是否存在"""
    required_files = {
        'main.py': '主程序文件',
        'requirements.txt': '依赖文件',
        'assets/app_icon.ico': '应用图标',
        'configFiles/config.json': '配置文件',
        'configFiles/prompts.json': '提示词模板'
    }

    missing_files = []
    for file_path, description in required_files.items():
        if not Path(file_path).exists():
            missing_files.append(f"{description} ({file_path})")

    if missing_files:
        raise BuildError(f"缺少必需的文件：\n" + "\n".join(missing_files))


def get_platform_info():
    """获取平台信息"""
    # 优先使用环境变量中的平台信息（来自GitHub Actions）
    platform_name = os.environ.get('PLATFORM', platform.system().lower())
    arch = os.environ.get('ARCH', platform.machine().lower())

    # 标准化架构名称
    if arch in ('amd64', 'x86_64', 'x64'):
        arch = 'x86_64'

    supported_platforms = {'linux', 'windows'}
    supported_archs = {'x86_64'}

    if platform_name not in supported_platforms:
        raise BuildError(f"不支持的平台: {platform_name}")
    if arch not in supported_archs:
        raise BuildError(f"不支持的架构: {arch}")

    return platform_name, arch

def clean_directory(dir_path):
    """确保目录被彻底清理"""
    if dir_path.exists():
        shutil.rmtree(dir_path)
        logging.info(f"清理目录: {dir_path}")
        # 确保目录已被删除
        while dir_path.exists():
            time.sleep(0.1)


import shutil
import logging
from pathlib import Path
import PyInstaller.__main__

def create_exe():
    """创建可执行文件"""
    try:
        # 检查必需文件
        check_required_files()

        # 获取平台信息
        platform_name, arch = get_platform_info()
        logging.info(f"开始构建 {platform_name}-{arch} 版本")

        # 设置输出目录
        dist_dir = Path(f"dist/{platform_name}_{arch}")
        build_dir = Path("build")

        # 清理旧的构建文件
        for dir_path in (dist_dir, build_dir):
            clean_directory(dir_path)

        # 创建输出目录
        dist_dir.parent.mkdir(parents=True, exist_ok=True)

        # 确定路径分隔符
        separator = ';' if platform_name == 'windows' else ':'

        # 基本 PyInstaller 参数
        args = [
            'main.py',
            f'--name=AICopilot',
            '--windowed',
            '--clean',
            '--noconfirm',
            f'--distpath={dist_dir}',  # 直接输出到 dist/windows_x86_64
            '--icon=assets/app_icon.ico',
            '--log-level=INFO',
        ]

        # 添加数据文件
        data_files = [
            ('configFiles/config.json', '.'),
            ('configFiles/prompts.json', '.'),
            ('assets', 'assets'),
        ]

        for src, dst in data_files:
            src_path = Path(src)
            if src_path.exists():
                args.append(f'--add-data={src}{separator}{dst}')
                logging.info(f"添加数据文件: {src} -> {dst}")
            else:
                logging.warning(f"数据文件不存在，已跳过: {src}")

        # 添加隐藏导入（如果需要）
        hidden_imports = [
            'module_name',  # 替换为实际需要隐藏导入的模块
        ]
        for module in hidden_imports:
            args.append(f'--hidden-import={module}')

        # 运行 PyInstaller
        logging.info("开始 PyInstaller 构建")
        PyInstaller.__main__.run(args)

        # 验证构建结果
        exe_name = "AICopilot.exe" if platform_name == 'windows' else "AICopilot"
        expected_exe = dist_dir / exe_name

        if not expected_exe.exists():
            raise BuildError(f"构建失败：未找到预期的可执行文件 {expected_exe}")

        logging.info(f"构建成功: {expected_exe}")

    except BuildError as e:
        logging.error(f"构建错误: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"未预期的错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    create_exe()