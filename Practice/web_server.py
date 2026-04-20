import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from infrastructure.user_store import UserStore
from src.generator import CodeGenerator


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


class AuthApi:
    """Simple in-memory 2FA API for the browser client."""

    def __init__(self, user_store: UserStore):
        self.user_store = user_store
        self.generator = CodeGenerator()
        self.codes: dict[str, dict[str, Any]] = {}
        self.max_attempts = 3

    def register(self, email: str, password: str) -> dict[str, Any]:
        return self.user_store.register_user(email, password)

    def login(self, email: str, password: str) -> dict[str, Any]:
        if not self.user_store.verify_user(email, password):
            return {"success": False, "message": "Неверный email или пароль"}

        code, expiry = self.generator.generate_with_expiry()
        self.codes[email] = {"code": code, "expiry": expiry, "attempts": 0}

        # В демо-режиме возвращаем код в ответе, потому что SMTP может быть не настроен.
        return {
            "success": True,
            "message": "Код подтверждения сгенерирован",
            "expires_at": expiry.isoformat(),
            "debug_code": code,
        }

    def verify_code(self, email: str, code: str) -> dict[str, Any]:
        if email not in self.codes:
            return {"success": False, "message": "Сначала выполните вход"}

        data = self.codes[email]
        if datetime.now() > data["expiry"]:
            del self.codes[email]
            return {"success": False, "message": "Срок действия кода истек"}

        if data["attempts"] >= self.max_attempts:
            del self.codes[email]
            return {"success": False, "message": "Превышено число попыток"}

        if code.strip().upper() != data["code"]:
            data["attempts"] += 1
            attempts_left = max(0, self.max_attempts - data["attempts"])
            return {
                "success": False,
                "message": f"Неверный код. Осталось попыток: {attempts_left}",
            }

        del self.codes[email]
        self.user_store.set_verified(email, True)
        return {"success": True, "message": "Авторизация успешно завершена"}


class WebHandler(BaseHTTPRequestHandler):
    auth_api = AuthApi(UserStore(str(BASE_DIR / "users.json")))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "Not found")
            return

        content_type = "text/plain; charset=utf-8"
        if path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        elif path.suffix == ".css":
            content_type = "text/css; charset=utf-8"

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict[str, Any]:
        content_len = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_file(WEB_DIR / "index.html")
            return
        if path == "/app.js":
            self._send_file(WEB_DIR / "app.js")
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        payload = self._read_json_body()
        email = str(payload.get("email", "")).strip().lower()

        if path == "/api/register":
            password = str(payload.get("password", ""))
            result = self.auth_api.register(email, password)
            self._send_json(200, result)
            return

        if path == "/api/login":
            password = str(payload.get("password", ""))
            result = self.auth_api.login(email, password)
            self._send_json(200, result)
            return

        if path == "/api/verify":
            code = str(payload.get("code", ""))
            result = self.auth_api.verify_code(email, code)
            self._send_json(200, result)
            return

        self._send_json(404, {"success": False, "message": "Маршрут не найден"})


def run_server(port: int = 8000) -> None:
    httpd = HTTPServer(("127.0.0.1", port), WebHandler)
    print(f"Web auth module running at http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
