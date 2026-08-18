# API

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Production

One notify endpoint on the Cloudflare Worker (URL in `config.json` → `notifyUrl`).

| Method | Path | Body |
|--------|------|------|
| OPTIONS | `/` (Worker) | CORS preflight |
| POST | Worker URL | JSON `{ "guestName": string, "turnstileToken"?: string }` |

## Local `tools/server.py`

| Method | Path | Body |
|--------|------|------|
| OPTIONS | `/api/notify` | CORS |
| POST | `/api/notify` | Same JSON |
| GET/HEAD | static files | Site assets; blocked names are not served |

## Limits

| Rule | Value |
|------|--------|
| Guest name | Printable, trimmed, max 60 chars |
| Body size (local) | Max 4096 bytes |
| Rate limit | 8 requests / client IP / 3600 seconds |
| CORS | Allowlist; missing/unknown Origin → 403 on browser requests |

## Responses

| Status | JSON |
|--------|------|
| 200 | `{ "ok": true }` |
| 400 | Bad JSON / empty name |
| 403 | Origin / Turnstile |
| 405 | Not POST |
| 429 | Rate limit |
| 502 | Turnstile or Telegram network/API |
| 503 | Missing `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` |

No REST CRUD. No health database.

---

<a id="русский"></a>

## Production

Один notify-endpoint на Cloudflare Worker (URL в `config.json` → `notifyUrl`).

| Method | Path | Body |
|--------|------|------|
| OPTIONS | `/` (Worker) | CORS preflight |
| POST | URL Worker | JSON `{ "guestName": string, "turnstileToken"?: string }` |

## Local `tools/server.py`

| Method | Path | Body |
|--------|------|------|
| OPTIONS | `/api/notify` | CORS |
| POST | `/api/notify` | Тот же JSON |
| GET/HEAD | static files | Ассеты сайта; заблокированные имена не отдаются |

## Limits

| Rule | Value |
|------|--------|
| Имя гостя | Печатные символы, trim, макс. 60 |
| Размер тела (local) | Макс. 4096 байт |
| Rate limit | 8 запросов / IP клиента / 3600 секунд |
| CORS | Allowlist; нет/чужой Origin → 403 для браузера |

## Responses

| Status | JSON |
|--------|------|
| 200 | `{ "ok": true }` |
| 400 | Плохой JSON / пустое имя |
| 403 | Origin / Turnstile |
| 405 | Не POST |
| 429 | Rate limit |
| 502 | Сеть/API Turnstile или Telegram |
| 503 | Нет `TELEGRAM_BOT_TOKEN` или `TELEGRAM_CHAT_ID` |

Нет REST CRUD. Нет health-базы.
