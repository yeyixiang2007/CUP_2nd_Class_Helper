#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目打包脚本

该脚本用于将中国石油大学第二课堂活动查询助手项目打包为可执行文件(.exe)，
并对打包后的文件进行压缩，以减小文件体积。

使用PyInstaller作为打包工具，支持创建单一可执行文件，并确保包含所有必要的依赖项。
"""

import os
import sys
import shutil
import zipfile
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
# 确保在Windows命令提示符中正确显示中文
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目配置
PROJECT_NAME = "CUP_2nd_Class_Helper"
MAIN_SCRIPT = "main_app.py"
OUTPUT_DIR = "dist"
BUILD_DIR = "build"
ICON_FILE = "res/logo.ico"

# 版本信息
VERSION = "1.0.0"


def ensure_dependencies():
    """
    确保所有必要的依赖已安装
    """
    try:
        # 检查PyInstaller是否已安装
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"],
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("PyInstaller已安装")

        # 安装项目依赖
        logger.info("安装项目依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        logger.info("项目依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖安装失败: {e}")
        return False


def clean_previous_builds():
    """
    清理之前的构建文件
    """
    try:
        if os.path.exists(OUTPUT_DIR):
            logger.info(f"清理之前的输出目录: {OUTPUT_DIR}")
            shutil.rmtree(OUTPUT_DIR)

        if os.path.exists(BUILD_DIR):
            logger.info(f"清理之前的构建目录: {BUILD_DIR}")
            shutil.rmtree(BUILD_DIR)

        if os.path.exists(f"./{BUILD_DIR}/{PROJECT_NAME}.spec"):
            logger.info(f"清理之前的spec文件: {PROJECT_NAME}.spec")
            os.remove(f"./{BUILD_DIR}/{PROJECT_NAME}.spec")

        return True
    except Exception as e:
        logger.error(f"清理构建文件失败: {e}")
        return False


def run_pyinstaller():
    """
    使用PyInstaller打包应用
    """
    try:
        # 构建PyInstaller命令
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--name", PROJECT_NAME,
            "--onefile",  # 创建单一可执行文件
            "--windowed",  # 不显示控制台窗口
            "--clean",  # 清理PyInstaller缓存
            "--distpath", OUTPUT_DIR,
            "--workpath", BUILD_DIR
        ]

        # 添加图标（如果有）
        if ICON_FILE and os.path.exists(ICON_FILE):
            cmd.extend(["--icon", ICON_FILE])

        # 添加版本信息
        version_info = f"{PROJECT_NAME} v{VERSION}"
        cmd.extend(["--version-file", create_version_file()])

        # 指定主脚本
        cmd.append(MAIN_SCRIPT)

        logger.info(f"开始使用PyInstaller打包应用: {' '.join(cmd)}")

        # 执行打包命令
        process = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # 输出打包日志
        if process.stdout:
            logger.info(f"PyInstaller输出:\n{process.stdout}")

        if process.stderr:
            logger.warning(f"PyInstaller警告:\n{process.stderr}")

        if process.returncode != 0:
            logger.error(f"PyInstaller打包失败，返回码: {process.returncode}")
            return False

        logger.info("PyInstaller打包完成")
        return True
    except Exception as e:
        logger.error(f"PyInstaller打包过程中发生错误: {e}")
        return False


def create_version_file():
    """
    创建版本信息文件
    """
    version_file = "version_info.txt"
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(f"# UTF-8\n")
        f.write(f"VSVersionInfo(\n")
        f.write(f"  ffi=FixedFileInfo(\n")
        f.write(f"    filevers=(1, 0, 0, 0),\n")
        f.write(f"    prodvers=(1, 0, 0, 0),\n")
        f.write(f"    mask=0x3f,\n")
        f.write(f"    flags=0x0,\n")
        f.write(f"    OS=0x4,\n")
        f.write(f"    fileType=0x1,\n")
        f.write(f"    subtype=0x0,\n")
        f.write(f"    date=(0, 0)\n")
        f.write(f"  ),\n")
        f.write(f"  kids=[\n")
        f.write(f"    StringFileInfo(\n")
        f.write(f"      [\n")
        f.write(f"        StringTable(\n")
        f.write(f"          '040904B0',\n")
        f.write(f"          [StringStruct('CompanyName', '中国石油大学'),\n")
        f.write(f"          StringStruct('FileDescription', '中国石油大学第二课堂活动查询助手'),\n")
        f.write(f"          StringStruct('FileVersion', '{VERSION}'),\n")
        f.write(f"          StringStruct('InternalName', '{PROJECT_NAME}'),\n")
        f.write(f"          StringStruct('LegalCopyright', '© 2023 中国石油大学第二课堂活动查询助手'),\n")
        f.write(f"          StringStruct('OriginalFilename', '{PROJECT_NAME}.exe'),\n")
        f.write(f"          StringStruct('ProductName', '{PROJECT_NAME}'),\n")
        f.write(f"          StringStruct('ProductVersion', '{VERSION}')])\n")
        f.write(f"      ]\n")
        f.write(f"    ),\n")
        f.write(f"    VarFileInfo([VarStruct('Translation', [1033, 1200])])\n")
        f.write(f"  ]\n")
        f.write(f")\n")
    return version_file


def compress_output():
    """
    压缩打包后的输出文件
    """
    try:
        # 检查输出目录和可执行文件是否存在
        exe_path = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}.exe")
        if not os.path.exists(exe_path):
            logger.error(f"可执行文件不存在: {exe_path}")
            return False

        # 创建压缩文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}_v{VERSION}_{timestamp}.zip")

        logger.info(f"开始压缩文件，输出至: {zip_filename}")

        # 创建ZIP文件
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加可执行文件
            zipf.write(exe_path, os.path.basename(exe_path))

            # 添加其他必要文件
            for root, _, files in os.walk('.'):
                # 跳过构建和输出目录
                if root in [OUTPUT_DIR, BUILD_DIR]:
                    continue

                # 添加文档文件
                for file in files:
                    if file.lower() in ['readme.md', 'license', 'requirements.txt']:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.basename(file_path))

        logger.info(f"文件压缩完成，压缩包大小: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        logger.error(f"文件压缩过程中发生错误: {e}")
        return False


def verify_build():
    """
    验证构建结果
    """
    try:
        # 检查可执行文件是否存在
        exe_path = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}.exe")
        if not os.path.exists(exe_path):
            logger.error(f"构建失败: 可执行文件不存在")
            return False

        # 检查可执行文件大小
        file_size = os.path.getsize(exe_path)
        logger.info(f"构建验证成功！")
        logger.info(f"可执行文件: {exe_path}")
        logger.info(f"文件大小: {file_size / 1024 / 1024:.2f} MB")

        return True
    except Exception as e:
        logger.error(f"构建验证失败: {e}")
        return False


def main():
    """
    主函数，执行整个打包流程
    """
    try:
        start_time = time.time()
        logger.info(f"开始构建 {PROJECT_NAME} v{VERSION}")

        # 1. 确保依赖已安装
        if not ensure_dependencies():
            logger.error("依赖安装失败，构建终止")
            return 1

        # 2. 清理之前的构建文件
        if not clean_previous_builds():
            logger.warning("清理构建文件失败，继续执行")

        # 3. 运行PyInstaller打包应用
        if not run_pyinstaller():
            logger.error("PyInstaller打包失败，构建终止")
            return 1

        # 4. 验证构建结果
        if not verify_build():
            logger.error("构建验证失败，构建终止")
            return 1

        # 5. 压缩输出文件
        if not compress_output():
            logger.warning("文件压缩失败，继续执行")

        end_time = time.time()
        logger.info(f"构建完成！总耗时: {end_time - start_time:.2f} 秒")
        return 0
    except Exception as e:
        logger.error(f"构建过程中发生未预期的错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
