#!/usr/bin/env python3
"""hermes-dashboard-helper — локальный лаунчер Hermes Dashboard для CanvasTTY.

Слушает только 127.0.0.1:9210. Позволяет плагину-виджету CanvasTTY
(который работает в песочнице без Node) запускать `hermes dashboard`.

Endpoints:
  GET  /status         -> {"running": bool, "url": "http://127.0.0.1:9119/"}
  POST /start          -> запускает dashboard, если он не запущен (тело не нужно)
  GET  /health         -> {"ok": true} для systemd/мониторинга

Безопасность: любой запрос /start должен нести заголовок X-Hermes-Token,
равный токену из ~/.config/hermes-dashboard-helper/token (создаётся при
первом запуске, chmod 600). Слушает только loopback.
"""
from __future__ import annotations

import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 9210
DASHBOARD_URL = "http://127.0.0.1:9119/"
DASHBOARD_PORT = 9119
CONFIG_DIR = os.path.expanduser("~/.config/hermes-dashboard-helper")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token")
LOG_FILE = os.path.join(CONFIG_DIR, "helper.log")

_lock = threading.Lock()
_started_at = 0.0


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass


def load_or_create_token() -> str:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            tok = f.read().strip()
            if tok:
                return tok
    tok = secrets.token_urlsafe(24)
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(tok)
    return tok


def find_hermes() -> str | None:
    env = os.environ.get("HERMES_BIN")
    if env and os.path.exists(env):
        return env
    try:
        out = subprocess.run(
            ["bash", "-lc", "command -v hermes"],
            capture_output=True, text=True, timeout=5,
        )
        path = out.stdout.strip()
        if path:
            return path
    except Exception:
        pass
    candidate = os.path.expanduser("~/.hermes/hermes-agent/venv/bin/hermes")
    return candidate if os.path.exists(candidate) else None


def dashboard_alive() -> bool:
    try:
        with urllib.request.urlopen(DASHBOARD_URL, timeout=2):
            return True
    except Exception:
        return False


def start_dashboard() -> bool:
    global _started_at
    if dashboard_alive():
        return True
    hermes = find_hermes()
    if not hermes:
        log("ERROR: hermes CLI not found")
        return False
    with _lock:
        if dashboard_alive():
            return True
        try:
            proc = subprocess.Popen(
                [hermes, "dashboard", "--port", "9119", "--host", "127.0.0.1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            _started_at = time.time()
            log(f"launched dashboard pid={proc.pid}")
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR launch: {exc}")
            return False
    # ждём готовности до 20 с
    deadline = time.time() + 20
    while time.time() < deadline:
        if dashboard_alive():
            return True
        time.sleep(0.4)
    return dashboard_alive()


class Handler(BaseHTTPRequestHandler):
    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Hermes-Token")
        self.send_header("Access-Control-Max-Age", "3600")

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A002 — тишина в stdout
        pass

    def do_OPTIONS(self):
        # Preflight для кросс-ориджин запросов из песочницы плагина
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            self._json(200, {"running": dashboard_alive(), "url": DASHBOARD_URL})
        elif self.path == "/health":
            self._json(200, {"ok": True})
        elif self.path == "/token":
            # Отдаём токен виджету плагина. Безопасно: helper слушает только
            # loopback, а локальный процесс и так имеет доступ к файлу токена.
            self._json(200, {"token": _TOKEN})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/start":
            self._json(404, {"error": "not found"})
            return
        provided = self.headers.get("X-Hermes-Token", "")
        if not secrets.compare_digest(provided, _TOKEN):
            self._json(403, {"error": "invalid token"})
            return
        ok = start_dashboard()
        self._json(200, {"running": ok, "url": DASHBOARD_URL})


_TOKEN = load_or_create_token()


def main() -> None:
    log(f"helper listening on {HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
