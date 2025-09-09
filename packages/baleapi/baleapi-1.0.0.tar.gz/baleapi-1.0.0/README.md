# baleapi

Python library for interacting with the Bale Bot API easily and asynchronously.

---

## Features

* Async support with `asyncio`
* Send messages, photos
* Inline and reply keyboards
* Handle incoming messages via handlers
* Manage updates with offset to ignore old messages
* Error handling with custom exceptions

---

## Installation

```bash
pip install asyncio
```

you can install `bale` for create, edit your own bots

```bash
pip install baleapi
```

---

## Usage Example

```python
import asyncio
from baleapi import Bot, Keyboard

TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(TOKEN)

async def handle(msg):
    chat_id = msg.chat.get("id")
    text = msg.text

    if text == "/start":
        await bot.client.send_message(chat_id, "Welcome to the bot 😎")

    elif text == "/key":
        kb = Keyboard.inline([[{"text": "Keyboard", "callback_data": "press"}]])
        await bot.client.send_message(chat_id, "Here is an inline keyboard:", reply_markup=kb)

    elif text == "/photo":
        photo_url = "https://example.com/photo.jpg"
        await bot.client.send_photo(chat_id, photo_url, caption="Sample photo 😎")

bot.add_message_handler(handle)
bot.run()
```

---

## Modules

### `client`

Handles API requests and provides methods:

* `get_me()`
* `get_updates(offset=None, timeout=10)`
* `send_message(chat_id, text, reply_markup=None)`
* `delete_message(chat_id, message_id)`
* `edit_message_text(chat_id, message_id, text)`
* `send_photo(chat_id, photo, caption=None)`

### `bot`

Manages the bot loop, incoming updates, and message handlers.

* `add_message_handler(func)`
* `run()`
* `run_async()`

### `keyboard`

Create keyboards:

* `Keyboard.inline(buttons)`
* `Keyboard.reply(buttons, resize=True)`

### `message`

Message model with attributes:

* `id`
* `chat`
* `from_user`
* `text`
* `date`

### `errors`

Custom exceptions:

* `BaleError`
* `BaleAPIError`

### `types`

Models for Chat and User objects.

---

## Notes

* Make sure to use your correct Bale Bot token.
* Async methods must be awaited or run within an event loop.

---

## License

MIT License
