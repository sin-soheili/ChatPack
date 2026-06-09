from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from chatpack.core.field import BaseField


class ConfirmDialog(BaseField):
    """A component that displays a binary yes/no confirmation dialog.

    It forces the user to interact via inline buttons and returns a boolean
    representing the choice immediately upon interaction.
    """

    def __init__(
        self,
        prompt: str,
        yes_text: str = "Yes ✅",
        no_text: str = "No ❌",
        **kwargs,
    ):
        """Initializes the ConfirmDialog with custom button text."""
        super().__init__(key="confirm", prompt=prompt, **kwargs)
        self.yes_text = yes_text
        self.no_text = no_text

    def _build_keyboard(self) -> InlineKeyboardMarkup:
        """Builds the inline keyboard containing yes and no options."""
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        self.yes_text, callback_data="cp:confirm:yes"
                    ),
                    InlineKeyboardButton(
                        self.no_text, callback_data="cp:confirm:no"
                    ),
                ]
            ]
        )

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Generates payload arguments for sending or editing the message."""
        if is_retry:
            return {}
        return {"reply_markup": self._build_keyboard()}

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> bool | None:
        """Processes the inline button callback."""
        if isinstance(update, CallbackQuery):
            value = update.data.split(":")[-1]
            return value == "yes"

        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> bool:
        """A helper method for standalone usage that returns only the boolean result.

        Args:
            client: The Pyrogram Client instance.
            chat_id (int): The target Telegram chat ID.
            timeout (int, optional): Expiration time in seconds. Defaults to 120.

        Returns:
            bool: True if 'Yes' was clicked, False if 'No' was clicked.
        """
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value