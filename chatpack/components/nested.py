from typing import Dict, Any, List
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from chatpack.core.field import BaseField


class NestedMenu(BaseField):
    """A multi-tiered navigation menu built dynamically from a nested dictionary structure.

    It supports backward and forward navigation paths within a single message
    interface and yields the final non-dictionary value upon selection.
    """

    def __init__(
        self,
        key: str,
        prompt: str,
        menu_data: Dict[str, Any],
        back_button_text: str = "🔙 Back",
        main_menu_button_text: str = "🏠 Main Menu",
        success_message_format: str = "{prompt}\n\n✅ Final Selection: *{selection}*",
        **kwargs,
    ):
        """Initializes the NestedMenu with a hierarchy dataset and button structures."""
        super().__init__(key, prompt, **kwargs)
        self.menu_data = menu_data
        self.back_button_text = back_button_text
        self.main_menu_button_text = main_menu_button_text
        self.success_message_format = success_message_format
        self.current_path: List[str] = []

    def _get_current_level(self) -> Dict[str, Any]:
        """Traverses the dictionary using the current recorded navigation state path."""
        current = self.menu_data
        for step in self.current_path:
            if isinstance(current, dict) and step in current:
                current = current[step]
        return current

    def _build_keyboard(self) -> InlineKeyboardMarkup:
        """Generates dynamic option grids based on current path node keys."""
        buttons = []
        current_level = self._get_current_level()

        if isinstance(current_level, dict):
            for key in current_level.keys():
                buttons.append(
                    [
                        InlineKeyboardButton(
                            key, callback_data=f"cp:{self.key}:go:{key}"
                        )
                    ]
                )

        nav_buttons = []
        if len(self.current_path) > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    self.back_button_text, callback_data=f"cp:{self.key}:back"
                )
            )
        if len(self.current_path) > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    self.main_menu_button_text,
                    callback_data=f"cp:{self.key}:main",
                )
            )

        if nav_buttons:
            buttons.append(nav_buttons)

        return InlineKeyboardMarkup(buttons)

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Appends the keyboard structure containing dynamic branch items."""
        return {"reply_markup": self._build_keyboard()}

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> Any | None:
        """Manages forward, back, and home routing states within the inline menu network."""
        if isinstance(update, CallbackQuery):
            await update.answer()

            data_parts = update.data.split(":")
            action = data_parts[-2] if len(data_parts) >= 3 else data_parts[-1]
            value = data_parts[-1]

            if action == "go":
                self.current_path.append(value)
                next_level = self._get_current_level()

                if not isinstance(next_level, dict):
                    await sent_message.edit_text(
                        self.success_message_format.format(
                            prompt=self.prompt, selection=value
                        )
                    )
                    return next_level

                await sent_message.edit_reply_markup(
                    reply_markup=self._build_keyboard()
                )
                return None

            elif value == "back":
                if self.current_path:
                    self.current_path.pop()
                await sent_message.edit_reply_markup(
                    reply_markup=self._build_keyboard()
                )
                return None

            elif value == "main":
                self.current_path.clear()
                await sent_message.edit_reply_markup(
                    reply_markup=self._build_keyboard()
                )
                return None

        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> Any:
        """A helper method for standalone usage that yields the selected menu target value."""
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value