import asyncio
from typing import Callable, Any
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from chatpack.utils.listener import listener_manager


class BaseField:
    """The foundational building block for all interactive chatpack fields.

    It manages the lifecycle of prompting, awaiting asynchronous updates,
    input validation, timeout handling, and tracking message IDs for cleanup.
    """

    def __init__(
        self,
        key: str,
        prompt: str,
        validators: list[Callable[[Any], bool]] = None,
        error_message: str = "Invalid input, please try again.",
        timeout_message: str = "⏱ Session timed out due to inactivity.",
    ):
        """Initializes the base field state and tracking attributes."""
        self.key = key
        self.prompt = prompt
        self.validators = validators or []
        self.error_message = error_message
        self.timeout_message = timeout_message

    def _validate(self, value: Any) -> bool:
        """Runs the collected validators against the extracted value."""
        for validator in self.validators:
            if not validator(value):
                return False
        return True

    def _get_kwargs(self, is_retry: bool = False) -> dict:
        """Hook to append extra arguments like reply_markup to the prompt message."""
        return {}

    async def ask(
        self, client: Client, chat_id: int, timeout: int = 120
    ) -> tuple[Any, list[int]]:
        """Orchestrates the message request/response loop within a secure chat lock."""
        current_prompt = self.prompt
        is_retry = False
        tracked_message_ids = []

        while True:
            extra_kwargs = self._get_kwargs(is_retry=is_retry)
            sent_message = await client.send_message(
                chat_id, current_prompt, **extra_kwargs
            )
            tracked_message_ids.append(sent_message.id)

            while True:
                loop = asyncio.get_running_loop()
                future = loop.create_future()

                listener_manager.register_listener(chat_id, future)

                try:
                    update = await asyncio.wait_for(future, timeout=timeout)

                    if isinstance(update, Message):
                        tracked_message_ids.append(update.id)
                        if update.text == "/cancel":
                            raise asyncio.CancelledError(
                                "Flow cancelled by user."
                            )

                    value = await self.process_response(update, sent_message)

                    if value is None:
                        continue

                    if self._validate(value):
                        return value, tracked_message_ids

                    is_retry = True
                    current_prompt = f"⚠️ {self.error_message}\n\n{self.prompt}"
                    break

                except asyncio.TimeoutError:
                    listener_manager.unregister_listener(chat_id)
                    await client.send_message(chat_id, self.timeout_message)
                    raise asyncio.TimeoutError("Flow timed out.")

                except Exception as e:
                    listener_manager.unregister_listener(chat_id)
                    raise e