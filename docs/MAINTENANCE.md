# Maintenance

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Routine

| Task | Cadence |
|------|---------|
| Confirm Pages URL opens | After each git push |
| Confirm Worker Deploy matches `worker.js` | After code change |
| Confirm Turnstile hostnames | If domain changes |
| Rotate bot token if leaked | Immediately |
| After the event | Unpublish Pages or remove personal photos |

## Secrets

Re-enter Worker Secrets in Cloudflare Dashboard only. Never commit values. `config.json` may hold `notifyUrl` and site key only.

## Warranty

**14 days after handover** for the documented Pages → Worker → Telegram path when CORS and secrets match this package.

---

<a id="русский"></a>

## Routine

| Task | Cadence |
|------|---------|
| URL Pages открывается | После каждого git push |
| Deploy Worker совпадает с `worker.js` | После изменения кода |
| Hostnames Turnstile | Если сменился домен |
| Ротация токена бота при утечке | Сразу |
| После события | Снять Pages или убрать личные фото |

## Secrets

Секреты Worker вводить только в Cloudflare Dashboard. Значения не коммитить. В `config.json` можно держать только `notifyUrl` и site key.

## Warranty

**14 дней после передачи** на задокументированный путь Pages → Worker → Telegram, если CORS и секреты соответствуют этому пакету.
