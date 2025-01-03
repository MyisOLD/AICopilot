import os
import httpx
from openai import OpenAI
from utils.proxy_utils import ProxyUtils

os.environ["http_proxy"] = "http://localhost:3467"
os.environ["https_proxy"] = "http://localhost:3467"


class APIService:

    @staticmethod
    def handle_response(response):
        if isinstance(response, str) and response.startswith("Error:"):
            return response

        full_response = ""
        try:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
            return full_response
        except Exception as e:
            return f"Error processing response: {str(e)}"

    @staticmethod
    def send_request(conversation_history, user_message, api_url, model_name, api_key, prompt):
        proxy_settings = ProxyUtils.get_win11_proxy_settings()

        proxies = {}
        if proxy_settings and proxy_settings["enabled"] and proxy_settings["server"]:
            proxies = {
                "http://": f"http://{proxy_settings['server']}",
                "https://": f"https://{proxy_settings['server']}",
            }
        client = OpenAI(
            api_key=api_key,
            base_url=api_url,
            # http_client=httpx.Client(proxies=proxies if proxies else None)
        )

        try:
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
            return response
        except Exception as e:
            print(f"API request error: {str(e)}")
            return f"Error: {str(e)}"


if __name__ == "__main__":
    conversation_history = ''
    user_message = '你好啊'
    api_url = 'https://yunwu.ai/v1'
    model_name = 'claude-3-5-sonnet-all'
    api_key = 'sk-XC7QONx5EnTqXUmAZPhbyU3Xnsf44gp4obVxeT777u7cHbiU'
    prompt = '你是个好助手'
    responce = APIService.send_request(conversation_history, user_message, api_url, model_name, api_key, prompt)
    for chunk in responce:
        print(chunk)