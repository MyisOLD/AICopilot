import winreg


class ProxyUtils:
    @staticmethod
    def get_win11_proxy_settings():
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            )
            proxy_enable = winreg.QueryValueEx(reg_key, "ProxyEnable")[0]
            proxy_server = winreg.QueryValueEx(reg_key, "ProxyServer")[0]
            winreg.CloseKey(reg_key)

            return {
                "enabled": bool(proxy_enable),
                "server": proxy_server if proxy_enable else None
            }
        except WindowsError as e:
            print(f"读取注册表错误: {e}")
            return None