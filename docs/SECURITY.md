# Security

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Model

Public static page + Worker notify. **Secrets stay on the Worker** (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TURNSTILE_SECRET_KEY`). Frontend and `config.json` must not contain tokens.

## Controls

| Control | Behavior |
|---------|----------|
| CORS allowlist | Default Pages origin `https://kyratop.github.io` + localhost `:8000`; override `ALLOWED_ORIGINS` |
| Rate limit | 8 / IP / 3600s (Worker Cache API; in-memory locally) |
| Turnstile | If secret set, token required; recommended in production |
| Guest name | Strip controls, max 60; shown via `textContent` (not `innerHTML`) |
| Local server | Default bind `127.0.0.1`; does not serve sensitive env filenames |
| Telegram errors | Client does not receive raw Telegram error bodies |

## Public page (privacy)

GitHub Pages is **world-readable**. Anything you put on the invitation (photos, names, venue, date/time) is visible to anyone with the URL. “Private party” is social (who you send the link to), not a network ACL.

Practical steps: share the link only with guests; prefer a private repo or keep original photos off public git; after the event, unpublish or strip personal media. Guest **name** is personal data sent to the organizer’s Telegram; the form states that tapping the button notifies the organizer. Minimize how long you keep those chats.

Third-party character art / trademarks: personal non-commercial template use is not affiliation and is not a license. This is **not legal advice**.

## Incidents

| Event | Action |
|-------|--------|
| Leaked bot token | Revoke in BotFather; new Worker secret |
| Notify spam | Enable Turnstile; tighten origins; Cloudflare rate limiting / WAF |
| Unwanted public media | Remove assets, commit, wait for Pages |
| Wrong Worker URL in `config.json` | Point `notifyUrl` at your Worker; redeploy Pages |

## Warranty

**14 days after handover.**

---

<a id="русский"></a>

## Model

Публичная статика + notify на Worker. **Секреты только на Worker** (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TURNSTILE_SECRET_KEY`). В frontend и `config.json` токенов быть не должно.

## Controls

| Control | Behavior |
|---------|----------|
| CORS allowlist | По умолчанию origin Pages `https://kyratop.github.io` + localhost `:8000`; переопределение `ALLOWED_ORIGINS` |
| Rate limit | 8 / IP / 3600с (Cache API Worker; локально in-memory) |
| Turnstile | Если задан secret — нужен token; на production рекомендуется |
| Имя гостя | Убрать control-символы, макс. 60; вывод через `textContent` (не `innerHTML`) |
| Локальный сервер | Bind по умолчанию `127.0.0.1`; не отдаёт чувствительные env-имена |
| Ошибки Telegram | Клиенту не отдаётся сырое тело ошибки Telegram |

## Public page (privacy)

GitHub Pages **читается кем угодно**. Всё, что вы положите в приглашение (фото, имена, площадка, дата/время), видно по URL. «Закрытая вечеринка» — социальная (кому отправили ссылку), не сетевой ACL.

Практика: ссылку только гостям; лучше private repo или не класть исходные фото в public git; после события снять публикацию или убрать личные медиа. **Имя** гостя — персональные данные в Telegram организатора; на форме сказано, что кнопка уведомляет организатора. Не храните эти чаты дольше нужного.

Чужой character art / trademark: личное некоммерческое использование шаблона — не аффилиация и не лицензия. Это **не юридическая консультация**.

## Incidents

| Event | Action |
|-------|--------|
| Утечка токена бота | Revoke в BotFather; новый Worker secret |
| Спам notify | Включить Turnstile; сузить origins; rate limiting / WAF Cloudflare |
| Нежелательные публичные медиа | Убрать assets, commit, дождаться Pages |
| Неверный URL Worker в `config.json` | `notifyUrl` на ваш Worker; пересобрать Pages |

## Warranty

**14 дней после передачи.**
