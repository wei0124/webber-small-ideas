#!/usr/bin/env python3
"""dashboard — a self-hosted personal start page, zero dependencies.

Usage:
    python3 dashboard.py                  Start server on port 8765 (default).
    python3 dashboard.py --config my.toml Use a specific config file.
    python3 dashboard.py --port 9000      Bind to a specific port.
    python3 dashboard.py --render         Print rendered HTML to stdout (no server).

Requires Python 3.11+ for tomllib.
"""
from __future__ import annotations

import argparse
import html
import os
import sys
import tomllib
from http.server import HTTPServer, BaseHTTPRequestHandler

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.toml")
DEFAULT_PORT = 8765

# ── Config loading ────────────────────────────────────────────────────────────


def load_config(path: str) -> dict:
    """Load and parse a TOML config file.

    Raises FileNotFoundError with a human-readable message if the file is
    missing.  Raises ValueError with a human-readable message on TOML parse
    errors.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in {path}: {exc}") from exc


# ── Validation ────────────────────────────────────────────────────────────────

_KNOWN_TYPES = {"bookmarks", "todos", "notes"}


def validate(config: dict) -> list[dict]:
    """Validate the config and return the list of widget dicts.

    Raises ValueError with a human-readable message pointing at the offending
    widget and field.
    """
    page = config.get("page", {})
    columns = page.get("columns", 1)
    if not isinstance(columns, int) or columns < 1:
        raise ValueError("'page.columns' must be a positive integer (default: 1).")
    if columns > 6:
        raise ValueError("'page.columns' must be at most 6.")

    widgets = config.get("widget", [])
    if not isinstance(widgets, list):
        raise ValueError("'widget' must be a TOML array ([[widget]]).")

    for idx, w in enumerate(widgets, start=1):
        wtype = w.get("type")
        if not wtype:
            raise ValueError(f"Widget #{idx} is missing required field 'type'.")
        if wtype not in _KNOWN_TYPES:
            raise ValueError(
                f"Widget #{idx} has unknown type {wtype!r}. "
                f"Known types: {', '.join(sorted(_KNOWN_TYPES))}."
            )

        span = w.get("span", 1)
        if not isinstance(span, int) or span < 1:
            raise ValueError(
                f"Widget #{idx} ({wtype}): 'span' must be a positive integer."
            )
        if span > columns:
            raise ValueError(
                f"Widget #{idx} ({wtype}): 'span' ({span}) exceeds "
                f"page columns ({columns})."
            )

        if wtype == "bookmarks":
            if "links" not in w:
                raise ValueError(
                    f"Widget #{idx} (type='bookmarks') is missing required field 'links'."
                )
            for li, link in enumerate(w["links"], start=1):
                if "name" not in link or "url" not in link:
                    raise ValueError(
                        f"Widget #{idx} (bookmarks): link #{li} requires 'name' and 'url'."
                    )

        elif wtype == "todos":
            if "items" not in w:
                raise ValueError(
                    f"Widget #{idx} (type='todos') is missing required field 'items'."
                )
                # (no sub-field validation required for items per spec)

        elif wtype == "notes":
            if "body" not in w:
                raise ValueError(
                    f"Widget #{idx} (type='notes') is missing required field 'body'."
                )

    return widgets


# ── Rendering (pure functions, no I/O) ───────────────────────────────────────


def _esc(text: str) -> str:
    """HTML-escape user-supplied text."""
    return html.escape(str(text), quote=True)


def _widget_style(widget: dict) -> str:
    """Return an inline style attribute for grid span, or empty string."""
    span = widget.get("span", 1)
    if span > 1:
        return f' style="grid-column: span {span}"'
    return ""


def render_bookmarks(widget: dict) -> str:
    """Render a bookmarks widget to an HTML fragment."""
    title = _esc(widget.get("title", "Bookmarks"))
    items = []
    for link in widget["links"]:
        name = _esc(link["name"])
        url = _esc(link["url"])
        items.append(f'        <li><a href="{url}">{name}</a></li>')
    body = "\n".join(items)
    return (
        f'    <section class="widget widget-bookmarks"{_widget_style(widget)}>\n'
        f"      <h2>{title}</h2>\n"
        f"      <ul>\n{body}\n      </ul>\n"
        f"    </section>"
    )


def render_todos(widget: dict) -> str:
    """Render a todos widget to an HTML fragment."""
    title = _esc(widget.get("title", "Todos"))
    items = []
    for item in widget["items"]:
        text = _esc(item.get("text", ""))
        checked = ' checked disabled' if item.get("done") else " disabled"
        items.append(
            f'        <li><input type="checkbox"{checked}> {text}</li>'
        )
    body = "\n".join(items)
    return (
        f'    <section class="widget widget-todos"{_widget_style(widget)}>\n'
        f"      <h2>{title}</h2>\n"
        f"      <ul>\n{body}\n      </ul>\n"
        f"    </section>"
    )


def render_notes(widget: dict) -> str:
    """Render a notes widget to an HTML fragment."""
    title = _esc(widget.get("title", "Notes"))
    body = _esc(widget["body"]).replace("\n", "<br>")
    return (
        f'    <section class="widget widget-notes"{_widget_style(widget)}>\n'
        f"      <h2>{title}</h2>\n"
        f"      <p>{body}</p>\n"
        f"    </section>"
    )


_RENDERERS = {
    "bookmarks": render_bookmarks,
    "todos": render_todos,
    "notes": render_notes,
}

_CSS_BASE = """\
    * { box-sizing: border-box; margin: 0; padding: 0; }
    h1 { margin-bottom: 1.5rem; font-size: 1.6rem; }
    .widget { background: #fff; border-radius: 8px; padding: 1.2rem;
              margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .widget h2 { font-size: 1.1rem; margin-bottom: 0.6rem; color: #444; }
    .widget ul { list-style: none; padding-left: 0; }
    .widget li { padding: 0.25rem 0; }
    .widget a { color: #0366d6; text-decoration: none; }
    .widget a:hover { text-decoration: underline; }
    .widget-notes p { white-space: normal; line-height: 1.5; }
"""


def _grid_css(columns: int) -> str:
    """Return CSS for the page body/grid container based on column count."""
    if columns <= 1:
        return (
            "    body {\n"
            "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n"
            "      background: #f5f5f5; color: #222; padding: 2rem;\n"
            "      max-width: 640px; margin: 0 auto;\n"
            "    }\n"
        )
    return (
        "    body {\n"
        "      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n"
        "      background: #f5f5f5; color: #222; padding: 2rem;\n"
        f"      max-width: 1200px; margin: 0 auto;\n"
        f"      display: grid; grid-template-columns: repeat({columns}, 1fr);\n"
        "      gap: 1rem;\n"
        "    }\n"
    )


def render_page(config: dict) -> str:
    """Render the full HTML page from a validated config dict."""
    page = config.get("page", {})
    page_title = _esc(page.get("title", "Dashboard"))
    columns = page.get("columns", 1)
    widgets = validate(config)

    fragments = []
    for w in widgets:
        renderer = _RENDERERS[w["type"]]
        fragments.append(renderer(w))

    body = "\n".join(fragments)
    css = _CSS_BASE + _grid_css(columns)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{page_title}</title>\n"
        "  <style>\n"
        f"{css}"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>{page_title}</h1>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


# ── HTTP server ───────────────────────────────────────────────────────────────


def _make_handler(config: dict) -> type:
    """Return a BaseHTTPRequestHandler subclass bound to the given config."""

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            html_page = render_page(config)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_page.encode("utf-8"))

        def log_message(self, format, *args):
            # Quieter logging (stderr, same as default but suppresses in tests).
            sys.stderr.write(f"[dashboard] {args[0]}\n")

    return DashboardHandler


def serve(config: dict, port: int = DEFAULT_PORT) -> None:
    """Start the HTTP server (blocking)."""
    handler = _make_handler(config)
    server = HTTPServer(("0.0.0.0", port), handler)
    print(f"Dashboard running at http://localhost:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
    finally:
        server.server_close()


# ── CLI entry point ───────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dashboard",
        description="A self-hosted personal start page (zero dependencies).",
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG,
        help=f"path to TOML config file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"port to bind (default: {DEFAULT_PORT})")
    parser.add_argument("--render", action="store_true",
                        help="print rendered HTML to stdout and exit (no server)")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        validate(config)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.render:
        print(render_page(config), end="")
        return 0

    serve(config, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
