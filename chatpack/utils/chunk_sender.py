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
    def split_text(text: str, max_chars: int = 4096) -> List[str]:
        if len(text) <= max_length:
            return [text]
    
        chunks = []
        remaining = text
    
        while remaining:
            if len(remaining) <= max_length:
                chunks.append(remaining)
                break
    
            cut = remaining[:max_length]
    
            last_newline = cut.rfind('\n')
            if last_newline > 0:
                chunk = cut[:last_newline]
                remaining = remaining[last_newline + 1:]
            else:
                last_space = cut.rfind(' ')
                if last_space > 0 and last_space > len(cut) // 2:
                    chunk = cut[:last_space]
                    remaining = remaining[last_space + 1:]
                else:
                    chunk = cut
                    remaining = remaining[max_length:]
    
            if chunk:
                chunks.append(chunk)
    
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
