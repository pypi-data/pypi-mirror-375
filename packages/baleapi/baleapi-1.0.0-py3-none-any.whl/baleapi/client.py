import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .errors import BaleAPIError

class Client:
    BASE_URL = "https://tapi.bale.ai/bot"

    def __init__(self, token: str):
        self.token = token
        self.url = f"{self.BASE_URL}{self.token}/"

    async def _request(self, method: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        
        async with aiohttp.ClientSession() as session:
            if files:
                async with session.post(self.url + method, data=data) as resp:
                    res = await resp.json()
            else:
                headers = {"Content-Type": "application/json"}
                if data is None:
                    data = {}
                async with session.post(self.url + method, json=data, headers=headers) as resp:
                    res = await resp.json()

            if not res.get("ok"):
                raise BaleAPIError(res.get("error_code", -1), res.get("description", "Unknown error"))
            return res["result"]

    
    async def get_me(self):
        return await self._request("getMe")

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 10):
        
        data = {"offset": offset, "timeout": timeout}
        return await self._request("getUpdates", data)

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None):
        data = {"chat_id": chat_id, "text": text}
        if reply_markup:
            data["reply_markup"] = reply_markup
        return await self._request("sendMessage", data)

    async def delete_message(self, chat_id: int, message_id: int):
        return await self._request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def edit_message_text(self, chat_id: int, message_id: int, text: str):
        return await self._request("editMessageText", {"chat_id": chat_id, "message_id": message_id})

    async def send_photo(self, chat_id: int, photo: str, caption: Optional[str] = None):
        data = {"chat_id": chat_id, "photo": photo}
        if caption:
            data["caption"] = caption
        return await self._request("sendPhoto", data)
