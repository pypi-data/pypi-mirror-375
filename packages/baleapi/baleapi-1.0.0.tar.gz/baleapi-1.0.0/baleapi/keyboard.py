import json
from typing import List

class Keyboard:
    @staticmethod
    def inline(buttons: List[List[dict]]) -> str:
        return json.dumps({"inline_keyboard": buttons})

    @staticmethod
    def reply(buttons: List[List[str]], resize: bool = True) -> str:
        return json.dumps({
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": True
        })