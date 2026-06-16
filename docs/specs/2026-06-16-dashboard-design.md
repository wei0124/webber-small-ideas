# Milestone 2 — `dashboard` Design

**Date:** 2026-06-16
**Status:** Approved (design); ready for implementation planning.

## Goal

A single self-hosted personal start page, built in the same spirit as `cheat`:
**zero dependencies, Python standard library only, clone-and-run.** It reads a
TOML config file and renders one read-only HTML page (bookmarks, to-dos, notes).
No external APIs, no API keys, no write-back, no frontend framework.

## Non-Goals (this MVP)

- No external API widgets (weather, etc.) — they break the no-network,
  no-key, clone-and-run promise. Deferred to a later stretch goal.
- No write-back / interactivity (checking off to-dos, adding bookmarks via the
  page). Read-only render only; you edit the config and refresh.
- No multi-column grid layout. Single-column, declaration-order layout for MVP.
- No clock / JS-driven widgets. Server-side string rendering only.

## Architecture

Single file `dashboard.py`, stdlib only. `python3 dashboard.py` starts a local
`http.server` that reads a TOML config and serves one rendered, read-only HTML
page. Continues the `cheat` DNA: one file, one purpose, no install.

## CLI Interface

- `python3 dashboard.py` — read default `dashboard.toml`, start server (default
  port 8765).
- `--config <path>` — use a specific config file.
- `--port <n>` — bind a specific port.
- `--render` — do NOT start a server; print the rendered HTML to stdout
  (for tests, static-page generation, or piping). Mirrors the design taste of
  `cheat --raw`.

## Config Schema (TOML, requires Python 3.11+ `tomllib`)

Top-level `[[widget]]` array. **Declaration order = top-to-bottom page order**
(this is how "config-driven layout, no code changes to rearrange" is satisfied).
Three widget types:

```toml
[page]
title = "Webber's Dashboard"

[[widget]]
type = "bookmarks"
title = "Dev"
links = [
    { name = "GitHub", url = "https://github.com" },
    { name = "MDN", url = "https://developer.mozilla.org" },
]

[[widget]]
type = "todos"
title = "Today"
items = [
    { text = "Ship dashboard MVP", done = false },
    { text = "Review PR", done = true },
]

[[widget]]
type = "notes"
title = "Scratch"
body = "Multi-line\ntext or notes."
```

## Data Flow & Components (logical layers inside the single file)

```
load_config(path) -> dict
    -> validate(config) -> list[widget]
    -> render_bookmarks(widget) -> str
       render_todos(widget)     -> str    (pure functions, one per type)
       render_notes(widget)     -> str
    -> render_page(config) -> str          (assembles HTML + inlined CSS)
    -> http.server handler returns the page
```

The render layer is **pure functions** that touch neither the network nor the
filesystem. This is the primary test seam.

## Error Handling

- Config file missing → clear message to stderr, exit 1.
- TOML parse error → translate the `tomllib` error into a human-readable message,
  exit 1.
- Widget missing `type` / required field, or unknown `type` → point at which
  widget and which field is wrong, exit 1.
- All user-supplied input (bookmark names, URLs, notes body) is passed through
  `html.escape` when rendered into HTML, to prevent injection.

## Testing (stdlib `unittest`, matching repo convention)

Test the data layer (pure functions) exhaustively:

- valid config parses correctly,
- each of the three widget types renders output containing the expected content,
- `html.escape` is applied (injection attempt is escaped),
- missing field / unknown type raises the expected error,
- `--render` end-to-end emits a complete HTML document containing the page title.

No real server needs to be started.

## Deliverables

- `dashboard.py`
- example `dashboard.toml`
- `tests/test_dashboard.py`
- README section documenting usage and the **Python 3.11+** requirement
- ROADMAP Milestone 2 checkboxes ticked

## Stretch (out of scope for this MVP)

- Multi-column / grid layout driven by config.
- Pluggable widget API so others can register their own widget types.
- Widgets that need JS or the network (clock, weather, live API widgets).

## Working Principles (inherited from ROADMAP)

1. Finish before starting — MVP runs, has tests and docs before anything new.
2. Boring tech wins — stdlib only, zero dependencies, no setup.
3. Tests are non-negotiable — runnable test suite ships with the tool.
4. AI accelerates, human decides — AI scaffolds; design taste stays human.
