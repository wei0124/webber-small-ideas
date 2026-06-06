"""Tests for cheat.py — run with: python -m pytest  (or python tests/test_cheat.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cheat  # noqa: E402


def test_available_lists_known_cheatsheets():
    names = cheat.available()
    assert "tar" in names
    assert "git-rebase" in names
    # sorted, no .md extension
    assert names == sorted(names)
    assert all(not n.endswith(".md") for n in names)


def test_render_known_cheatsheet():
    out = cheat.render("tar")
    assert "archive" in out.lower()


def test_render_unknown_raises_with_suggestions():
    try:
        cheat.render("tarr")  # typo
    except KeyError as exc:
        name, suggestions = exc.args
        assert name == "tarr"
        assert "tar" in suggestions
    else:
        raise AssertionError("expected KeyError for unknown cheatsheet")


def test_search_matches_body_not_just_name():
    # "tunnel" appears in ssh.md body, not in any filename.
    hits = cheat.search("tunnel")
    assert "ssh" in hits


def test_search_is_case_insensitive():
    assert cheat.search("REBASE") == cheat.search("rebase")


def test_main_list_returns_zero(capsys):
    rc = cheat.main(["--list"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "tar" in captured.out


def test_main_unknown_command_returns_one(capsys):
    rc = cheat.main(["definitely-not-a-command"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "No cheatsheet" in captured.err


def test_extract_commands_fenced_blocks():
    md = "# heading\n\nsome prose\n\n```\nfoo --bar\nbaz --qux\n```\n\nmore text\n"
    assert cheat.extract_commands(md) == ["foo --bar", "baz --qux"]


def test_extract_commands_multiple_blocks():
    md = "```\na\n```\n\n```\nb\nc\n```\n"
    assert cheat.extract_commands(md) == ["a", "b", "c"]


def test_extract_commands_ignores_prose_and_headings():
    md = "# title\n\nparagraph\n\n> blockquote\n"
    assert cheat.extract_commands(md) == []


def test_extract_commands_preserves_leading_whitespace():
    md = "```\n  indented cmd\n```\n"
    assert cheat.extract_commands(md) == ["  indented cmd"]


def test_copy_to_clipboard_returns_none_when_no_tool(monkeypatch):
    monkeypatch.setattr(cheat.shutil, "which", lambda _: None)
    assert cheat.copy_to_clipboard("hello") is None


def test_copy_to_clipboard_uses_first_available_tool(monkeypatch):
    calls: list[tuple[list[str], bytes]] = []

    def fake_which(tool):
        return "/usr/bin/" + tool if tool == "wl-copy" else None

    def fake_run(cmd, input=None, check=False):
        calls.append((cmd, input))

    monkeypatch.setattr(cheat.shutil, "which", fake_which)
    monkeypatch.setattr(cheat.subprocess, "run", fake_run)

    result = cheat.copy_to_clipboard("some text")
    assert result == "wl-copy"
    assert len(calls) == 1
    assert calls[0][0] == ["wl-copy"]
    assert calls[0][1] == b"some text"


def test_main_copy_flag_success(monkeypatch, capsys):
    monkeypatch.setattr(cheat, "copy_to_clipboard", lambda text: "pbcopy")
    rc = cheat.main(["-c", "tar"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Copied" in captured.err
    assert "tar" in captured.err
    assert captured.out == ""


def test_main_copy_flag_unknown_command(capsys):
    rc = cheat.main(["-c", "definitely-not-a-command"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "No cheatsheet" in captured.err


def test_main_copy_flag_no_clipboard_tool(monkeypatch, capsys):
    monkeypatch.setattr(cheat, "copy_to_clipboard", lambda text: None)
    rc = cheat.main(["--copy", "tar"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "No clipboard tool" in captured.err
    assert "tar" in captured.out


def test_completion_script_bash_contains_compgen_and_cheat():
    script = cheat.completion_script("bash")
    assert "compgen" in script
    assert "cheat" in script


def test_completion_script_zsh_contains_compadd():
    script = cheat.completion_script("zsh")
    assert "compadd" in script


def test_completion_script_fish_raises_valueerror():
    try:
        cheat.completion_script("fish")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for unsupported shell 'fish'")


def test_main_completion_bash_returns_zero(capsys):
    rc = cheat.main(["--completion", "bash"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "complete" in captured.out


if __name__ == "__main__":
    # Allow running without pytest installed: minimal manual runner.
    import traceback

    class _Monkeypatch:
        """Minimal monkeypatch shim: only supports setattr."""
        def __init__(self):
            self._saved: list[tuple[object, str, object]] = []

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
        try:
            params = fn.__code__.co_varnames
            kwargs = {}
            if "capsys" in params:
                class _Cap:
                    def readouterr(self):
                        import io
                        return type("R", (), {"out": _buf_out.getvalue(),
                                              "err": _buf_err.getvalue()})()
                import io
                _buf_out, _buf_err = io.StringIO(), io.StringIO()
                old_out, old_err = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = _buf_out, _buf_err
                kwargs["capsys"] = _Cap()
            if "monkeypatch" in params:
                mp = _Monkeypatch()
                kwargs["monkeypatch"] = mp
            try:
                fn(**kwargs)
            finally:
                if "capsys" in params:
                    sys.stdout, sys.stderr = old_out, old_err
                if "monkeypatch" in params:
                    mp.undo()
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    raise SystemExit(1 if failed else 0)
