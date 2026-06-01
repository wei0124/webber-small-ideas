#!/usr/bin/env python3
"""cheat — fast, offline, example-first command cheatsheets.

Usage:
    cheat <command>        Show the cheatsheet for a command (e.g. `cheat tar`).
    cheat --list           List every available cheatsheet.
    cheat --search <term>  Find cheatsheets whose name or body mentions <term>.

Cheatsheets are plain Markdown files in the `cheatsheets/` folder next to this
script, so adding your own is just dropping in a new `.md` file.
"""
from __future__ import annotations

import argparse
import os
import sys
from difflib import get_close_matches

CHEAT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cheatsheets")

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cheat",
        description="Fast, offline, example-first command cheatsheets.",
    )
    parser.add_argument("command", nargs="?", help="command to look up")
    parser.add_argument("--list", action="store_true", help="list all cheatsheets")
    parser.add_argument("--search", metavar="TERM", help="search cheatsheets")
    args = parser.parse_args(argv)

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
