# Web invitation

Static web invitation with Telegram RSVP via Cloudflare Worker.

[English](#english) · [Русский](#русский)

---

<a id="english"></a>

## English

### For the customer

#### What is this

A **GitHub Pages** invitation: guests open a link, read the card, type a name, and tap the button. The organizer receives a Telegram message via a **Cloudflare Worker**. Bot tokens never live on the page. This repository is a **template** — replace photos and text for your event.

All clocks in this product use **Moscow time (MSK, UTC+3)**. There is no application scheduler; the event date and time on the page are MSK (start **19:30 MSK**).

#### How to use

1. Open the Production URL: date, **19:30 MSK**, text, images.
2. Send the link only to guests (the site is as public as the URL).
3. Guest enters a name → Turnstile (production Worker) → Telegram message to you.
4. After the event, consider unpublishing the page or removing personal photos.

#### Production URL

| Item | Value |
|------|--------|
| Invitation | `https://kyratop.github.io/Web_event/` |
| Notify Worker | `[Cloudflare Worker HTTPS URL]` |

#### Core functions

- Mobile invitation card
- Date and start time in **MSK** (**19:30 MSK**)
- RSVP with guest name
- Telegram notify to the organizer
- Optional Cloudflare Turnstile
- Fallback Telegram link if notify fails
- Same browser does not send twice (`localStorage` flag)

#### Security

Guests never see bot tokens. The page is **public** if the URL is known. Do not publish photos you are not willing to share. If a Worker secret or bot token leaks: rotate the token in BotFather and update Worker Secrets. Details: [`docs/SECURITY.md`](docs/SECURITY.md).

### For the developer

#### Architecture

```text
Guest browser (GitHub Pages)
 → POST { guestName, turnstileToken? }
 → Cloudflare Worker (or local tools/server.py)
 → Telegram Bot API
 → organizer chat
```

No database. No app scheduler. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

#### Tech Stack

| Layer | Stack |
|-------|--------|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Hosting | GitHub Pages |
| Notify | Cloudflare Workers |
| Anti-bot | Cloudflare Turnstile (recommended in production) |
| Messaging | Telegram Bot API |
| Local | Python 3 (`tools/server.py`); Pillow optional for GIF |

#### Project Structure

```text
index.html
css/  js/  config.json
cloudflare-worker/worker.js
tools/                 server.py, get_chat_id.py, make_birthday_gif.py
docs/
assets/                your photos (not in git by default)
README.md
```

#### Installation

```powershell
cd c:\projects\Web_event
python tools/get_chat_id.py
python tools/server.py
```

Open http://127.0.0.1:8000. Local notify uses `config.json` → `"notifyUrl": "/api/notify"`. **GitHub Pages has no `/api/notify`** — before going live, set `notifyUrl` to the Worker HTTPS URL.

#### Environment

**Public** (`config.json`): `notifyUrl`, `telegramUsername`, `turnstileSiteKey`.

**Secrets** (Worker / local only — never commit values):

| Name | Purpose |
|------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot API token |
| `TELEGRAM_CHAT_ID` | Destination chat |
| `TURNSTILE_SECRET_KEY` | Turnstile verify (required on the production Worker) |
| `ALLOWED_ORIGINS` | CORS allowlist override |
| `HOST` / `PORT` | Local bind (default `127.0.0.1:8000`) |

#### Database

**None.** Guest name goes to Telegram only. Browser `localStorage` stores a sent-flag, not the name. [`docs/DATABASE.md`](docs/DATABASE.md).

#### Testing

No automated suite. Manual: open the page, submit RSVP, confirm Telegram, confirm Turnstile if enabled.

#### Deployment

1. GitHub Pages: `index.html` at repo root.
2. Deploy `cloudflare-worker/worker.js`; set Secrets.
3. Put Worker URL into `config.json` → `notifyUrl`.
4. Align CORS origin with Pages. [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

#### Security

Tokens only on the Worker. CORS allowlist, rate limit (~8 / IP / hour), Turnstile. Do not put secrets in HTML/JS/`config.json`. [`docs/SECURITY.md`](docs/SECURITY.md).

### For support

#### Troubleshooting

| Symptom | Checks |
|---------|--------|
| Button error, no Telegram | `notifyUrl`; Worker secrets; bot `/start` |
| 403 Origin | Pages origin vs `ALLOWED_ORIGINS` |
| 429 | Rate limit 8 / IP / hour |
| Turnstile failed | Site key vs `TURNSTILE_SECRET_KEY` |
| Form already sent | `localStorage` flag `babyBossInviteReceived` |

Full matrix: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

#### Backup

Git copy of `index.html`, `css/`, `js/`, `config.json` (public), `assets/`. Secrets live in Cloudflare Dashboard (not in git). RSVP history = organizer Telegram chat.

#### Recovery

Redeploy Pages + Worker. Recreate Secrets if rotated. Guest `localStorage` is not recoverable and is not required.

#### Maintenance

After each push, confirm Pages. After Worker code change, Deploy again. After the event: unpublish or remove personal photos. [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).

#### Warranty

**14 days after handover** for the documented Pages → Worker → Telegram path when CORS and secrets match this package. Not covered: GitHub/Cloudflare/Telegram outages, spam if Turnstile is off, third-party art, privacy impact of a public URL.

#### Security (incidents)

Leaked token: revoke in BotFather, update Worker Secret. Notify spam: enable Turnstile, tighten origins. [`docs/SECURITY.md`](docs/SECURITY.md).

---

<a id="русский"></a>

## Русский

### Для заказчика

#### Что это

**Веб-приглашение** на **GitHub Pages**: гость открывает ссылку, читает карточку, вводит имя и нажимает кнопку. Организатор получает сообщение в Telegram через **Cloudflare Worker**. Токен бота на странице не хранится. Репозиторий — **шаблон**: подставьте свои фото и текст.

Все часы в продукте — **московское время (MSK, UTC+3)**. Планировщика приложения нет; дата и время на странице — MSK (начало **19:30 MSK**).

#### Как пользоваться

1. Открыть Production URL: дата, **19:30 MSK**, текст, картинки.
2. Ссылку отправлять только гостям (сайт публичен по URL).
3. Гость вводит имя → Turnstile (production Worker) → сообщение вам в Telegram.
4. После события подумать: снять страницу или убрать личные фото.

#### Production URL

| Что | Значение |
|-----|----------|
| Приглашение | `https://kyratop.github.io/Web_event/` |
| Notify Worker | `[Cloudflare Worker HTTPS URL]` |

#### Основные функции

- Карточка приглашения под телефон
- Дата и время начала **MSK** (**19:30 MSK**)
- RSVP с именем гостя
- Уведомление организатору в Telegram
- Опциональный Cloudflare Turnstile
- Запасная ссылка в Telegram, если notify не сработал
- Повторная отправка с того же браузера блокируется (флаг `localStorage`)

#### Безопасность

Гости не видят токены бота. Страница **публичная**, если известен URL. Не публикуйте фото, которые нельзя светить. Утечка секрета Worker или токена: сменить токен в BotFather и обновить Worker Secrets. Подробнее: [`docs/SECURITY.md`](docs/SECURITY.md).

### Для разработчика

#### Architecture

```text
Браузер гостя (GitHub Pages)
 → POST { guestName, turnstileToken? }
 → Cloudflare Worker (или локальный tools/server.py)
 → Telegram Bot API
 → чат организатора
```

Базы нет. Планировщика приложения нет. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

#### Tech Stack

| Слой | Стек |
|------|------|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Хостинг | GitHub Pages |
| Notify | Cloudflare Workers |
| Anti-bot | Cloudflare Turnstile (на production рекомендуется) |
| Сообщения | Telegram Bot API |
| Локально | Python 3 (`tools/server.py`); Pillow опционально для GIF |

#### Project Structure

```text
index.html
css/  js/  config.json
cloudflare-worker/worker.js
tools/                 server.py, get_chat_id.py, make_birthday_gif.py
docs/
assets/                ваши фото (по умолчанию не в git)
README.md
```

#### Installation

```powershell
cd c:\projects\Web_event
python tools/get_chat_id.py
python tools/server.py
```

Открыть http://127.0.0.1:8000. Локальный notify: в `config.json` `"notifyUrl": "/api/notify"`. **У GitHub Pages нет `/api/notify`** — перед публикацией задайте `notifyUrl` как HTTPS URL Worker.

#### Environment

**Публично** (`config.json`): `notifyUrl`, `telegramUsername`, `turnstileSiteKey`.

**Секреты** (только Worker / локально — значения не коммитить):

| Имя | Назначение |
|-----|------------|
| `TELEGRAM_BOT_TOKEN` | Токен Bot API |
| `TELEGRAM_CHAT_ID` | Куда слать notify |
| `TURNSTILE_SECRET_KEY` | Проверка Turnstile (обязательно на production Worker) |
| `ALLOWED_ORIGINS` | Переопределение CORS allowlist |
| `HOST` / `PORT` | Локальный bind (по умолчанию `127.0.0.1:8000`) |

#### Database

**Нет.** Имя гостя уходит только в Telegram. В `localStorage` — флаг отправки, не имя. [`docs/DATABASE.md`](docs/DATABASE.md).

#### Testing

Автотестов нет. Вручную: открыть страницу, отправить RSVP, проверить Telegram, проверить Turnstile если включён.

#### Deployment

1. GitHub Pages: `index.html` в корне репозитория.
2. Задеплоить `cloudflare-worker/worker.js`; задать Secrets.
3. URL Worker → `config.json` → `notifyUrl`.
4. Согласовать CORS origin с Pages. [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

#### Security

Токены только на Worker. CORS allowlist, rate limit (~8 / IP / час), Turnstile. Секреты не класть в HTML/JS/`config.json`. [`docs/SECURITY.md`](docs/SECURITY.md).

### Для поддержки

#### Troubleshooting

| Симптом | Проверить |
|---------|-----------|
| Ошибка кнопки, нет Telegram | `notifyUrl`; секреты Worker; `/start` боту |
| 403 Origin | Origin Pages vs `ALLOWED_ORIGINS` |
| 429 | Rate limit 8 / IP / час |
| Turnstile failed | Site key vs `TURNSTILE_SECRET_KEY` |
| Форма уже отправлена | Флаг `localStorage` `babyBossInviteReceived` |

Полная матрица: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

#### Backup

Копия в git: `index.html`, `css/`, `js/`, `config.json` (публичный), `assets/`. Секреты — в Cloudflare Dashboard (не в git). История RSVP = чат Telegram организатора.

#### Recovery

Заново задеплоить Pages + Worker. Секреты создать снова, если ротировали. `localStorage` гостей не восстанавливается и не нужен.

#### Maintenance

После каждого push проверить Pages. После правки Worker — Deploy. После события: снять публикацию или убрать личные фото. [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).

#### Warranty

**14 дней после передачи** на задокументированный путь Pages → Worker → Telegram, если CORS и секреты соответствуют этому пакету. Не покрывается: сбои GitHub/Cloudflare/Telegram, спам при выключенном Turnstile, чужой character art, последствия публичного URL.

#### Безопасность (инциденты)

Утечка токена: revoke в BotFather, обновить Worker Secret. Спам notify: включить Turnstile, сузить origins. [`docs/SECURITY.md`](docs/SECURITY.md).

---

© All rights reserved.
