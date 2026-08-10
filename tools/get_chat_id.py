"""
Helper script: find your Telegram chat_id.

Steps:
1. Create a bot with @BotFather and put TELEGRAM_BOT_TOKEN into .env
2. Open Telegram, find your bot, press Start / send any message
3. Run: python get_chat_id.py
4. Copy chat_id into TELEGRAM_CHAT_ID in .env
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        value = value.encode("utf-8").decode("utf-8-sig").strip()
        value = "".join(ch for ch in value if ch.isprintable())
        os.environ[key.strip()] = value


def main() -> None:
    load_dotenv(ROOT / ".env")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("Добавьте TELEGRAM_BOT_TOKEN в файл .env и запустите снова.")
        return

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not payload.get("ok"):
        print("Telegram API error:", payload)
        return

    results = payload.get("result") or []
    if not results:
        print("Пока нет сообщений. Напишите боту /start в Telegram и повторите.")
        return

    seen = set()
    print("Найденные chat_id:")
    for item in results:
        message = item.get("message") or item.get("edited_message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None or chat_id in seen:
            continue
        seen.add(chat_id)
        username = chat.get("username") or "-"
        first_name = chat.get("first_name") or ""
        print(f"- chat_id={chat_id}  name={first_name}  username=@{username}")


if __name__ == "__main__":
    main()
