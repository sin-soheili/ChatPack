from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from chatpack.core.field import BaseField


class RatingStars(BaseField):
    """A field component that provides an interactive star rating interface.

    It updates the inline keyboard dynamically as the user selects rating
    scores and returns the final integer value upon submission.
    """

    def __init__(
        self,
        key: str,
        prompt: str,
        max_stars: int = 5,
        submit_button_text: str = "Submit Rating 📤",
        success_message_format: str = "{prompt}\n\n✅ Thank you for rating! You gave: {stars} Stars",
        **kwargs,
    ):
        """Initializes the RatingStars component with threshold and formatting settings."""
        super().__init__(key, prompt, **kwargs)
        self.max_stars = max_stars
        self.submit_button_text = submit_button_text
        self.success_message_format = success_message_format
        self.current_rating = 0

    def _build_keyboard(self) -> InlineKeyboardMarkup:
        """Builds the inline keyboard containing the active/inactive stars and submit button."""
        star_buttons = []
        for i in range(1, self.max_stars + 1):
            icon = "⭐" if i <= self.current_rating else "⚫"
            star_buttons.append(
                InlineKeyboardButton(icon, callback_data=f"cp:{self.key}:set:{i}")
            )

        keyboard = [
            star_buttons,
            [
                InlineKeyboardButton(
                    self.submit_button_text, callback_data=f"cp:{self.key}:submit"
                )
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Attaches the interactive rating interface to the prompt payload."""
        return {"reply_markup": self._build_keyboard()}

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> int | None:
        """Handles dynamic score rendering steps and finalized submissions."""
        if isinstance(update, CallbackQuery):
            await update.answer()

            data_parts = update.data.split(":")
            action = data_parts[-2] if len(data_parts) >= 3 else data_parts[-1]
            value = data_parts[-1]

            if action == "set":
                self.current_rating = int(value)
                await sent_message.edit_reply_markup(
                    reply_markup=self._build_keyboard()
                )
                return None

            elif value == "submit":
                await sent_message.edit_text(
                    self.success_message_format.format(
                        prompt=self.prompt, stars=self.current_rating
                    )
                )
                return self.current_rating

        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> int:
        """A helper method for standalone usage that yields the final integer score directly."""
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value