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


if __name__ == "__main__":
    # Allow running without pytest installed: minimal manual runner.
    import traceback

    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in funcs:
        try:
            # crude capsys shim for the two tests that need it
            if "capsys" in fn.__code__.co_varnames:
                class _Cap:
                    def readouterr(self):
                        import io
                        return type("R", (), {"out": _buf_out.getvalue(),
                                              "err": _buf_err.getvalue()})()
                import io
                _buf_out, _buf_err = io.StringIO(), io.StringIO()
                old_out, old_err = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = _buf_out, _buf_err
                try:
                    fn(_Cap())
                finally:
                    sys.stdout, sys.stderr = old_out, old_err
            else:
                fn()
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    raise SystemExit(1 if failed else 0)
