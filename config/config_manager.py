import json

from config import Settings


class ConfigManager:
    @staticmethod
    def get_models():
        config = Settings.load_config()
        return config.get('models', [])

    @staticmethod
    def get_templates():
        try:
            with open('./configFiles/prompts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"templates": []}

    @staticmethod
    def save_templates(templates):
        with open('./configFiles/prompts.json', 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=4, ensure_ascii=False)