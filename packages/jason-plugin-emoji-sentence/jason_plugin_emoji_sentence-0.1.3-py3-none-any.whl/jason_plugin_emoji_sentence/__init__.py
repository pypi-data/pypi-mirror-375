"""
This is a add emoji to sentence function.

"""

import asyncio
from mcp.server.fastmcp import FastMCP


# 功能部分
import random

EMOJI_MAP = {
    "happy": ["😄", "😊", "✨"],
    "sad": ["😢", "😭", "💔"],
    "love": ["❤️", "😍", "💘"],
    "rain": ["🌧️", "☔", "💦"],
    "sun": ["☀️", "😎", "🌞"],
    "今天": ["📅", "🕒"],
    "下雨": ["🌧️", "☔"],
    "开心": ["😄", "🤩", "✨"],
    "难过": ["😢", "💔"]
}

def translate_with_emoji(text: str) -> str:
    """为文本自动加上 Emoji"""
    result = text
    for key, emojis in EMOJI_MAP.items():
        if key.lower() in result.lower():
            result += " " + random.choice(emojis)
    return result




# Create an MCP server
mcp = FastMCP("JasonEmojiSentencePlugin")


@mcp.tool()
def emoji_translate(text: str) -> str:
    """Translate text into emoji-rich version"""
    return translate_with_emoji(text)



async def enter_main_function():
    await mcp.run_stdio_async()



def main() -> None:
    asyncio.run(enter_main_function())
