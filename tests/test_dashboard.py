"""Tests for dashboard.py — run with: python -m pytest tests/test_dashboard.py"""
import os
import sys
import tempfile
import textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dashboard  # noqa: E402

# ── Fixtures ─────────────────────────────────────────────────────────────────

_VALID_TOML = textwrap.dedent("""\
[page]
title = "Test Dashboard"

[[widget]]
type = "bookmarks"
title = "Links"
links = [
    { name = "GitHub", url = "https://github.com" },
    { name = "Evil <script>", url = "javascript:alert(1)" },
]

[[widget]]
type = "todos"
title = "Tasks"
items = [
    { text = "Write tests", done = false },
    { text = "Ship MVP",    done = true  },
]

[[widget]]
type = "notes"
title = "Memo"
body = "Line 1\\nLine 2"
""")


def _write_toml(tmp_path, content: str = _VALID_TOML, name: str = "dashboard.toml") -> str:
    """Write TOML content to a temp file and return its path."""
    path = os.path.join(str(tmp_path), name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


# ── load_config ───────────────────────────────────────────────────────────────


def test_load_config_valid(tmp_path):
    path = _write_toml(tmp_path)
    config = dashboard.load_config(path)
    assert config["page"]["title"] == "Test Dashboard"
    assert len(config["widget"]) == 3


def test_load_config_missing_file_raises():
    try:
        dashboard.load_config("/nonexistent/path/dashboard.toml")
    except FileNotFoundError as exc:
        assert "not found" in str(exc).lower()
    else:
        raise AssertionError("expected FileNotFoundError")


def test_load_config_invalid_toml_raises(tmp_path):
    path = _write_toml(tmp_path, content="[invalid\ntoml = = =", name="bad.toml")
    try:
        dashboard.load_config(path)
    except ValueError as exc:
        assert "toml" in str(exc).lower() or "invalid" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for invalid TOML")


# ── validate ─────────────────────────────────────────────────────────────────


def test_validate_valid_config(tmp_path):
    path = _write_toml(tmp_path)
    config = dashboard.load_config(path)
    widgets = dashboard.validate(config)
    assert len(widgets) == 3
    assert [w["type"] for w in widgets] == ["bookmarks", "todos", "notes"]


def test_validate_missing_type_raises():
    config = {"widget": [{"title": "Oops"}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "type" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for missing type")


def test_validate_unknown_type_raises():
    config = {"widget": [{"type": "calendar"}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "unknown type" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for unknown type")


def test_validate_bookmarks_missing_links_raises():
    config = {"widget": [{"type": "bookmarks", "title": "No links"}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "links" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for bookmarks without links")


def test_validate_bookmarks_link_missing_url_raises():
    config = {"widget": [{"type": "bookmarks", "title": "Bad link",
                          "links": [{"name": "NoURL"}]}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "url" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for link missing url")


def test_validate_todos_missing_items_raises():
    config = {"widget": [{"type": "todos", "title": "Empty"}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "items" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for todos without items")


def test_validate_notes_missing_body_raises():
    config = {"widget": [{"type": "notes", "title": "Empty"}]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "body" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for notes without body")


def test_validate_no_widget_key_returns_empty():
    config = {"page": {"title": "No widgets"}}
    widgets = dashboard.validate(config)
    assert widgets == []


# ── render_bookmarks ─────────────────────────────────────────────────────────


def test_render_bookmarks_contains_link():
    widget = {"type": "bookmarks", "title": "Dev",
              "links": [{"name": "GitHub", "url": "https://github.com"}]}
    out = dashboard.render_bookmarks(widget)
    assert 'href="https://github.com"' in out
    assert "GitHub" in out
    assert "Dev" in out


def test_render_bookmarks_escapes_html():
    widget = {"type": "bookmarks", "title": "Test",
              "links": [{"name": "<script>alert(1)</script>",
                         "url": "https://example.com"}]}
    out = dashboard.render_bookmarks(widget)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_render_bookmarks_escapes_url():
    widget = {"type": "bookmarks", "title": "Test",
              "links": [{"name": "link", "url": '"><img src=x onerror=alert(1)>'}]}
    out = dashboard.render_bookmarks(widget)
    assert 'onerror' not in out or "&lt;" in out or "&quot;" in out


# ── render_todos ──────────────────────────────────────────────────────────────


def test_render_todos_checked_and_unchecked():
    widget = {"type": "todos", "title": "Today",
              "items": [{"text": "Done task", "done": True},
                        {"text": "Open task", "done": False}]}
    out = dashboard.render_todos(widget)
    assert "checked" in out
    assert "Done task" in out
    assert "Open task" in out
    # Count unchecked (not checked) items
    assert out.count('type="checkbox"') == 2


def test_render_todos_escapes_html():
    widget = {"type": "todos", "title": "XSS",
              "items": [{"text": "<img src=x onerror=alert(1)>", "done": False}]}
    out = dashboard.render_todos(widget)
    assert "<img" not in out
    assert "&lt;img" in out


# ── render_notes ──────────────────────────────────────────────────────────────


def test_render_notes_contains_body():
    widget = {"type": "notes", "title": "Memo", "body": "Hello world"}
    out = dashboard.render_notes(widget)
    assert "Hello world" in out
    assert "Memo" in out


def test_render_notes_newlines_to_br():
    widget = {"type": "notes", "title": "Lines", "body": "Line 1\nLine 2"}
    out = dashboard.render_notes(widget)
    assert "Line 1<br>Line 2" in out


def test_render_notes_escapes_html():
    widget = {"type": "notes", "title": "XSS",
              "body": "<script>alert('xss')</script>"}
    out = dashboard.render_notes(widget)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


# ── render_page ───────────────────────────────────────────────────────────────


def test_render_page_full_document(tmp_path):
    path = _write_toml(tmp_path)
    config = dashboard.load_config(path)
    out = dashboard.render_page(config)
    assert out.startswith("<!DOCTYPE html>")
    assert "</html>" in out
    assert "Test Dashboard" in out


def test_render_page_widgets_in_declaration_order(tmp_path):
    path = _write_toml(tmp_path)
    config = dashboard.load_config(path)
    out = dashboard.render_page(config)
    # Use rfind to skip CSS class definitions; look at the actual widget sections
    bm_pos = out.rfind("widget-bookmarks")
    notes_pos = out.rfind("widget-notes")
    assert bm_pos != -1 and notes_pos != -1
    assert bm_pos < notes_pos


def test_render_page_escapes_page_title():
    config = {"page": {"title": "<b>Bold</b>"}, "widget": []}
    out = dashboard.render_page(config)
    assert "<title>&lt;b&gt;Bold&lt;/b&gt;</title>" in out


def test_render_page_default_title_when_missing():
    config = {"widget": []}
    out = dashboard.render_page(config)
    assert "Dashboard" in out


def test_render_page_injection_in_bookmark_name_escaped():
    config = {
        "page": {"title": "Test"},
        "widget": [{
            "type": "bookmarks",
            "title": "Dev",
            "links": [{"name": "<b>bold</b>", "url": "https://example.com"}],
        }],
    }
    out = dashboard.render_page(config)
    assert "<b>bold</b>" not in out
    assert "&lt;b&gt;bold&lt;/b&gt;" in out


# ── main (CLI) ────────────────────────────────────────────────────────────────


def test_main_render_end_to_end(tmp_path, capsys):
    path = _write_toml(tmp_path)
    rc = dashboard.main(["--config", path, "--render"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "<!DOCTYPE html>" in captured.out
    assert "Test Dashboard" in captured.out
    assert "GitHub" in captured.out


def test_main_missing_config_returns_one(capsys):
    rc = dashboard.main(["--config", "/no/such/file.toml", "--render"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "not found" in captured.err.lower()


def test_main_invalid_toml_returns_one(tmp_path, capsys):
    path = _write_toml(tmp_path, content="[broken\ntoml = = =", name="bad.toml")
    rc = dashboard.main(["--config", path, "--render"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "invalid" in captured.err.lower() or "toml" in captured.err.lower()


def test_main_validation_error_returns_one(tmp_path, capsys):
    bad_config = '[page]\ntitle = "Bad"\n\n[[widget]]\ntype = "unknown"\n'
    path = _write_toml(tmp_path, content=bad_config, name="bad_widget.toml")
    rc = dashboard.main(["--config", path, "--render"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "unknown" in captured.err.lower()


def test_main_render_no_server_started(tmp_path, capsys):
    """--render must NOT start a server (test that it returns immediately)."""
    path = _write_toml(tmp_path)
    rc = dashboard.main(["--config", path, "--render"])
    # If we reach here, no server blocked us.
    assert rc == 0


# ── Default config file (dashboard.toml next to dashboard.py) ────────────────


def test_example_toml_is_valid():
    """The shipped dashboard.toml must parse and validate cleanly."""
    example = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "dashboard.toml")
    if not os.path.isfile(example):
        return  # skip if not present
    config = dashboard.load_config(example)
    widgets = dashboard.validate(config)
    assert len(widgets) > 0


def test_example_toml_render_does_not_crash():
    example = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "dashboard.toml")
    if not os.path.isfile(example):
        return
    config = dashboard.load_config(example)
    out = dashboard.render_page(config)
    # Apostrophe is HTML-escaped, so check for the prefix only
    assert "Webber" in out and "Dashboard" in out


# ── Grid layout: columns validation ────────────────────────────────────────


def test_validate_columns_default_when_missing():
    config = {"page": {"title": "No cols"}, "widget": []}
    widgets = dashboard.validate(config)
    assert widgets == []


def test_validate_columns_positive_integer():
    config = {"page": {"columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi"}
    ]}
    widgets = dashboard.validate(config)
    assert len(widgets) == 1


def test_validate_columns_zero_raises():
    config = {"page": {"columns": 0}, "widget": []}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "columns" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for columns=0")


def test_validate_columns_negative_raises():
    config = {"page": {"columns": -1}, "widget": []}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "columns" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for columns=-1")


def test_validate_columns_too_large_raises():
    config = {"page": {"columns": 7}, "widget": []}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "at most 6" in str(exc).lower() or "columns" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for columns=7")


# ── Grid layout: span validation ──────────────────────────────────────────


def test_validate_span_default_when_missing():
    config = {"page": {"columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi"}
    ]}
    widgets = dashboard.validate(config)
    assert len(widgets) == 1


def test_validate_span_valid():
    config = {"page": {"columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi", "span": 2}
    ]}
    widgets = dashboard.validate(config)
    assert widgets[0]["span"] == 2


def test_validate_span_exceeds_columns_raises():
    config = {"page": {"columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi", "span": 3}
    ]}
    try:
        dashboard.validate(config)
    except ValueError as exc:
        assert "exceeds" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for span > columns")


# ── Grid layout: rendering ─────────────────────────────────────────────────


def test_render_page_single_column_no_grid_css():
    config = {"page": {"title": "Single"}, "widget": [
        {"type": "notes", "title": "N", "body": "hi"}
    ]}
    out = dashboard.render_page(config)
    assert "max-width: 640px" in out
    assert "grid-template-columns" not in out


def test_render_page_two_columns_has_grid_css():
    config = {"page": {"title": "Grid", "columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi"}
    ]}
    out = dashboard.render_page(config)
    assert "grid-template-columns: repeat(2, 1fr)" in out
    assert "max-width: 1200px" in out


def test_render_page_span_emits_inline_style():
    config = {"page": {"title": "Span", "columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi", "span": 2}
    ]}
    out = dashboard.render_page(config)
    assert 'style="grid-column: span 2"' in out


def test_render_page_no_span_no_inline_style():
    config = {"page": {"title": "NoSpan", "columns": 2}, "widget": [
        {"type": "notes", "title": "N", "body": "hi"}
    ]}
    out = dashboard.render_page(config)
    assert "grid-column" not in out


def test_render_page_backward_compat(tmp_path):
    """Existing _VALID_TOML (no columns, no span) renders without grid CSS."""
    path = _write_toml(tmp_path)
    config = dashboard.load_config(path)
    out = dashboard.render_page(config)
    assert "max-width: 640px" in out
    assert "grid-template-columns" not in out
    assert "grid-column" not in out


# ── Standalone runner (no pytest required) ───────────────────────────────────

if __name__ == "__main__":
    import shutil
    import traceback
    import pathlib

    class _Monkeypatch:
        def __init__(self):
            self._saved = []
        def setattr(self, target, name, value):
            self._saved.append((target, name, getattr(target, name)))
            setattr(target, name, value)
        def undo(self):
            for target, name, old in reversed(self._saved):
                setattr(target, name, old)
            self._saved.clear()

    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in funcs:
        params = fn.__code__.co_varnames
        kwargs = {}
        _tmp_dir = None
        old_out = old_err = None
        mp = None
        _passed = True
        _err_msg = ""
        try:
            if "tmp_path" in params:
                _tmp_dir = tempfile.mkdtemp()
                kwargs["tmp_path"] = pathlib.Path(_tmp_dir)
            if "capsys" in params:
                import io
                class _Cap:
                    def readouterr(self):
                        return type("R", (), {"out": _buf_out.getvalue(),
                                              "err": _buf_err.getvalue()})()
                _buf_out, _buf_err = io.StringIO(), io.StringIO()
                old_out, old_err = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = _buf_out, _buf_err
                kwargs["capsys"] = _Cap()
            if "monkeypatch" in params:
                mp = _Monkeypatch()
                kwargs["monkeypatch"] = mp
            fn(**kwargs)
        except Exception:
            _passed = False
            _err_msg = traceback.format_exc()
            failed += 1
        finally:
            if old_out is not None:
                sys.stdout, sys.stderr = old_out, old_err
            if mp is not None:
                mp.undo()
            if _tmp_dir is not None:
                shutil.rmtree(_tmp_dir, ignore_errors=True)
            # Print result AFTER stdout is restored so it reaches the real terminal
            if _passed:
                print(f"PASS {fn.__name__}")
            else:
                print(f"FAIL {fn.__name__}")
                print(_err_msg, end="")
    print(f"\n{'=' * 40}")
    print(f"{'All passed!' if failed == 0 else f'{failed} FAILED'}")
    raise SystemExit(1 if failed else 0)
