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


def _make_fake_fetch(listing, files):
    """Return a fake ``fetch(url) -> bytes`` for sync tests.

    `listing` is the JSON-serialisable list returned for the API URL.
    `files` maps download_url strings to the bytes they should return.
    """
    import json as _json

    def fake_fetch(url):
        if "contents/cheatsheets" in url:
            return _json.dumps(listing).encode()
        return files.get(url, b"")

    return fake_fetch


def _sample_listing():
    """Canned GitHub contents-API listing for two cheatsheets."""
    return [
        {
            "name": "fake-cmd.md",
            "type": "file",
            "download_url": "https://raw.example.com/fake-cmd.md",
        },
        {
            "name": "another-cmd.md",
            "type": "file",
            "download_url": "https://raw.example.com/another-cmd.md",
        },
    ]


def _sample_files():
    """Canned remote file content matching the listing above."""
    return {
        "https://raw.example.com/fake-cmd.md": b"# fake-cmd\n\n```\nfake --flag\n```\n",
        "https://raw.example.com/another-cmd.md": b"# another-cmd\n\n```\nanother --x\n```\n",
    }


def test_sync_empty_dir_reports_all_added(tmp_path):
    listing = _sample_listing()
    files = _sample_files()
    fetch = _make_fake_fetch(listing, files)

    result = cheat.sync(
        api_url="https://api.github.com/repos/x/y/contents/cheatsheets",
        dest_dir=str(tmp_path),
        fetch=fetch,
    )

    assert result["added"] == ["another-cmd.md", "fake-cmd.md"]
    assert result["updated"] == []
    assert result["unchanged"] == []
    assert (tmp_path / "fake-cmd.md").read_bytes() == files["https://raw.example.com/fake-cmd.md"]
    assert (tmp_path / "another-cmd.md").read_bytes() == files["https://raw.example.com/another-cmd.md"]


def test_sync_identical_content_reports_unchanged(tmp_path):
    listing = _sample_listing()
    files = _sample_files()
    fetch = _make_fake_fetch(listing, files)
    api = "https://api.github.com/repos/x/y/contents/cheatsheets"

    cheat.sync(api_url=api, dest_dir=str(tmp_path), fetch=fetch)

    result = cheat.sync(api_url=api, dest_dir=str(tmp_path), fetch=fetch)
    assert result["added"] == []
    assert result["updated"] == []
    assert result["unchanged"] == ["another-cmd.md", "fake-cmd.md"]


def test_sync_changed_content_reports_updated(tmp_path):
    listing = _sample_listing()
    files = _sample_files()
    fetch = _make_fake_fetch(listing, files)
    api = "https://api.github.com/repos/x/y/contents/cheatsheets"

    cheat.sync(api_url=api, dest_dir=str(tmp_path), fetch=fetch)

    (tmp_path / "fake-cmd.md").write_bytes(b"# old content\n")

    updated_files = dict(files)
    updated_files["https://raw.example.com/fake-cmd.md"] = b"# new content\n"
    fetch2 = _make_fake_fetch(listing, updated_files)

    result = cheat.sync(api_url=api, dest_dir=str(tmp_path), fetch=fetch2)
    assert result["added"] == []
    assert result["updated"] == ["fake-cmd.md"]
    assert result["unchanged"] == ["another-cmd.md"]
    assert (tmp_path / "fake-cmd.md").read_bytes() == b"# new content\n"


def test_main_sync_end_to_end(monkeypatch, tmp_path, capsys):
    listing = _sample_listing()
    files = _sample_files()
    fetch = _make_fake_fetch(listing, files)
    monkeypatch.setattr(cheat, "_fetch", fetch)
    monkeypatch.setattr(cheat, "CHEAT_DIR", str(tmp_path))
    monkeypatch.setattr(cheat, "DEFAULT_SYNC_URL",
                        "https://api.github.com/repos/x/y/contents/cheatsheets")

    rc = cheat.main(["--sync"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Sync complete" in captured.out
    assert "2 added" in captured.out


def test_parse_tags_single_line():
    md = "# title\n<!-- tags: devops, networking -->\n## section\n"
    assert cheat.parse_tags(md) == ["devops", "networking"]


def test_parse_tags_no_tags():
    md = "# title\n## section\nno tags here\n"
    assert cheat.parse_tags(md) == []


def test_parse_tags_multiple_lines():
    md = "<!-- tags: a, b -->\nsome text\n<!-- tags: c -->\n"
    assert cheat.parse_tags(md) == ["a", "b", "c"]


def test_parse_tags_strips_whitespace():
    md = "<!-- tags:  foo , bar ,  baz  -->\n"
    assert cheat.parse_tags(md) == ["foo", "bar", "baz"]


def test_parse_tags_empty_inner():
    md = "<!-- tags: -->\n"
    assert cheat.parse_tags(md) == []


def test_all_tags_returns_dict():
    tags = cheat.all_tags()
    assert isinstance(tags, dict)
    assert len(tags) > 0


def test_all_tags_known_tag():
    tags = cheat.all_tags()
    assert "text-processing" in tags
    assert "grep" in tags["text-processing"]
    assert "sed" in tags["text-processing"]


def test_all_tags_devops():
    tags = cheat.all_tags()
    assert "devops" in tags
    assert "docker" in tags["devops"]
    assert "kubectl" in tags["devops"]


def test_main_tags_list_all(capsys):
    rc = cheat.main(["--tags"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "text-processing" in captured.out
    assert "devops" in captured.out


def test_main_tags_filter_specific(capsys):
    rc = cheat.main(["--tags", "git"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "git-rebase" in captured.out


def test_main_tags_filter_nonexistent(capsys):
    rc = cheat.main(["--tags", "nonexistent-tag-xyz"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "No cheatsheets tagged" in captured.err


def test_main_tags_counts_format(capsys):
    rc = cheat.main(["--tags"])
    captured = capsys.readouterr()
    assert rc == 0
    lines = captured.out.strip().split("\n")
    for line in lines:
        assert "(" in line and ")" in line


def test_tags_present_in_new_cheatsheets():
    tags = cheat.all_tags()
    assert "orchestration" in tags
    assert "kubectl" in tags["orchestration"]
    assert "build" in tags
    assert "make" in tags["build"]
    assert "terminal" in tags
    assert "tmux" in tags["terminal"]


if __name__ == "__main__":
    # Allow running without pytest installed: minimal manual runner.
    import shutil
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
            _tmp_dir = None
            if "tmp_path" in params:
                import pathlib
                import tempfile
                _tmp_dir = tempfile.mkdtemp()
                kwargs["tmp_path"] = pathlib.Path(_tmp_dir)
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
                if _tmp_dir is not None:
                    shutil.rmtree(_tmp_dir, ignore_errors=True)
            print(f"PASS {fn.__name__}")
        except Exception:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    raise SystemExit(1 if failed else 0)
