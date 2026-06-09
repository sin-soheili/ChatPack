from typing import Dict, List
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from chatpack.core.field import BaseField


class SelectMenu(BaseField):
    """A field component that provides a single-choice selection menu using inline buttons.

    It accepts either a flat list of options or a key-value dictionary,
    updates the UI upon interaction, and returns the selected key string.
    """

    def __init__(
        self, key: str, prompt: str, options: Dict[str, str] | List[str], **kwargs
    ):
        """Initializes the SelectMenu and standardizes list options into a dictionary layout."""
        super().__init__(key, prompt, **kwargs)
        if isinstance(options, list):
            self.options = {item: item for item in options}
        else:
            self.options = options

    def _build_keyboard(self) -> InlineKeyboardMarkup:
        """Generates rows of inline buttons dynamically mapped from options data."""
        buttons = []
        for value, text in self.options.items():
            buttons.append(
                [InlineKeyboardButton(text, callback_data=f"cp:{self.key}:{value}")]
            )
        return InlineKeyboardMarkup(buttons)

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Appends the keyboard markup structure on the initial prompt delivery."""
        if is_retry:
            return {}
        return {"reply_markup": self._build_keyboard()}

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> str | None:
        """Extracts the interacting node key and replaces buttons with static feedback text."""
        if isinstance(update, CallbackQuery):
            data_parts = update.data.split(":")
            value = data_parts[-1]

            await sent_message.edit_text(
                f"{self.prompt}\n\n✅ Selected: *{self.options.get(value)}*"
            )
            return value

        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> str:
        """A helper method for standalone usage that yields the raw selected string value."""
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value