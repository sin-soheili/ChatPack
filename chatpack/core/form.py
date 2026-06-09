import asyncio
from typing import List, Any
from pyrogram import Client


class Form:
    """A collection manager responsible for sequencing multiple chatpack fields.

    It handles executing individual fields in order, aggregate collected form results,
    manages timeouts collectively, and optionally flushes the chat UI history.
    """

    def __init__(
        self, fields: List[Any], timeout_per_field: int = 120, cleanup: bool = False
    ):
        """Initializes the Form configuration with targeted sequential fields."""
        self.fields = fields
        self.timeout_per_field = timeout_per_field
        self.cleanup = cleanup

    async def run(self, client: Client, chat_id: int) -> dict | None:
        """Executes each assigned field sequentially and compiles the gathered response datasets."""
        results = {}
        all_tracked_ids = []

        try:
            for field in self.fields:
                value, msg_ids = await field.ask(
                    client, chat_id, timeout=self.timeout_per_field
                )
                all_tracked_ids.extend(msg_ids)
                results[field.key] = value

            if self.cleanup and all_tracked_ids:
                asyncio.create_task(
                    client.delete_messages(chat_id, all_tracked_ids)
                )

            return results

        except (asyncio.TimeoutError, asyncio.CancelledError):
            if self.cleanup and all_tracked_ids:
                asyncio.create_task(
                    client.delete_messages(chat_id, all_tracked_ids)
                )
            return None