import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .errors import BaleAPIError
import os

class Client:
    BASE_URL = "https://tapi.bale.ai/bot"

    def __init__(self, token: str):
        self.token = token
        self.url = f"{self.BASE_URL}{self.token}/"

    async def _request(self, method: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            if data is None:
                data = {}
            async with session.post(self.url + method, json=data, headers=headers) as resp:
                res = await resp.json()
        if not res.get("ok"):
            raise BaleAPIError(res.get("error_code", -1), res.get("description", "Unknown error"))
        return res["result"]

    async def _multipart_request(self, method: str, data: Dict[str, Any], file_field: str, file_path: str) -> Dict[str, Any]:
       
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        form = aiohttp.FormData()
        
        for k, v in data.items():
            if v is None:
                continue
             
            form.add_field(k, str(v))
        
        form.add_field(file_field, open(file_path, "rb"))

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + method, data=form) as resp:
                res = await resp.json()
        if not res.get("ok"):
            raise BaleAPIError(res.get("error_code", -1), res.get("description", "Unknown error"))
        return res["result"]

    # ----- متد -----
    async def get_me(self):
        return await self._request("getMe")

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 10):
        data = {"offset": offset, "timeout": timeout}
        return await self._request("getUpdates", data)

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None):
        data = {"chat_id": chat_id, "text": text}
        if reply_markup:
            
            import json
            if not isinstance(reply_markup, str):
                data["reply_markup"] = json.dumps(reply_markup)
            else:
                data["reply_markup"] = reply_markup
        return await self._request("sendMessage", data)

    async def delete_message(self, chat_id: int, message_id: int):
        return await self._request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def edit_message_text(self, chat_id: int, message_id: int, text: str):
        return await self._request("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    # ----- سند -----
    async def send_photo(self, chat_id: int, photo: str, caption: Optional[str] = None):
       
        data = {"chat_id": chat_id}
        if photo.startswith("http://") or photo.startswith("https://"):
            data["photo"] = photo
            if caption:
                data["caption"] = caption
            return await self._request("sendPhoto", data)
        else:
            if caption:
                data["caption"] = caption
            return await self._multipart_request("sendPhoto", data, "photo", photo)

    async def send_video(self, chat_id: int, video: str, caption: Optional[str] = None):
        data = {"chat_id": chat_id}
        if video.startswith("http://") or video.startswith("https://"):
            data["video"] = video
            if caption:
                data["caption"] = caption
            return await self._request("sendVideo", data)
        else:
            if caption:
                data["caption"] = caption
            return await self._multipart_request("sendVideo", data, "video", video)

    async def send_audio(self, chat_id: int, audio: str, caption: Optional[str] = None):
        data = {"chat_id": chat_id}
        if audio.startswith("http://") or audio.startswith("https://"):
            data["audio"] = audio
            if caption:
                data["caption"] = caption
            return await self._request("sendAudio", data)
        else:
            if caption:
                data["caption"] = caption
            return await self._multipart_request("sendAudio", data, "audio", audio)

    async def send_document(self, chat_id: int, document: str, caption: Optional[str] = None):
        data = {"chat_id": chat_id}
        if document.startswith("http://") or document.startswith("https://"):
            data["document"] = document
            if caption:
                data["caption"] = caption
            return await self._request("sendDocument", data)
        else:
            if caption:
                data["caption"] = caption
            return await self._multipart_request("sendDocument", data, "document", document)

    async def send_sticker(self, chat_id: int, sticker: str):
        
        data = {"chat_id": chat_id}
        if sticker.startswith("http://") or sticker.startswith("https://"):
            
            data["sticker"] = sticker
            return await self._request("sendSticker", data)
        elif os.path.exists(sticker):
            return await self._multipart_request("sendSticker", data, "sticker", sticker)
        else:
            
            data["sticker"] = sticker
            return await self._request("sendSticker", data)          
    # ----- گروه / کانال -----
    async def get_chat(self, chat_id: int):
        return await self._request("getChat", {"chat_id": chat_id})

    async def get_chat_members_count(self, chat_id: int):
        return await self._request("getChatMembersCount", {"chat_id": chat_id})

    async def get_chat_administrators(self, chat_id: int):
        return await self._request("getChatAdministrators", {"chat_id": chat_id})

    async def ban_chat_member(self, chat_id: int, user_id: int):
        return await self._request("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def unban_chat_member(self, chat_id: int, user_id: int):
        return await self._request("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def promote_chat_member(self, chat_id: int, user_id: int, **permissions):
        data = {"chat_id": chat_id, "user_id": user_id}
        data.update(permissions)
        return await self._request("promoteChatMember", data)

    async def set_chat_title(self, chat_id: int, title: str):
        return await self._request("setChatTitle", {"chat_id": chat_id, "title": title})

    async def set_chat_description(self, chat_id: int, description: str):
        return await self._request("setChatDescription", {"chat_id": chat_id, "description": description})

    async def set_chat_photo(self, chat_id: int, file_path: str):
        return await self._multipart_request("setChatPhoto", {"chat_id": chat_id}, "photo", file_path)

    async def delete_chat_photo(self, chat_id: int):
        return await self._request("deleteChatPhoto", {"chat_id": chat_id})

    async def pin_chat_message(self, chat_id: int, message_id: int):
        return await self._request("pinChatMessage", {"chat_id": chat_id, "message_id": message_id})

    async def unpin_chat_message(self, chat_id: int, message_id: int):
      return await self._request("unpinChatMessage", {
        "chat_id": chat_id,
        "message_id": message_id
    })
