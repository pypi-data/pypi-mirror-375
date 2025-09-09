class Message:
    def __init__(self, data: dict):
        self.id = data.get("message_id")
        self.chat = data.get("chat", {})
        self.from_user = data.get("from", {})
        self.text = data.get("text")
        self.date = data.get("date")