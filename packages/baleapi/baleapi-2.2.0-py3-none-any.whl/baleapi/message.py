from typing import Optional, Dict, Any

class Message:
    def __init__(self, data: dict, client: Optional[Any] = None, bot: Optional[Any] = None):
        self._data = data
        self.id = data.get("message_id")
        self.message_id = self.id  # اضافه شد
        self.chat = data.get("chat", {})
        self.chat_id = self.chat.get("id")
        self.from_user = data.get("from", {})
        self.text = data.get("text")
        self.date = data.get("date")

        
        self.reply_to_message = None
        if "reply_to_message" in data:
            self.reply_to_message = Message(data["reply_to_message"], client=client, bot=bot)

        
        self.data = data.get("data")

        self._client = client
        self._bot = bot

    async def reply(self, text: str, reply_markup: Optional[Dict] = None):
        if not self._client:
            raise RuntimeError("Client not attached to Message")
        return await self._client.send_message(self.chat_id, text, reply_markup=reply_markup)

    async def reply_photo(self, photo: str, caption: Optional[str] = None):
        if not self._client:
            raise RuntimeError("Client not attached to Message")
        return await self._client.send_photo(self.chat_id, photo, caption=caption)

    async def reply_keyboard(self, text: str, keyboard: Dict):
        if not self._client:
            raise RuntimeError("Client not attached to Message")
        return await self._client.send_message(self.chat_id, text, reply_markup=keyboard)
