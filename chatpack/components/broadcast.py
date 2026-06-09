import asyncio
from typing import List
from pyrogram import Client
from pyrogram.types import Message as PyroMessage
from chatpack.core.field import BaseField


class BroadcastSender(BaseField):
    """A component responsible for broadcasting messages to a list of users.

    It captures any message type from the admin, replicates it across
    all target users sequentially without altering the admin's chat UI,
    and returns the final execution statistics.
    """

    def __init__(
        self,
        user_ids: List[int],
        prompt: str = "Please forward or send the message you want to broadcast:",
        **kwargs,
    ):
        """Initializes the BroadcastSender with a target list of user IDs.

        Args:
            user_ids (List[int]): A list of Telegram chat/user IDs to receive the broadcast.
            prompt (str, optional): The instruction message sent to the admin.
            **kwargs: Additional keyword arguments passed to the BaseField.
        """
        super().__init__(key="broadcast", prompt=prompt, **kwargs)
        self.user_ids = user_ids

    async def process_response(
        self, update: PyroMessage, sent_message: PyroMessage
    ) -> dict | None:
        """Processes the received message and broadcasts it directly to users.

        Args:
            update (PyroMessage): The incoming message containing the broadcast content.
            sent_message (PyroMessage): The prompt message originally sent by the bot.

        Returns:
            dict | None: A dictionary containing 'success', 'failed', and 'total' counts,
                         or None if the update is invalid.
        """
        if isinstance(update, PyroMessage):
            success_count = 0
            failure_count = 0

            for user_id in self.user_ids:
                try:
                    await update.copy(chat_id=user_id)
                    success_count += 1
                except Exception:
                    failure_count += 1

                await asyncio.sleep(0.05)

            return {
                "success": success_count,
                "failed": failure_count,
                "total": len(self.user_ids),
            }

        return None