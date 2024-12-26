import json
import sys
import os

def get_models():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config.get('models', [])
def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 然后修改配置文件读取部分
def get_models():
    config_path = get_resource_path('config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get('models', [])
def get_prompt_templates():
    try:
        with open('prompts.json', 'r') as f:
            config = json.load(f)
        return config.get('templates', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_custom_prompts():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config.get('custom_prompts', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_custom_prompts(prompts):
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    config['custom_prompts'] = prompts
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)