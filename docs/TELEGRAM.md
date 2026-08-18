# Telegram

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Role

Not a user-facing command bot. The organizer’s bot receives **notify** messages from the Worker (or local `server.py`) via Bot API `sendMessage`.

## Setup

1. BotFather → `/newbot` → store token as `TELEGRAM_BOT_TOKEN` (Worker Secret).
2. Open the bot, send `/start`.
3. `python tools/get_chat_id.py` → `TELEGRAM_CHAT_ID`.
4. Worker uses both secrets; frontend never sees them.

## Message

Worker sends a short RSVP line with the sanitized guest name. Optional frontend fallback: `config.json` `telegramUsername` (no `@`) opens `https://t.me/<user>?text=...` if `fetch` fails.

## Time

No bot scheduler. Invitation start time on the page: **19:30 MSK**.

---

<a id="русский"></a>

## Role

Это не бот с командами для гостя. Бот организатора получает **notify**-сообщения от Worker (или локального `server.py`) через Bot API `sendMessage`.

## Setup

1. BotFather → `/newbot` → токен как `TELEGRAM_BOT_TOKEN` (Worker Secret).
2. Открыть бота, отправить `/start`.
3. `python tools/get_chat_id.py` → `TELEGRAM_CHAT_ID`.
4. Worker использует оба секрета; frontend их не видит.

## Message

Worker шлёт короткую строку RSVP с нормализованным именем гостя. Опциональный fallback frontend: `config.json` `telegramUsername` (без `@`) открывает `https://t.me/<user>?text=...`, если `fetch` не удался.

## Time

Планировщика бота нет. Время начала на странице: **19:30 MSK**.
