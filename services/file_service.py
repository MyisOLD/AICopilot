# chat_app/services/file_service.py

import os
from PyQt6.QtWidgets import QFileDialog
import fitz  # PyMuPDF for PDF files
import chardet  # 用于检测文件编码


class FileService:
    @staticmethod
    def read_text_file(file_path):
        """读取文本文件内容，使用多重编码尝试"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'ascii']

        # 首先尝试用 chardet 检测
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
            detected = chardet.detect(raw_data)
            if detected['encoding']:
                encodings.insert(0, detected['encoding'])
        except:
            pass

        # 尝试不同的编码
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue

        # 如果所有编码都失败，则抛出异常
        raise Exception("无法以任何支持的编码方式读取该文件，请确保文件编码正确")

    @staticmethod
    def read_file(file_path):
        """读取文件内容"""
        try:
            if file_path.lower().endswith('.pdf'):
                return FileService._read_pdf(file_path)
            else:
                return FileService.read_text_file(file_path)
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    @staticmethod
    def _read_pdf(file_path):
        """读取PDF文件内容"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    @staticmethod
    def _read_text_file(file_path):
        """读取文本文件内容，自动检测编码"""
        try:
            # 首先读取文件的二进制内容
            with open(file_path, 'rb') as file:
                raw_data = file.read()

            # 检测文件编码
            result = chardet.detect(raw_data)
            encoding = result['encoding']

            # 使用检测到的编码读取文件
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    @staticmethod
    def get_file_size(file_path):
        """获取文件大小（以MB为单位）"""
        return os.path.getsize(file_path) / (1024 * 1024)

    @staticmethod
    def is_file_size_valid(file_path, max_size_mb=10):
        """检查文件大小是否在允许范围内"""
        return FileService.get_file_size(file_path) <= max_size_mb