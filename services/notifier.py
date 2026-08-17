"""
Phone notifications via Telegram.
If you don't set TELEGRAM_* in .env, it just logs instead.
"""

import httpx
from config import settings
from rich.console import Console

console = Console()


async def send_message(text: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        console.print(f"[dim][NOTIFY] {text}[/dim]")
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10)
            return resp.status_code == 200
    except Exception as e:
        console.print(f"[red]Telegram notify failed: {e}[/red]")
        return False


def send_message_sync(text: str) -> bool:
    """Sync version for non-async code."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        console.print(f"[dim][NOTIFY] {text}[/dim]")
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        with httpx.Client() as client:
            resp = client.post(url, json=payload, timeout=10)
            return resp.status_code == 200
    except Exception as e:
        console.print(f"[red]Telegram notify failed: {e}[/red]")
        return False
