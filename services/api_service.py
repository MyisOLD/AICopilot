import httpx
from openai import OpenAI
from utils.proxy_utils import ProxyUtils

class APIService:
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
            http_client=httpx.Client(proxies=proxies if proxies else None)
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