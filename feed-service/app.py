from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from kanban import parse_kanban_markdown, sections_to_html


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KANBAN_SOURCE_PATH = Path(
    os.environ.get("KANBAN_SOURCE_PATH", PROJECT_ROOT / "data" / "KANBAN.md")
).expanduser()
DAILY_BRIEF_HTML_PATH = Path(
    os.environ.get(
        "DAILY_BRIEF_HTML_PATH",
        PROJECT_ROOT / "data" / "daily-brief.html",
    )
).expanduser()


def render_shell(title: str, body: str) -> bytes:
    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ padding: 18px 20px; border-bottom: 1px solid #334155; }}
    main {{ padding: 18px 20px; }}
    h1, h2 {{ margin: 0 0 12px 0; }}
    .panel {{ margin: 0 0 16px 0; padding: 16px; border: 1px solid #334155; border-radius: 10px; background: #111827; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; border-bottom: 1px solid #243041; padding: 8px 10px; vertical-align: top; }}
    th {{ color: #93c5fd; font-size: 12px; text-transform: uppercase; letter-spacing: .02em; }}
    a {{ color: #93c5fd; }}
    .muted {{ color: #94a3b8; }}
    pre {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div class="muted">Kanban source: {KANBAN_SOURCE_PATH}</div>
  </header>
  <main>{body}</main>
</body>
</html>"""
    return html.encode("utf-8")


def load_daily_brief_html() -> str:
    if DAILY_BRIEF_HTML_PATH.exists():
        return DAILY_BRIEF_HTML_PATH.read_text(encoding="utf-8")
    return (
        "<section class='panel'>"
        "<h2>Daily Brief</h2>"
        "<p class='muted'>No Daily Brief HTML found.</p>"
        f"<p class='muted'>Expected path: {DAILY_BRIEF_HTML_PATH}</p>"
        "</section>"
    )


def build_kanban_payload() -> dict:
    try:
        sections = parse_kanban_markdown(KANBAN_SOURCE_PATH)
    except FileNotFoundError:
        sections = []
    return {
        "source": str(KANBAN_SOURCE_PATH),
        "sections": [
            {
                "name": section.name,
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "assignee": item.assignee,
                        "priority": item.priority,
                        "notes": item.notes,
                    }
                    for item in section.items
                ],
            }
            for section in sections
        ],
    }


def build_kanban_html() -> bytes:
    if KANBAN_SOURCE_PATH.exists():
        body = sections_to_html(parse_kanban_markdown(KANBAN_SOURCE_PATH))
    else:
        body = (
            "<section class='panel'>"
            "<h2>Kanban</h2>"
            "<p class='muted'>No Kanban markdown found.</p>"
            f"<p class='muted'>Expected path: {KANBAN_SOURCE_PATH}</p>"
            "</section>"
        )
    return render_shell("Kanban", body)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        if self.path == "/api/kanban":
            body = json.dumps(build_kanban_payload(), ensure_ascii=False, indent=2).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body)
            return

        if self.path == "/kanban":
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", build_kanban_html())
            return

        if self.path == "/daily-brief":
            body = load_daily_brief_html().encode("utf-8")
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)
            return

        payload = {
            "kanban": "/kanban",
            "daily_brief": "/daily-brief",
            "api": "/api/kanban",
            "health": "/health",
        }
        body = render_shell("Glance Feed", "<pre>" + json.dumps(payload, indent=2) + "</pre>")
        self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)


def main() -> int:
    port = int(os.environ.get("PORT", "8081"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"listening on {port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
