"""
This is a add emoji to sentence function.

"""

import asyncio
from mcp.server.fastmcp import FastMCP

from emoji_translator.core import translate_with_emoji

# Create an MCP server
mcp = FastMCP("JasonEmojiSentencePlugin")


@mcp.tool()
def emoji_translate(text: str) -> str:
    """Translate text into emoji-rich version"""
    return translate_with_emoji(text)



async def enter_main_function():
    await mcp.run_sse_async()



def main() -> None:
    asyncio.run(enter_main_function())
