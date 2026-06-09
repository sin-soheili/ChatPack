import asyncio
from typing import List, Union
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from pyrogram.errors import UserNotParticipant
from chatpack.core.field import BaseField


class JoinChecker(BaseField):
    """A field component that forces users to join specified sponsor channels.

    It validates channel membership via Telegram's API on demand and blocks
    flow propagation until the conditions (all or any channels) are met.
    """

    def __init__(
        self,
        key: str,
        prompt: str,
        channels: List[Union[int, str]],
        mode: str = "all",
        button_text: str = "Verify Membership ✅",
        channel_button_format: str = "Join Channel {i} 📢",
        success_message_format: str = "{prompt}\n\n✅ Membership verified!",
        not_joined_alert: str = "You must join the channel(s) first! ⚠️",
        **kwargs,
    ):
        """Initializes the JoinChecker with targeting parameters and formatting configurations."""
        super().__init__(key, prompt, **kwargs)
        self.channels = channels
        self.mode = mode.lower()
        self.button_text = button_text
        self.channel_button_format = channel_button_format
        self.success_message_format = success_message_format
        self.not_joined_alert = not_joined_alert

    def _build_keyboard(self) -> InlineKeyboardMarkup:
        """Builds the layout featuring channel links and the main verification button."""
        buttons = []
        for i, channel in enumerate(self.channels, 1):
            url = (
                f"https://t.me/{channel.replace('@', '')}"
                if isinstance(channel, str) and channel.startswith("@")
                else None
            )
            if url:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            self.channel_button_format.format(i=i), url=url
                        )
                    ]
                )

        buttons.append(
            [
                InlineKeyboardButton(
                    self.button_text, callback_data=f"cp:{self.key}:verify"
                )
            ]
        )
        return InlineKeyboardMarkup(buttons)

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Appends the channel navigation keyboard to the current chat prompt."""
        return {"reply_markup": self._build_keyboard()}

    async def _check_membership(self, client, user_id: int) -> bool:
        """Queries Telegram API to evaluate if the user satisfies channel join requirements."""
        joined_count = 0
        for channel in self.channels:
            try:
                await client.get_chat_member(chat_id=channel, user_id=user_id)
                joined_count += 1
                if self.mode == "any":
                    return True
            except UserNotParticipant:
                continue
            except Exception:
                continue

        if self.mode == "all":
            return joined_count == len(self.channels)
        return joined_count > 0

    async def process_response(
        self, update: Message | CallbackQuery, sent_message: Message
    ) -> bool | None:
        """Inspects verification actions and shows alerts if conditions are unfulfilled."""
        if isinstance(update, CallbackQuery):
            value = update.data.split(":")[-1]

            if value == "verify":
                user_id = update.from_user.id
                is_member = await self._check_membership(update._client, user_id)

                if is_member:
                    await update.answer()
                    await sent_message.edit_text(
                        self.success_message_format.format(prompt=self.prompt)
                    )
                    return True
                else:
                    await update.answer(text=self.not_joined_alert, show_alert=True)
                    return None
        return None

    async def ask_value(self, client, chat_id: int, timeout: int = 120) -> bool:
        """A helper method for standalone usage that yields a pure boolean result."""
        value, _ = await self.ask(client, chat_id, timeout=timeout)
        return value