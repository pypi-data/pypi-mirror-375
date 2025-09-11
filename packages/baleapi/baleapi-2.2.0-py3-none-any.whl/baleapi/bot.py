import asyncio
from typing import Callable, List, Dict, Any, Optional
from .client import Client
from .message import Message

HandlerFunc = Callable[[Message], Any]
CommandHandlerFunc = Callable[[Message, List[str]], Any]

class Bot:
    def __init__(self, token: str):
        self.client = Client(token)
        
        self.handlers: List[HandlerFunc] = []
        
        self.text_handlers: List[HandlerFunc] = []
        self.photo_handlers: List[HandlerFunc] = []
        
        self.command_handlers: Dict[str, CommandHandlerFunc] = {}

    
    def add_message_handler(self, func: HandlerFunc):
        
        self.handlers.append(func)

    def add_text_handler(self, func: HandlerFunc):
        
        self.text_handlers.append(func)

    def add_photo_handler(self, func: HandlerFunc):
        
        self.photo_handlers.append(func)

    def add_command_handler(self, command: str, func: CommandHandlerFunc):
        
        self.command_handlers[command.lstrip("/")] = func

    async def handle_update(self, update: Dict):
        message_data = update.get("message")
        if not message_data:
            return

        
        msg = Message(message_data, client=self.client, bot=self)

        
        for handler in self.handlers:
            try:
                await handler(msg)
            except Exception as e:
                
                print("Error in generic handler:", e)

        if msg.text:
            text = msg.text.strip()
            if text.startswith("/"):
                parts = text.split()
                cmd = parts[0].lstrip("/").split("@")[0]
                args = parts[1:]
                if cmd in self.command_handlers:
                    try:
                        await self.command_handlers[cmd](msg, args)
                    except Exception as e:
                        print("Error in command handler:", e)
            for handler in self.text_handlers:
                try:
                    await handler(msg)
                except Exception as e:
                    print("Error in text handler:", e)

        
        if message_data.get("photo") or message_data.get("photo_id") or message_data.get("photos"):
            for handler in self.photo_handlers:
                try:
                    await handler(msg)
                except Exception as e:
                    print("Error in photo handler:", e)

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 10) -> list:
        return await self.client.get_updates(offset, timeout)

    async def run_async(self):
        
        updates = await self.get_updates()
        offset = None
        if updates:
            try:
                offset = updates[-1]["update_id"] + 1
            except Exception:
                offset = None

        print("Bot Started... (listening for new messages)")

        while True:
            try:
                updates = await self.get_updates(offset)
                for u in updates:
                    offset = u["update_id"] + 1
                    await self.handle_update(u)
            except Exception as e:
                
                print("Error Loop:", e)
                await asyncio.sleep(2)
            await asyncio.sleep(1)

    def run(self):
        asyncio.run(self.run_async())
