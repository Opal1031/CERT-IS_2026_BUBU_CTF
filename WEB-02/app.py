import json
import os
import re
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


FLAG = os.environ.get("FLAG", "")
if not re.fullmatch(r"BUBU\{[^{}\r\n]+\}", FLAG):
    raise SystemExit("FLAG must be set to a value in BUBU{...} format.")

try:
    PORT = int(os.environ.get("PORT", "3000"))
except ValueError as error:
    raise SystemExit("PORT must be an integer from 1 to 65535.") from error
if not 1 <= PORT <= 65535:
    raise SystemExit("PORT must be an integer from 1 to 65535.")

SITE = Path(__file__).resolve().parent / "site"
ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/booths": ("booths.html", "text/html; charset=utf-8"),
    "/schedule": ("schedule.html", "text/html; charset=utf-8"),
    "/guide": ("guide.html", "text/html; charset=utf-8"),
    "/static/style.css": ("static/style.css", "text/css; charset=utf-8"),
    "/static/booths.js": ("static/booths.js", "text/javascript; charset=utf-8"),
}

BOOTH_ROWS = [
    (1, "암호 해독 연구소", "체험", "A동 101호", "짧은 암호 퍼즐과 해독 체험", 84, 1),
    (2, "패킷 탐험대", "실습", "A동 102호", "네트워크 흐름을 따라가는 미니 실습", 92, 1),
    (3, "디지털 흔적 찾기", "체험", "A동 103호", "사진과 파일에 남은 흔적 찾기", 76, 1),
    (4, "보안 퀴즈 라운지", "이벤트", "B동 201호", "팀원과 함께 푸는 보안 퀴즈", 98, 1),
    (5, "웹 방어 실험실", "실습", "B동 202호", "웹 요청을 관찰하는 짧은 실습", 89, 1),
    (6, "동아리 교류존", "안내", "B동 203호", "참가 동아리 소개와 자유 교류", 71, 1),
]

DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.executescript(
    """
    CREATE TABLE booths (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT NOT NULL,
        popularity INTEGER NOT NULL,
        public INTEGER NOT NULL
    );
    CREATE TABLE staff_secrets (
        name TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """
)
DB.executemany("INSERT INTO booths VALUES (?, ?, ?, ?, ?, ?, ?)", BOOTH_ROWS)
DB.execute("INSERT INTO staff_secrets VALUES (?, ?)", ("event_flag", FLAG))
DB.commit()
DB.execute("PRAGMA query_only = ON")
DB_LOCK = threading.Lock()


def get_booths(sort):
    if not sort or len(sort) > 512 or "\x00" in sort:
        raise ValueError("Invalid sort")

    query = (
        "SELECT id, name, category, location, description, popularity "
        "FROM booths WHERE public = 1 ORDER BY " + sort + " LIMIT 6"
    )

    with DB_LOCK:
        deadline = time.monotonic() + 0.4
        DB.set_progress_handler(lambda: time.monotonic() >= deadline, 1000)
        try:
            return [dict(row) for row in DB.execute(query).fetchall()]
        finally:
            DB.set_progress_handler(None, 0)


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def respond_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.respond(status, "application/json; charset=utf-8", body)

    def do_GET(self):
        try:
            request = urlsplit(self.path)
            path = request.path
        except ValueError:
            self.respond_json(400, {"error": "잘못된 요청입니다."})
            return

        if path == "/healthz":
            self.respond(200, "text/plain; charset=utf-8", b"ok")
            return

        if path == "/api/booths":
            try:
                params = parse_qs(request.query, keep_blank_values=True, max_num_fields=8)
                sort = params.get("sort", ["popularity DESC, id ASC"])[0]
                booths = get_booths(sort)
            except (ValueError, sqlite3.Error):
                self.respond_json(400, {"error": "정렬 기준을 적용할 수 없습니다."})
                return
            self.respond_json(200, {"booths": booths})
            return

        route = ROUTES.get(path)
        if route is None:
            self.respond_json(404, {"error": "페이지를 찾을 수 없습니다."})
            return

        filename, content_type = route
        try:
            content = (SITE / filename).read_bytes()
        except OSError:
            self.respond_json(500, {"error": "페이지를 불러올 수 없습니다."})
            return
        self.respond(200, content_type, content)

    def log_message(self, format_string, *args):
        pass


if __name__ == "__main__":
    try:
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    finally:
        DB.close()
