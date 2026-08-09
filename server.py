"""
Local web server for the Baby Boss invitation.

What it does:
1. Serves the static invitation page (HTML, CSS, images, fonts).
2. Handles POST /api/notify and sends a Telegram message via Bot API.

Required environment variables in .env:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


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


class InviteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        if urlparse(self.path).path != "/api/notify":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/notify":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            data = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "Некорректный JSON."},
            )
            return

        guest_name = str(data.get("guestName") or "").strip()
        if not guest_name:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": "Укажите имя гостя."},
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
            details = error.read().decode("utf-8", errors="ignore")
            self._json_response(
                HTTPStatus.BAD_GATEWAY,
                {
                    "ok": False,
                    "error": f"Telegram API вернул ошибку: {error.code}. {details}",
                },
            )
            return
        except Exception as error:  # noqa: BLE001 - return readable API error
            self._json_response(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "error": str(error)},
            )
            return

        self._json_response(HTTPStatus.OK, {"ok": True})

    def _json_response(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"[server] {self.address_string()} - {format % args}")


def main() -> None:
    load_dotenv(ENV_PATH)
    server = ThreadingHTTPServer((HOST, PORT), InviteHandler)
    print(f"Invitation server: http://127.0.0.1:{PORT}")
    print("Telegram notify endpoint: POST /api/notify")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
