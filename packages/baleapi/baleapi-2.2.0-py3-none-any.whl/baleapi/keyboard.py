import json
from typing import List, Dict, Union

class Keyboard:
    @staticmethod
    def inline(buttons: List[List[Dict[str, str]]]) -> str:
        return json.dumps({"inline_keyboard": buttons})

    @staticmethod
    def reply(buttons: List[List[Union[str, Dict]]], resize: bool = True, one_time: bool = True) -> str:
        return json.dumps({
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time
        })
