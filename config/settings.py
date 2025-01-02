import json
import os
import sys


class Settings:
    @staticmethod
    def get_resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    @staticmethod
    def load_config():
        config_path = Settings.get_resource_path('configFiles/config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
