# Baby Boss — веб-приглашение на 1 год

Персональное web invitation (веб-приглашение) в стиле Baby Boss на день рождения Михаила.

**Live demo:** [https://kyratop.github.io/Web_event/](https://kyratop.github.io/Web_event/)

Статический сайт на **GitHub Pages** + **Cloudflare Worker**, который шлёт уведомление в **Telegram** через Bot API, когда гость подтверждает получение приглашения (RSVP).

---

## Что внутри

- Красивая карточка-приглашение (`index.html` + `css/style.css`)
- Анимированное фото именинника (`assets/birthday-person.gif`)
- Форма RSVP: гость вводит имя → `POST` на Worker → сообщение организатору в Telegram
- Локальный dev-server с тем же notify endpoint (`tools/server.py`)

---

## Как это работает для гостей

1. Открывают ссылку на GitHub Pages.
2. Читают приглашение (дата, время, адрес).
3. Вводят имя и нажимают **«Я получил приглашение»**.
4. Браузер вызывает `notifyUrl` из `config.json` (Cloudflare Worker).
5. Worker отправляет сообщение в ваш Telegram chat через Bot API.
6. В браузере сохраняется флаг в `localStorage`, чтобы случайно не слать повторно.

Секреты бота **никогда** не попадают во frontend — только на Worker / в локальный `.env`.

---

## Структура проекта

```text
Web_event/
├── index.html                 # Страница приглашения
├── config.json                # notifyUrl (публичный Worker URL)
├── .env.example               # Шаблон переменных (без секретов)
├── assets/
│   ├── design.jpg             # Оформление / фон карточки
│   ├── birthday-person.jpg    # Исходное фото
│   └── birthday-person.gif    # Анимация для страницы
├── css/
│   └── style.css
├── js/
│   └── script.js              # RSVP + fetch config/notify
├── content/
│   └── text_pozdravleniya.txt # Текст приглашения (черновик)
├── cloudflare-worker/
│   └── worker.js              # Telegram notify API
├── tools/
│   ├── server.py              # Локальный static + POST /api/notify
│   ├── get_chat_id.py         # Узнать TELEGRAM_CHAT_ID
│   └── make_birthday_gif.py   # Собрать GIF из JPG (нужен Pillow)
└── docs/
    ├── SECURITY_AND_LEGAL.md
    └── BUGS.md
```

---

## Локальный запуск

Требуется Python 3.

1. Скопируйте `.env.example` → `.env` и заполните вручную:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
2. (Опционально) Узнайте chat id:

```bash
python tools/get_chat_id.py
```

Сначала напишите боту `/start` в Telegram.

3. Запустите сервер из корня репозитория:

```bash
python tools/server.py
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Важно:** текущий `config.json` указывает на production Worker. Чтобы тестировать локальный `/api/notify`, временно поставьте:

```json
{
  "notifyUrl": "https://YOUR-WORKER.workers.dev",
  "telegramUsername": "",
  "turnstileSiteKey": "YOUR_TURNSTILE_SITE_KEY"
}
```

Не коммитьте `.env`. Не публикуйте значения token / chat id / Turnstile secret.

---

## Deploy

### 1) GitHub Pages

1. Push репозитория на GitHub.
2. Settings → Pages → Source: ветка с `index.html` в корне (или docs/ — у этого проекта корень).
3. Сайт будет доступен примерно как:  
   `https://<user>.github.io/Web_event/`

### 2) Cloudflare Worker

1. Создайте Worker и вставьте код из `cloudflare-worker/worker.js`.
2. В Cloudflare Dashboard → Worker → Settings → Variables / Secrets добавьте:
   - `TELEGRAM_BOT_TOKEN` — secret
   - `TELEGRAM_CHAT_ID` — secret
   - `TURNSTILE_SECRET_KEY` — secret (рекомендуется)
3. Deploy Worker и скопируйте его URL.
4. Создайте виджет **Turnstile** в Cloudflare Dashboard → Turnstile:
   - Hostnames: `kyratop.github.io` (и при тесте `localhost`)
   - Скопируйте **Site Key** и **Secret Key**
5. Secret Key → Worker secret `TURNSTILE_SECRET_KEY`  
   Site Key → `config.json` → `turnstileSiteKey`
6. Пропишите URL Worker в `config.json`:

```json
{
  "notifyUrl": "https://YOUR-WORKER.workers.dev",
  "telegramUsername": "",
  "turnstileSiteKey": "YOUR_TURNSTILE_SITE_KEY"
}
```

7. Закоммитьте обновлённый `config.json` (без секретов) и дождитесь обновления Pages.  
8. **Важно:** заново Deploy Worker с новым `worker.js` (CORS allowlist, rate limit, Turnstile).

Опционально: `telegramUsername` (без `@`) включает deep-link fallback в Telegram, если API notify недоступен.  
Опционально: Worker secret/var `ALLOWED_ORIGINS` — список Origin через запятую (по умолчанию Pages + localhost).

---

## Config

| Поле | Назначение |
|------|------------|
| `notifyUrl` | URL Worker или `/api/notify` локально |
| `telegramUsername` | Fallback `t.me/<user>?text=...` (может быть пустым) |
| `turnstileSiteKey` | Публичный Site Key Cloudflare Turnstile (secret — только на Worker) |

---

## Environment

Шаблон: `.env.example`

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TURNSTILE_SECRET_KEY=
```

Используется только локальными скриптами (`tools/server.py`, `tools/get_chat_id.py`).  
На production те же имена — как **Worker secrets**, не как файл в репозитории.

---

## Security (кратко)

- **Не** кладите bot token в HTML/JS/`config.json`.
- Frontend вызывает только публичный notify URL.
- Worker: CORS allowlist, soft **rate limit**, опционально **Turnstile**.
- Локальный `server.py` по умолчанию на `127.0.0.1` и **не** отдаёт `.env`.
- Подробный разбор: [`docs/SECURITY_AND_LEGAL.md`](docs/SECURITY_AND_LEGAL.md).
- Известные баги / edge cases: [`docs/BUGS.md`](docs/BUGS.md).

---

## Legal / disclaimer

Это **личное / fan** приглашение. Оформление в духе Baby Boss и связанные изображения **не** означают официальную связь с DreamWorks или правообладателями франшизы. Использование character art — на свой риск, для некоммерческого личного события.

На сайте есть **личное фото ребёнка**. Публикуйте ссылку осознанно и только для круга гостей. Документы в `docs/` носят информационный характер и **не** являются юридической консультацией.

---

## Лицензия кода

Код репозитория можно использовать как основу для своего личного приглашения. Сторонние шрифты (Google Fonts), чужие trademark / character art и личные фото подчиняются отдельным правилам правообладателей и privacy.
