# Database

**Language:** [English](#english) · [Русский](#русский)

<a id="english"></a>

## Engine

**None.** Production stores no RSVP rows. There is no SQLite, no Postgres, no app scheduler.

## Where data lives

| Data | Location |
|------|----------|
| Invitation copy, photos | Git / GitHub Pages (public) |
| Guest name | Telegram message to the organizer only |
| Sent flag | Browser `localStorage` key `babyBossInviteReceived` = `1` |
| Secrets | Cloudflare Worker Secrets / local environment (not git) |

## Backup implication

Backup = git repo + Telegram chat export if you need an RSVP archive. Clearing `localStorage` lets the same browser submit again (rate limit still applies).

---

<a id="русский"></a>

## Engine

**Нет.** Production не хранит строки RSVP. Нет SQLite, Postgres и планировщика приложения.

## Where data lives

| Data | Location |
|------|----------|
| Текст и фото приглашения | Git / GitHub Pages (публично) |
| Имя гостя | Только сообщение Telegram организатору |
| Флаг отправки | Браузерный `localStorage` ключ `babyBossInviteReceived` = `1` |
| Секреты | Cloudflare Worker Secrets / локальное окружение (не git) |

## Backup implication

Backup = git-репозиторий + export чата Telegram, если нужен архив RSVP. Очистка `localStorage` позволяет той же браузерной сессии отправить форму снова (rate limit всё равно действует).
