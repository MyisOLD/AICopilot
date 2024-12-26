import os
import winreg

import httpx
from openai import OpenAI


def get_win11_proxy_settings():
    try:
        # 打开注册表键
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )

        # 检查代理是否启用
        proxy_enable = winreg.QueryValueEx(reg_key, "ProxyEnable")[0]

        # 获取代理服务器地址
        proxy_server = winreg.QueryValueEx(reg_key, "ProxyServer")[0]

        winreg.CloseKey(reg_key)

        return {
            "enabled": bool(proxy_enable),
            "server": proxy_server if proxy_enable else None
        }

    except WindowsError as e:
        print(f"读取注册表错误: {e}")
        return None
def send_request(conversation_history, user_message, api_url, model_name, api_key, prompt):
    proxy_settings = get_win11_proxy_settings()
    proxies = {}
    if proxy_settings and proxy_settings["enabled"] and proxy_settings["server"]:
        proxies = {
            "http://": f"http://{proxy_settings['server']}",
            "https://": f"https://{proxy_settings['server']}",
        }
    else:
        print("未检测到有效代理配置，将不使用代理")

    client = OpenAI(
        api_key=api_key,
        base_url=api_url,
        http_client=httpx.Client(proxies=proxies if proxies else None)
    )
    try:
        print(f"Sending request to: {api_url}")

        messages = []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        print("Request sent successfully")
        return response
    except Exception as e:
        print(f"API request error: {str(e)}")
        return f"Error: {str(e)}"

# 测试代码
if __name__ == "__main__":
    # 测试函数
    # result = get_win11_proxy_settings()['server']
    print("测试结果:", f"http://{get_win11_proxy_settings()['server']}")