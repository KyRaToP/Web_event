# Architecture

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Overview

Static **web invitation template** on GitHub Pages plus a Cloudflare Worker that forwards RSVP names to Telegram. **No database. No application scheduler.** Event clock on the page is **MSK**; start **19:30 MSK**.

## Components

| Component | Role |
|-----------|------|
| `index.html` + `css/` + `js/script.js` | Public invitation + RSVP form |
| `config.json` | Public `notifyUrl`, `turnstileSiteKey`, optional `telegramUsername` |
| Cloudflare Worker `worker.js` | CORS, rate limit, Turnstile, Telegram `sendMessage` |
| `tools/server.py` | Local static + `POST /api/notify` on `127.0.0.1` |
| `tools/get_chat_id.py` | Resolve `TELEGRAM_CHAT_ID` after `/start` |
| `tools/make_birthday_gif.py` | Optional local GIF (Pillow) |

## Data flow

```text
Guest browser (Pages)
 → POST { guestName, turnstileToken }
 → Worker
 → Turnstile siteverify (required; missing Worker secret → 503)
 → Telegram Bot API
Organizer chat
```

`localStorage` key `babyBossInviteReceived=1` is a sent-flag only (not the name).

## Related

[`DEPLOYMENT.md`](DEPLOYMENT.md) · [`API.md`](API.md) · [`TELEGRAM.md`](TELEGRAM.md) · [`SECURITY.md`](SECURITY.md)

---

<a id="русский"></a>

## Обзор

Статический **шаблон веб-приглашения** на GitHub Pages и Cloudflare Worker, который пересылает имена RSVP в Telegram. **Нет базы. Нет планировщика приложения.** Часы на странице — **MSK**; начало **19:30 MSK**.

## Components

| Component | Role |
|-----------|------|
| `index.html` + `css/` + `js/script.js` | Публичное приглашение + форма RSVP |
| `config.json` | Публичные `notifyUrl`, `turnstileSiteKey`, опционально `telegramUsername` |
| Cloudflare Worker `worker.js` | CORS, rate limit, Turnstile, Telegram `sendMessage` |
| `tools/server.py` | Локальная статика + `POST /api/notify` на `127.0.0.1` |
| `tools/get_chat_id.py` | Получить `TELEGRAM_CHAT_ID` после `/start` |
| `tools/make_birthday_gif.py` | Опциональный локальный GIF (Pillow) |

## Data flow

```text
Guest browser (Pages)
 → POST { guestName, turnstileToken }
 → Worker
 → Turnstile siteverify (обязательно; нет секрета Worker → 503)
 → Telegram Bot API
Organizer chat
```

Ключ `localStorage` `babyBossInviteReceived=1` — только флаг отправки (не имя).

## Related

[`DEPLOYMENT.md`](DEPLOYMENT.md) · [`API.md`](API.md) · [`TELEGRAM.md`](TELEGRAM.md) · [`SECURITY.md`](SECURITY.md)
