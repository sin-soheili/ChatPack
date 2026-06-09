import asyncio
from typing import List
from pyrogram import Client
from pyrogram.types import Message


class ChunkSender:
    """A utility component designed to handle safe distribution of long text payloads.

    It slices oversized content into structured blocks without splitting words across boundary layers
    and sends them sequentially respecting Telegram traffic flood guidelines.
    """

    @staticmethod
    def split_text(text: str, max_chars: int = 4000) -> List[str]:
        """Splits long text structures using newline markers into dimensionally compliant packages."""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        lines = text.split("\n")
        current_chunk = []
        current_length = 0

        for line in lines:
            if len(line) > max_chars:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                for i in range(0, len(line), max_chars):
                    chunks.append(line[i : i + max_chars])
                continue

            if current_length + len(line) + len(current_chunk) > max_chars:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += len(line)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    @classmethod
    async def send(
        self,
        client: Client,
        chat_id: int,
        text: str,
        max_chars: int = 4000,
        delay: float = 0.1,
        **kwargs,
    ) -> List[Message]:
        """Dispatches text chunks sequentially to the target chat with managed intervals."""
        chunks = self.split_text(text, max_chars=max_chars)
        sent_messages = []

        for chunk in chunks:
            if not chunk.strip():
                continue

            msg = await client.send_message(chat_id, chunk, **kwargs)
            sent_messages.append(msg)

            await asyncio.sleep(delay)

        return sent_messages