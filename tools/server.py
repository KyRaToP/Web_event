"""
Local web server for the Baby Boss invitation.

What it does:
1. Serves the static invitation page (HTML, CSS, images).
2. Handles POST /api/notify and sends a Telegram message via Bot API.

Security defaults:
- Binds to 127.0.0.1 (localhost only)
- Blocks serving .env and other sensitive files
- Soft in-memory rate limit for /api/notify
- Optional Cloudflare Turnstile verification

Required environment variables in .env:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
Optional:
- TURNSTILE_SECRET_KEY
- HOST (default 127.0.0.1)
- PORT (default 8000)
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
MAX_GUEST_NAME_LENGTH = 60
MAX_NOTIFY_BODY_BYTES = 4096
RATE_LIMIT_MAX = 8
RATE_LIMIT_WINDOW_SECONDS = 3600
BLOCKED_STATIC_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".gitignore",
}
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://kyratop.github.io",
}

_rate_limit_hits: dict[str, deque[float]] = defaultdict(deque)


def load_dotenv(path: Path) -> None:
    """Load key=value pairs from .env into process environment."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        value = value.encode("utf-8").decode("utf-8-sig").strip()
        value = "".join(ch for ch in value if ch.isprintable())
        os.environ[key] = value


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise RuntimeError(body.get("description") or "Telegram API error")


def verify_turnstile(token: str, secret: str, remote_ip: str) -> bool:
    payload = urllib.parse.urlencode(
        {
            "secret": secret,
            "response": token,
            "remoteip": remote_ip,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data=payload,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = json.loads(response.read().decode("utf-8"))
        return bool(body.get("success"))


def is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    hits = _rate_limit_hits[client_ip]
    while hits and now - hits[0] > RATE_LIMIT_WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= RATE_LIMIT_MAX:
        return True
    hits.append(now)
    return False


class InviteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _is_sensitive_path(self, path: str) -> bool:
        clean = urlparse(path).path
        name = Path(clean).name.lower()
        if name in BLOCKED_STATIC_NAMES:
            return True
        if name.startswith(".env"):
            return True
        return False

    def do_GET(self):
        if self._is_sensitive_path(self.path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_HEAD(self):
        if self._is_sensitive_path(self.path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        super().do_HEAD()

    def _cors_origin(self) -> str | None:
        origin = self.headers.get("Origin", "").strip()
        if origin in ALLOWED_ORIGINS:
            return origin
        return None

    def do_OPTIONS(self):
        if urlparse(self.path).path != "/api/notify":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        origin = self._cors_origin()
        if not origin:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/notify":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        client_ip = self.client_address[0] if self.client_address else "unknown"
        if is_rate_limited(client_ip):
            self._json_response(
                HTTPStatus.TOO_MANY_REQUESTS,
                {"ok": False, "error": "Слишком много запросов. Попробуйте позже."},
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "Некорректный Content-Length."},
            )
            return

        if length < 0 or length > MAX_NOTIFY_BODY_BYTES:
            self._json_response(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                {"ok": False, "error": "Слишком большое тело запроса."},
            )
            return

        raw_body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "Некорректный JSON."},
            )
            return

        guest_name = " ".join(str(data.get("guestName") or "").split())
        guest_name = "".join(
            ch for ch in guest_name if ch.isprintable()
        ).strip()[:MAX_GUEST_NAME_LENGTH]
        if not guest_name:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "Укажите имя гостя."},
            )
            return

        turnstile_secret = os.environ.get("TURNSTILE_SECRET_KEY", "").strip()
        if turnstile_secret:
            turnstile_token = str(data.get("turnstileToken") or "").strip()
            if not turnstile_token:
                self._json_response(
                    HTTPStatus.FORBIDDEN,
                    {
                        "ok": False,
                        "error": "Подтвердите, что вы не робот (Turnstile).",
                    },
                )
                return
            try:
                ok = verify_turnstile(turnstile_token, turnstile_secret, client_ip)
            except Exception:  # noqa: BLE001
                self._json_response(
                    HTTPStatus.BAD_GATEWAY,
                    {"ok": False, "error": "Не удалось проверить Turnstile."},
                )
                return
            if not ok:
                self._json_response(
                    HTTPStatus.FORBIDDEN,
                    {"ok": False, "error": "Проверка Turnstile не пройдена."},
                )
                return

        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        if not token or not chat_id:
            self._json_response(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {
                    "ok": False,
                    "error": "Telegram ещё не настроен. Добавьте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в .env",
                },
            )
            return

        message = (
            "Baby Boss Invite\n\n"
            f"Гость получил приглашение: {guest_name}\n"
            "Событие: 1 год Михаила"
        )

        try:
            send_telegram_message(token, chat_id, message)
        except urllib.error.HTTPError as error:
            error.read()
            self._json_response(
                HTTPStatus.BAD_GATEWAY,
                {
                    "ok": False,
                    "error": f"Telegram API вернул ошибку: {error.code}.",
                },
            )
            return
        except Exception:  # noqa: BLE001
            self._json_response(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "error": "Не удалось отправить уведомление в Telegram."},
            )
            return

        self._json_response(HTTPStatus.OK, {"ok": True})

    def _json_response(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"[server] {self.address_string()} - {format % args}")


def main() -> None:
    load_dotenv(ENV_PATH)
    server = ThreadingHTTPServer((HOST, PORT), InviteHandler)
    print(f"Invitation server: http://127.0.0.1:{PORT}")
    print(f"Bind address: {HOST}:{PORT}")
    print("Run from project root: python tools/server.py")
    print("Telegram notify endpoint: POST /api/notify")
    print("Sensitive files like .env are not served.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
