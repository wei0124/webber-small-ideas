#!/usr/bin/env python3
"""cheat — fast, offline, example-first command cheatsheets.

Usage:
    cheat <command>        Show the cheatsheet for a command (e.g. `cheat tar`).
    cheat -c <command>     Copy command lines from a cheatsheet to the clipboard.
    cheat --list           List every available cheatsheet.
    cheat --search <term>  Find cheatsheets whose name or body mentions <term>.
    cheat --completion bash  Print a bash completion script (also: zsh).
    cheat --tags             List all tags and their counts.
    cheat --tags <tag>       List sheets that have a specific tag.
    cheat --sync [URL]     Pull the latest community cheatsheets from GitHub.

Cheatsheets are plain Markdown files in the `cheatsheets/` folder next to this
script, so adding your own is just dropping in a new `.md` file.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from difflib import get_close_matches

CHEAT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cheatsheets")

DEFAULT_SYNC_URL = (
    "https://api.github.com/repos/wei0124/webber-small-ideas/contents/cheatsheets"
)

# ANSI colors, disabled automatically when output is not a TTY.
_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def available() -> list[str]:
    """Return sorted cheatsheet names (filename without the .md extension)."""
    if not os.path.isdir(CHEAT_DIR):
        return []
    return sorted(
        f[:-3] for f in os.listdir(CHEAT_DIR) if f.endswith(".md")
    )


def _path_for(name: str) -> str:
    return os.path.join(CHEAT_DIR, f"{name}.md")


def render(name: str) -> str:
    """Return the pretty-printed cheatsheet for `name`.

    Raises KeyError if no cheatsheet matches, attaching close suggestions.
    """
    names = available()
    if name not in names:
        suggestions = get_close_matches(name, names, n=3, cutoff=0.4)
        raise KeyError(name, suggestions)
    with open(_path_for(name), encoding="utf-8") as fh:
        return _highlight(fh.read())


def _highlight(markdown: str) -> str:
    """Minimal Markdown highlighter: headings, code, and comments."""
    out: list[str] = []
    in_code = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            out.append("  " + _c(line, "36"))  # cyan command
        elif stripped.startswith("#"):
            out.append(_c(line.lstrip("# "), "1;33"))  # bold yellow heading
        elif stripped.startswith("#") is False and stripped.startswith(">"):
            out.append(_c(line, "2"))  # dim blockquote
        else:
            out.append(line)
    return "\n".join(out)


def search(term: str) -> list[str]:
    """Return cheatsheet names whose name or body contains `term`."""
    term = term.lower()
    hits: list[str] = []
    for name in available():
        if term in name.lower():
            hits.append(name)
            continue
        with open(_path_for(name), encoding="utf-8") as fh:
            if term in fh.read().lower():
                hits.append(name)
    return hits


def parse_tags(markdown: str) -> list[str]:
    """Parse tags from ``<!-- tags: foo, bar -->`` lines in `markdown`."""
    tags: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- tags:") and stripped.endswith("-->"):
            inner = stripped[len("<!-- tags:"):-len("-->")].strip()
            if inner:
                tags.extend(t.strip() for t in inner.split(",") if t.strip())
    return tags


def all_tags() -> dict[str, list[str]]:
    """Return ``{tag: [sheet_names]}`` for every cheatsheet that declares tags."""
    result: dict[str, list[str]] = {}
    for name in available():
        with open(_path_for(name), encoding="utf-8") as fh:
            for tag in parse_tags(fh.read()):
                result.setdefault(tag, []).append(name)
    return result


_CLIPBOARD_TOOLS: list[tuple[str, list[str]]] = [
    ("pbcopy", []),
    ("wl-copy", []),
    ("xclip", ["-selection", "clipboard"]),
    ("xsel", ["--clipboard", "--input"]),
    ("clip", []),
]


def extract_commands(markdown: str) -> list[str]:
    """Return lines inside fenced ``` code blocks from `markdown`."""
    lines: list[str] = []
    in_code = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            lines.append(line)
    return lines


def copy_to_clipboard(text: str) -> str | None:
    """Copy `text` to the system clipboard.

    Returns the name of the clipboard tool used, or None if none was found.
    """
    for tool, extra_args in _CLIPBOARD_TOOLS:
        if shutil.which(tool):
            subprocess.run(
                [tool, *extra_args],
                input=text.encode(),
                check=True,
            )
            return tool
    return None


def _raw_markdown(name: str) -> str:
    """Return the raw Markdown for cheatsheet `name`.

    Raises KeyError with close suggestions if not found.
    """
    names = available()
    if name not in names:
        suggestions = get_close_matches(name, names, n=3, cutoff=0.4)
        raise KeyError(name, suggestions)
    with open(_path_for(name), encoding="utf-8") as fh:
        return fh.read()


def completion_script(shell: str) -> str:
    """Return a shell completion script for `shell` (bash or zsh).

    Raises ValueError for unsupported shells.
    """
    if shell == "bash":
        return (
            "_cheat_completions() {\n"
            "    local cur\n"
            '    cur="${COMP_WORDS[COMP_CWORD]}"\n'
            '    COMPREPLY=( $(compgen -W "$(cheat --list 2>/dev/null)" -- "$cur") )\n'
            "}\n"
            "complete -F _cheat_completions cheat\n"
        )
    if shell == "zsh":
        return (
            "_cheat_completions() {\n"
            "    compadd $(cheat --list 2>/dev/null)\n"
            "}\n"
            "compdef _cheat_completions cheat\n"
        )
    raise ValueError(f"Unsupported shell: {shell!r} (expected 'bash' or 'zsh')")


def _fetch(url: str) -> bytes:
    """Fetch `url` and return its content as bytes.

    Uses a User-Agent header (required by the GitHub API) and a 15-second
    timeout.  Raises on any network or HTTP error.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "cheat-cli/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def sync(
    api_url: str = DEFAULT_SYNC_URL,
    dest_dir: str = CHEAT_DIR,
    *,
    fetch: "callable[[str], bytes] | None" = None,
) -> dict:
    """Pull community cheatsheets from a GitHub contents-API listing.

    `api_url` must return a JSON array of file objects (keys: ``name``,
    ``type``, ``download_url``).  Only entries where ``type == "file"`` and
    ``name`` ends with ``".md"`` are processed.

    `dest_dir` is created if it does not exist.  Each remote file is compared
    against the local copy (byte-for-byte); files are written only when they
    are new or have changed.

    `fetch` is an injectable ``fetch(url) -> bytes`` callable so tests can
    run fully offline.  When *None* (the default), the module-level
    ``_fetch`` is used (looked up at call time so it can be monkeypatched).

    Returns ``{"added": [...], "updated": [...], "unchanged": [...]}``
    (sorted name lists).

    Raises ``RuntimeError`` with a human-readable message on any network or
    JSON error.
    """
    if fetch is None:
        fetch = _fetch
    try:
        listing = json.loads(fetch(api_url))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch cheatsheet listing from {api_url}: {exc}"
        ) from exc

    os.makedirs(dest_dir, exist_ok=True)

    added: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []

    for entry in listing:
        if entry.get("type") != "file":
            continue
        name: str = entry.get("name", "")
        if not name.endswith(".md"):
            continue
        download_url: str = entry.get("download_url", "")
        if not download_url:
            continue

        try:
            remote_bytes = fetch(download_url)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to download {name} from {download_url}: {exc}"
            ) from exc

        local_path = os.path.join(dest_dir, name)
        if not os.path.exists(local_path):
            with open(local_path, "wb") as fh:
                fh.write(remote_bytes)
            added.append(name)
        else:
            with open(local_path, "rb") as fh:
                local_bytes = fh.read()
            if local_bytes != remote_bytes:
                with open(local_path, "wb") as fh:
                    fh.write(remote_bytes)
                updated.append(name)
            else:
                unchanged.append(name)

    return {
        "added": sorted(added),
        "updated": sorted(updated),
        "unchanged": sorted(unchanged),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cheat",
        description="Fast, offline, example-first command cheatsheets.",
    )
    parser.add_argument("command", nargs="?", help="command to look up")
    parser.add_argument("-c", "--copy", action="store_true",
                        help="copy command lines to clipboard instead of displaying")
    parser.add_argument("--list", action="store_true", help="list all cheatsheets")
    parser.add_argument("--search", metavar="TERM", help="search cheatsheets")
    parser.add_argument("--tags", nargs="?", const=True, metavar="TAG",
                        help="list all tags (or filter by a specific tag)")
    parser.add_argument("--completion", choices=["bash", "zsh"],
                        help="print a shell completion script (bash or zsh)")
    parser.add_argument("--sync", nargs="?", const=DEFAULT_SYNC_URL, metavar="URL",
                        help="sync community cheatsheets from a GitHub repo")
    args = parser.parse_args(argv)

    if args.completion:
        print(completion_script(args.completion), end="")
        return 0

    if args.sync is not None:
        try:
            result = sync(api_url=args.sync, dest_dir=CHEAT_DIR)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        n_added = len(result["added"])
        n_updated = len(result["updated"])
        n_unchanged = len(result["unchanged"])
        print(f"Sync complete: {n_added} added, {n_updated} updated, {n_unchanged} unchanged.")
        for name in result["added"]:
            print(f"  + {name}")
        for name in result["updated"]:
            print(f"  ~ {name}")
        return 0

    if args.tags is not None:
        tags = all_tags()
        if not tags:
            print("No tags found.", file=sys.stderr)
            return 1
        if args.tags is True:
            for tag in sorted(tags):
                print(f"{tag} ({len(tags[tag])})")
        else:
            sheets = tags.get(args.tags, [])
            if not sheets:
                print(f"No cheatsheets tagged {args.tags!r}.", file=sys.stderr)
                return 1
            print("\n".join(sheets))
        return 0

    if args.list:
        names = available()
        if not names:
            print("No cheatsheets found.", file=sys.stderr)
            return 1
        print("\n".join(names))
        return 0

    if args.search:
        hits = search(args.search)
        if not hits:
            print(f"No cheatsheet mentions {args.search!r}.", file=sys.stderr)
            return 1
        print("\n".join(hits))
        return 0

    if not args.command:
        parser.print_help()
        return 1

    if args.copy:
        try:
            md = _raw_markdown(args.command)
        except KeyError as exc:
            name, suggestions = exc.args
            print(f"No cheatsheet for {name!r}.", file=sys.stderr)
            if suggestions:
                print(f"Did you mean: {', '.join(suggestions)}?", file=sys.stderr)
            return 1
        commands = extract_commands(md)
        if not commands:
            print(f"No commands found in {args.command!r}.", file=sys.stderr)
            return 1
        text = "\n".join(commands)
        tool = copy_to_clipboard(text)
        if tool is None:
            print(text)
            print("No clipboard tool found; printed commands to stdout instead.",
                  file=sys.stderr)
            return 1
        print(f"Copied {len(commands)} command(s) from {args.command} to clipboard.",
              file=sys.stderr)
        return 0

    try:
        print(render(args.command))
    except KeyError as exc:
        name, suggestions = exc.args
        print(f"No cheatsheet for {name!r}.", file=sys.stderr)
        if suggestions:
            print(f"Did you mean: {', '.join(suggestions)}?", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
