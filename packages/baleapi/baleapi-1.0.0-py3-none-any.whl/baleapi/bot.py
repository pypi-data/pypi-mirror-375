import asyncio
from typing import Callable, List, Dict, Any
from .client import Client
from .message import Message

HandlerFunc = Callable[[Message], Any]

class Bot:
    def __init__(self, token: str):
        self.client = Client(token)
        self.handlers: List[HandlerFunc] = []

    def add_message_handler(self, func: HandlerFunc):
        self.handlers.append(func)

    async def handle_update(self, update: Dict):
        message_data = update.get("message")
        if message_data:
            msg = Message(message_data)
            for handler in self.handlers:
                await handler(msg)

    async def get_updates(self, offset: int = None, timeout: int = 10) -> list:
        
        params = {"offset": offset, "timeout": timeout}
        return await self.client.get_updates(offset)

    async def run_async(self):
        
        updates = await self.get_updates()
        offset = None
        if updates:
            offset = updates[-1]["update_id"] + 1

        while True:
            updates = await self.get_updates(offset)
            for u in updates:
                offset = u["update_id"] + 1
                await self.handle_update(u)
            await asyncio.sleep(1)

    def run(self):
        print("Bot Started...")
        asyncio.run(self.run_async())