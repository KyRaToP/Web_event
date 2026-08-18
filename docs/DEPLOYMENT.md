# Deployment

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## A) GitHub Pages

1. Push the repo (`index.html` at repository root).
2. Settings → Pages → that branch.
3. Public URL: `https://kyratop.github.io/Web_event/`

## B) Cloudflare Worker

1. Create a Worker; paste `cloudflare-worker/worker.js`; Deploy.
2. Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TURNSTILE_SECRET_KEY` (required on the Worker).
3. Optional `ALLOWED_ORIGINS` — comma-separated. Code default includes `https://kyratop.github.io`, `http://127.0.0.1:8000`, `http://localhost:8000`.
4. Put the Worker HTTPS URL into `config.json` → `notifyUrl`.

## C) Cloudflare Turnstile

1. Add widget; hostnames: `kyratop.github.io` and `localhost` for tests.
2. **Site Key** → `config.json` → `turnstileSiteKey` (public).
3. **Secret Key** → Worker Secret `TURNSTILE_SECRET_KEY` (never git).

## D) Commit public config

Commit `config.json` with live `notifyUrl` and `turnstileSiteKey` only. No tokens.

## Local

```powershell
cd c:\projects\Web_event
python tools/server.py
```

http://127.0.0.1:8000 — bind default `HOST=127.0.0.1`. Local `notifyUrl` is `"/api/notify"`. GitHub Pages needs the Worker HTTPS URL in `notifyUrl`.

## Checklist

| Item | Done when |
|------|-----------|
| Assets | `assets/design.jpg`, `assets/birthday-person.gif` |
| Copy | Invitation text edited in `index.html` |
| Bot | `/start` sent; chat id known |
| Worker secrets | Token + chat id (+ Turnstile secret) |
| CORS | Origin matches Pages |
| Pages | `https://kyratop.github.io/Web_event/` opens; RSVP reaches Telegram |

---

<a id="русский"></a>

## A) GitHub Pages

1. Запушить репозиторий (`index.html` в корне).
2. Settings → Pages → эта ветка.
3. Публичный URL: `https://kyratop.github.io/Web_event/`

## B) Cloudflare Worker

1. Создать Worker; вставить `cloudflare-worker/worker.js`; Deploy.
2. Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TURNSTILE_SECRET_KEY` (обязательно на Worker).
3. Опционально `ALLOWED_ORIGINS` — через запятую. В коде по умолчанию `https://kyratop.github.io`, `http://127.0.0.1:8000`, `http://localhost:8000`.
4. HTTPS URL Worker → `config.json` → `notifyUrl`.

## C) Cloudflare Turnstile

1. Добавить виджет; hostnames: `kyratop.github.io` и `localhost` для тестов.
2. **Site Key** → `config.json` → `turnstileSiteKey` (публичный).
3. **Secret Key** → Worker Secret `TURNSTILE_SECRET_KEY` (никогда в git).

## D) Commit public config

Закоммитить `config.json` только с боевыми `notifyUrl` и `turnstileSiteKey`. Без токенов.

## Local

```powershell
cd c:\projects\Web_event
python tools/server.py
```

http://127.0.0.1:8000 — bind по умолчанию `HOST=127.0.0.1`. Локальный `notifyUrl`: `"/api/notify"`. Для GitHub Pages нужен HTTPS URL Worker в `notifyUrl`.

## Checklist

| Item | Done when |
|------|-----------|
| Assets | `assets/design.jpg`, `assets/birthday-person.gif` |
| Copy | Текст приглашения в `index.html` |
| Bot | Отправлен `/start`; chat id известен |
| Worker secrets | Токен + chat id (+ secret Turnstile) |
| CORS | Origin совпадает с Pages |
| Pages | `https://kyratop.github.io/Web_event/` открывается; RSVP доходит до Telegram |
