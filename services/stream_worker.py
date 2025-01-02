# chat_app/services/stream_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
import time
from .api_service import APIService


class StreamWorker(QThread):
    """
    处理API流式响应的工作线程
    负责发送请求并实时处理返回的数据流
    """
    # 信号定义
    message_ready = pyqtSignal(str, int)  # 单个消息片段准备好
    reply_finished = pyqtSignal(str, int)  # 完整回复结束
    error_occurred = pyqtSignal(str)  # 发生错误

    def __init__(self, conversation_history, user_message, api_url, model_name, api_key, prompt, model_index):
        """
        初始化流式处理工作线程

        Args:
            conversation_history (list): 对话历史记录
            user_message (str): 用户当前消息
            api_url (str): API 端点URL
            model_name (str): 模型名称
            api_key (str): API密钥
            prompt (str): 系统提示词
            model_index (int): 模型索引
        """
        super().__init__()
        self.conversation_history = conversation_history
        self.user_message = user_message
        self.api_url = api_url
        self.model_name = model_name
        self.api_key = api_key
        self.prompt = prompt
        self.model_index = model_index
        self.reply = ''

    def run(self):
        """
        线程执行的主要逻辑
        发送API请求并处理流式响应
        """
        try:
            # 使用APIService发送请求
            response = APIService.send_request(
                self.conversation_history,
                self.user_message,
                self.api_url,
                self.model_name,
                self.api_key,
                self.prompt
            )

            # 检查是否返回了错误字符串
            if isinstance(response, str):
                self.message_ready.emit(response, self.model_index)
                return

            # 处理流式响应
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        self.reply += content
                        self.message_ready.emit(content, self.model_index)
                        time.sleep(0.01)  # 控制输出速度

            # 发送完整回复信号
            self.reply_finished.emit(self.reply, self.model_index)
            # 清空回复缓存
            self.reply = ''

        except Exception as e:
            print(f"Streaming error: {str(e)}")
            self.error_occurred.emit(str(e))

    def stop(self):
        """
        停止当前工作线程
        """
        self.terminate()
        self.wait()