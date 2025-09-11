class Chat:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.type = data.get("type")

class User:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.username = data.get("username")