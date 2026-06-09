import asyncio
from pyrogram.types import Message, CallbackQuery


class MessageListener:
    """A centralized coordinator for tracking active user conversation states.

    It manages futures tied to specific Telegram chat IDs, resolving them
    automatically when an authorized user update flows through the pipeline.
    """

    def __init__(self):
        """Initializes an empty registry dictionary for routing listener futures."""
        self._listeners = {}

    def register_listener(self, chat_id: int, future: asyncio.Future):
        """Binds a pending async future to a tracking target chat ID location."""
        self._listeners[chat_id] = future

    def unregister_listener(self, chat_id: int):
        """Removes the tracking association lock from the active registry database."""
        self._listeners.pop(chat_id, None)

    def resolve(self, chat_id: int, update: Message | CallbackQuery) -> bool:
        """Fulfills the pending future lock with the received update instance if valid."""
        future = self._listeners.get(chat_id)
        if future and not future.done():
            future.set_result(update)
            self.unregister_listener(chat_id)
            return True
        return False


listener_manager = MessageListener()