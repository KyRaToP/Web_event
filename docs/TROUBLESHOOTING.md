# Troubleshooting

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Matrix

| Symptom | Checks |
|---------|--------|
| Button error, no Telegram | `config.json` `notifyUrl`; Worker secrets; bot `/start` |
| 403 Origin not allowed | Pages origin in `ALLOWED_ORIGINS` / `DEFAULT_ALLOWED_ORIGINS` |
| 429 | 8 / IP / hour — wait or another network |
| Turnstile failed | Site key vs `TURNSTILE_SECRET_KEY`; widget hostname |
| 503 Telegram secrets | `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` on Worker |
| 502 Telegram API | Token revoked; wrong chat id; Bot API outage |
| Form already sent | Clear `localStorage` flag `babyBossInviteReceived` |
| Missing images | `assets/design.jpg`, `assets/birthday-person.gif` |
| Fallback Telegram window | Set `telegramUsername` without `@` |

Do not print secret **values**.

---

<a id="русский"></a>

## Matrix

| Symptom | Checks |
|---------|--------|
| Ошибка кнопки, нет Telegram | `config.json` `notifyUrl`; секреты Worker; `/start` боту |
| 403 Origin not allowed | Origin Pages в `ALLOWED_ORIGINS` / `DEFAULT_ALLOWED_ORIGINS` |
| 429 | 8 / IP / час — подождать или другая сеть |
| Turnstile failed | Site key vs `TURNSTILE_SECRET_KEY`; hostname виджета |
| 503 Telegram secrets | `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` на Worker |
| 502 Telegram API | Токен отозван; неверный chat id; сбой Bot API |
| Форма уже отправлена | Очистить флаг `localStorage` `babyBossInviteReceived` |
| Нет картинок | `assets/design.jpg`, `assets/birthday-person.gif` |
| Окно fallback Telegram | Задать `telegramUsername` без `@` |

Не печатать секретные **значения**.
