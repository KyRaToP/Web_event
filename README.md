# Web invitation (Telegram RSVP)

Шаблон **web invitation** (веб-приглашения) со статическим сайтом на **GitHub Pages** и уведомлениями в **Telegram** через **Cloudflare Worker** (Bot API).

Гость открывает страницу, читает текст, вводит имя и нажимает кнопку — организатор получает сообщение в Telegram.

Секреты бота **никогда** не кладите в frontend — только в Worker Secrets / локальный `.env`.

---

## Быстрый старт (что положить и куда)

### 1) Изображения → папка `assets/`

Положите **свои** файлы с **точными именами** (на них ссылается `index.html`):

| Файл | Назначение |
|------|------------|
| `assets/design.jpg` | Фон / рамка карточки приглашения |
| `assets/birthday-person.gif` | Анимация / фото именинника на странице |
| `assets/birthday-person.jpg` | (Опционально) исходник для сборки GIF |

Пример:

```text
assets/
├── design.jpg              ← обязательно
├── birthday-person.gif     ← обязательно для фото на сайте
└── birthday-person.jpg     ← опционально, если собираете GIF сами
```

Собрать GIF из JPG (нужен Pillow):

```bash
python tools/make_birthday_gif.py
```

Скрипт читает `assets/birthday-person.jpg` и пишет `assets/birthday-person.gif`.

> Личные фото **не** рекомендуется коммитить в public-репозиторий. Держите их локально или в private repo.

### 2) Текст приглашения

- Черновик / исходник: `content/text_pozdravleniya.txt`
- Текст на сайте редактируйте в `index.html` (блок `.invite-body`)

### 3) Конфиг → `config.json`

Скопируйте структуру и подставьте **свои** значения:

```json
{
  "notifyUrl": "https://YOUR-WORKER.workers.dev",
  "telegramUsername": "",
  "turnstileSiteKey": "YOUR_TURNSTILE_SITE_KEY"
}
```

| Поле | Куда взять / что поставить |
|------|----------------------------|
| `notifyUrl` | URL вашего Cloudflare Worker после Deploy. Для локального теста API: `"/api/notify"` |
| `telegramUsername` | Опционально: ваш Telegram username **без** `@` (fallback deep-link). Можно `""` |
| `turnstileSiteKey` | **Site Key** из Cloudflare Turnstile (публичный). Secret — только на Worker |

### 4) Секреты → `.env` (локально) и Worker Secrets (production)

Скопируйте `.env.example` → `.env` (файл `.env` **не** коммитьте):

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TURNSTILE_SECRET_KEY=
```

| Переменная | Где взять | Куда на production |
|------------|-----------|--------------------|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) → `/newbot` | Worker → Secrets |
| `TELEGRAM_CHAT_ID` | Напишите боту `/start`, затем `python tools/get_chat_id.py` | Worker → Secrets |
| `TURNSTILE_SECRET_KEY` | Cloudflare → Turnstile → виджет → **Secret Key** | Worker → Secrets |

---

## Структура проекта

```text
./
├── index.html                 # Страница приглашения (правьте текст здесь)
├── config.json                # notifyUrl, turnstileSiteKey (без секретов)
├── .env.example               # Шаблон переменных
├── assets/                    # ВАШИ изображения (см. таблицу выше)
├── css/style.css
├── js/script.js               # RSVP + Turnstile + notify
├── content/                   # Текстовые черновики
├── cloudflare-worker/worker.js
├── tools/
│   ├── server.py              # Локальный static + POST /api/notify
│   ├── get_chat_id.py
│   └── make_birthday_gif.py
└── docs/
    ├── SECURITY_AND_LEGAL.md
    └── BUGS.md
```

---

## Локальный запуск

Нужен Python 3.

1. Положите изображения в `assets/` (см. выше).
2. Заполните `.env` и при необходимости `config.json` (`notifyUrl`: `"/api/notify"` для локального API).
3. Напишите боту `/start`, при необходимости:

```bash
python tools/get_chat_id.py
```

4. Из корня репозитория:

```bash
python tools/server.py
```

5. Откройте http://127.0.0.1:8000

Сервер по умолчанию слушает только `127.0.0.1` и не отдаёт `.env`.

---

## Deploy (чтобы заработало у вас)

### A) GitHub Pages

1. Запушьте репозиторий на GitHub.
2. Settings → Pages → Source: ветка с `index.html` **в корне** репозитория.
3. Сайт будет вида: `https://<ваш-username>.github.io/<имя-репо>/`

### B) Cloudflare Worker

1. Workers & Pages → Create → Start with Hello World (или свой Worker).
2. Вставьте код из `cloudflare-worker/worker.js` → Deploy.
3. Settings → Variables / Secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TURNSTILE_SECRET_KEY` (рекомендуется)
4. (Опционально) `ALLOWED_ORIGINS` — список Origin через запятую.  
   По умолчанию в коде: ваш GitHub Pages origin + localhost.  
   **Обязательно** поправьте origin в `worker.js` (`DEFAULT_ALLOWED_ORIGINS`) или задайте `ALLOWED_ORIGINS` под свой `https://<user>.github.io`.
5. Скопируйте URL Worker → `config.json` → `notifyUrl`.

### C) Cloudflare Turnstile

1. Dashboard → Turnstile → **Add widget manually**.
2. Hostname: ваш `*.github.io` (и `localhost` для теста).
3. **Site Key** → `config.json` → `turnstileSiteKey`.
4. **Secret Key** → Worker Secret `TURNSTILE_SECRET_KEY` (не в Git).
5. Снова Deploy Worker, если меняли код.

### D) Закоммитьте публичный конфиг

Закоммитьте `config.json` с вашим `notifyUrl` и `turnstileSiteKey` (без секретов) и дождитесь обновления Pages.

---

## Чеклист «всё заработало»

- [ ] В `assets/` есть `design.jpg` и `birthday-person.gif`
- [ ] Текст в `index.html` свой
- [ ] Бот создан, `/start` нажат, `TELEGRAM_CHAT_ID` известен
- [ ] Secrets на Worker заполнены
- [ ] Worker Deploy с актуальным `worker.js`
- [ ] `config.json`: правильный `notifyUrl` и (желательно) `turnstileSiteKey`
- [ ] CORS / `ALLOWED_ORIGINS` совпадает с вашим GitHub Pages origin
- [ ] Pages включён, сайт открывается, кнопка шлёт сообщение в Telegram

---

## Security (кратко)

- Не кладите bot token / Turnstile secret в HTML, JS или `config.json`.
- Frontend вызывает только публичный notify URL.
- Worker: CORS allowlist, soft rate limit, опционально Turnstile.
- Подробнее: [`docs/SECURITY_AND_LEGAL.md`](docs/SECURITY_AND_LEGAL.md), [`docs/BUGS.md`](docs/BUGS.md).

---

## Legal / disclaimer

Шаблон для **личного** некоммерческого приглашения. Если используете чужой character art / trademark — это на ваш риск и не означает аффилиации с правообладателями. Личные фото публикуйте осознанно (лучше private repo или без коммита в Git). Документы в `docs/` — информационные, не юридическая консультация.

---

## Лицензия кода

Код можно использовать как основу своего приглашения. Шрифты (Google Fonts), чужие изображения и персональные данные регулируются отдельно.
