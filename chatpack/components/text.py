from pyrogram.types import Message, CallbackQuery
from chatpack.core.field import BaseField


class TextInput(BaseField):
    """A field component that captures raw textual inputs sent by the user.

    It filters out inline callback traffic, handles direct message responses,
    and returns the plain text string.
    """

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> str | None:
        """Extracts and verifies the text body from an incoming message update."""
        if isinstance(update, Message):
            return update.text
        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> str:
        """A helper method for standalone usage that yields the raw text string directly."""
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value