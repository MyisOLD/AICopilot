import json

class HistoryService:
    @staticmethod
    def save_history(conversation_histories):
        with open('./configFiles/history.json', 'w') as f:
            json.dump(conversation_histories, f)

    @staticmethod
    def load_history():
        try:
            with open('./configFiles/history.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def clear_history():
        with open('./configFiles/history.json', 'w') as f:
            json.dump([], f)