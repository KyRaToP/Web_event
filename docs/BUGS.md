# Bugs и замечания — Baby Boss invite

Анализ HTML/CSS/JS, Cloudflare Worker, `tools/server.py` и путей после структуры `assets/`, `css/`, `js/`, `tools/`, `cloudflare-worker/`, `content/`.

Легенда severity:
- **Critical** — ломает основной сценарий
- **High** — заметный функциональный / security-adjacent дефект
- **Medium** — edge case, UX, локальная разработка
- **Low** — polish, документация, косметика
- **Suggestion** — улучшение, не баг

---

## Проверка путей (index.html ↔ файлы)

| Ссылка в коде | Файл | Статус |
|---------------|------|--------|
| `css/style.css` | `css/style.css` | OK |
| `js/script.js` | `js/script.js` | OK |
| `assets/design.jpg` | `assets/design.jpg` | OK |
| `assets/birthday-person.gif` | `assets/birthday-person.gif` | OK |
| `config.json` (fetch) | `config.json` | OK |
| Google Fonts Nunito / Unbounded | CDN | OK (есть system-ui fallback) |

`ROOT` в `tools/server.py` = parent of `tools/` → корень репозитория — корректно для `python tools/server.py`.

Сломанных путей после restructure **не найдено**.

---

## Исправлено

### 1. [High] Telegram fallback записывал успех в `localStorage` без реальной доставки

**Было:** при ошибке Worker/API, если задан `telegramUsername`, открывался `t.me/...`, форма блокировалась как «уже отправлено», даже если гость не нажал Send.

**Стало** (`js/script.js`): fallback больше не пишет `localStorage` и не вызывает `markAsSent()`; кнопка остаётся активной для повторной попытки.

### 2. [High] `og:image` с относительным URL

**Было:** `content="assets/design.jpg"` — многие crawler'ы (Telegram/VK/Facebook) не резолвят relative path → битый preview.

**Стало** (`index.html`): абсолютный URL  
`https://kyratop.github.io/Web_event/assets/design.jpg`.

### 3. [Medium] Нет лимита / нормализации `guestName` на сервере

**Было:** клиент ограничивал 60 символов; Worker и `server.py` принимали произвольную строку (длинный payload, control chars в Telegram).

**Стало:**
- `cloudflare-worker/worker.js` — `normalizeGuestName`, max 60;
- `tools/server.py` — printable + max 60, лимит тела запроса 4 KB, безопасный разбор `Content-Length`.

### 4. [Medium] Утечка деталей Telegram API в ответ локального server

**Было:** тело ошибки Telegram пробрасывалось в JSON клиенту.

**Стало:** только код/общее сообщение (`tools/server.py`).

### 5. [Low] Неверный путь в docstring `get_chat_id.py`

**Было:** `python get_chat_id.py`.  
**Стало:** `python tools/get_chat_id.py` (из корня проекта).

---

## Найденные проблемы (ещё открыты)

### [High] Открытый notify endpoint без rate limit

Worker принимает POST с любого клиента (`CORS *`). Можно спамить Telegram чат.

**Suggestion:** Cloudflare Rate Limiting, Turnstile, или временное отключение Worker после события.

Подробнее: `docs/SECURITY_AND_LEGAL.md`.

### [Medium] Local RSVP не бьёт в `/api/notify` при текущем `config.json`

`js/script.js` по умолчанию использует `/api/notify`, но `config.json` перезаписывает `notifyUrl` на production Worker.

Итог: `python tools/server.py` + локальный `.env` **не** используются фронтендом, пока в `config.json` указан Worker.

**Suggestion:** для локальных тестов временно поставить `"notifyUrl": "/api/notify"` или завести некоммитимый override (не реализовано).

### [Medium] `telegramUsername` пустой — fallback фактически выключен

При недоступности Worker гость видит только ошибку сети (после фикса fallback без username).

**Suggestion:** либо заполнить username организатора, либо явно описать гостям альтернативный контакт.

### [Medium] Локальный server может отдать `.env` как static file

`SimpleHTTPRequestHandler` раздаёт весь `ROOT`. Запрос к `/.env` на `0.0.0.0` в чужой сети — риск.

**Suggestion:** bind `HOST=127.0.0.1`; запретить path `.env` в handler.

### [Medium] Mobile: `object-fit: fill` для рамки

На узких экранах `design.jpg` растягивается (`css/style.css`), возможны искажения пропорций.

**Suggestion:** `object-fit: cover` + проверка кадрирования на реальных телефонах.

### [Low] Landscape phone layout

В landscape invite сужается (`max-width` media); длинный текст + RSVP требуют scroll — приемлемо, но тесно.

### [Low] Кнопка после успеха: `cursor: wait` у `:disabled`

Визуально выглядит как «ещё грузится», хотя RSVP уже завершён.

**Suggestion:** отдельный класс `.is-done` с `cursor: default`.

### [Low] Нет `favicon`

Мелочь для вкладки браузера.

### [Low] `content/text_pozdravleniya.txt` не подключён к сайту

Дублирует текст приглашения для редактирования; рассинхрон с `index.html` возможен вручную — не runtime-баг.

### [Suggestion] Нет явного consent-текста у RSVP

Имя уходит в Telegram без пояснения на UI.

### [Suggestion] После праздника оставить публичные фото/адрес

Privacy: подумать о снятии Pages / замене фото.

### [Suggestion] Worker не проверяет Origin allowlist

Слабая защита, но снижает случайный browser abuse с чужих сайтов.

---

## Worker error handling (обзор)

| Сценарий | Поведение | Оценка |
|----------|-----------|--------|
| Не-POST | 405 + JSON | OK |
| Битый JSON | 400 | OK |
| Пустое имя | 400 | OK |
| Нет secrets | 503 | OK |
| Сеть к Telegram | 502 | OK |
| Telegram API fail | 502 + `description` | OK; description может быть verbose |
| Успех | `{ ok: true }` | OK |

Frontend корректно читает `data.ok` / `data.error`.

---

## RSVP / localStorage edge cases

| Сценарий | Поведение |
|----------|-----------|
| Успешный notify | `localStorage` = `1`, кнопка disabled |
| Reload после успеха | Сразу «уже отправлено» |
| Очистка site data | Можно отправить снова |
| Имя не сохраняется | Только флаг — OK |
| Fallback Telegram (если username задан) | Больше не блокирует навсегда (исправлено) |
| Два устройства одного гостя | Два уведомления — ожидаемо |

---

## Шрифты

Подключение Google Fonts в `index.html` корректно. При блокировке CDN страница остаётся читаемой за счёт `system-ui`.

---

## Итог

Критических поломок путей/сборки нет. Главные открытые риски: **spam notify** и **local config vs Worker URL**. Исправления выше — быстрые, high-confidence.
