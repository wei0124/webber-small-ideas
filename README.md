# webber-small-ideas

A workshop for **small, genuinely useful open-source tools** — each one scoped
tightly enough to finish, polished enough to be proud of, and free for anyone to
use, fork, and build on.

The philosophy: **AI-accelerated, human-steered.** Lean on an AI assistant to
scaffold and iterate fast, while a human owns the design taste, the polish, and
the "does this actually feel good to use?" judgment calls. The goal is durable,
well-tested software the community can rely on — not throwaway code.

The running list of candidate tools lives in [`IDEAS.md`](IDEAS.md). The
delivery plan lives in [`ROADMAP.md`](ROADMAP.md).

---

## Shipping now: `cheat` — offline command cheatsheets

The first tool from the list. A fast, offline, example-first cheatsheet for any
command you keep forgetting the flags for. Zero dependencies — pure Python
standard library, so it runs anywhere Python 3.8+ does.

### Usage

```
python3 cheat.py tar              # show the tar cheatsheet
python3 cheat.py git-rebase       # show the git rebase cheatsheet
python3 cheat.py --list           # list every available cheatsheet
python3 cheat.py --search tunnel  # find cheatsheets mentioning "tunnel"
python3 cheat.py -c tar           # copy tar commands to the clipboard
python3 cheat.py --raw tar        # print raw Markdown (pipe-friendly)
python3 cheat.py --completion bash  # print bash completion script
python3 cheat.py --sync           # pull latest community cheatsheets
```

### Clipboard copy

Run `cheat -c <command>` to extract the command lines from a cheatsheet's code blocks and copy them to the system clipboard. Works on macOS (pbcopy), Linux Wayland (wl-copy), Linux X11 (xclip/xsel), and Windows (clip). Falls back to printing the commands to stdout if no clipboard tool is available.

Mistype a name and it suggests the closest match:

```
$ python3 cheat.py gti-rebase
No cheatsheet for 'gti-rebase'.
Did you mean: git-rebase?
```

### Adding your own cheatsheet

Drop a Markdown file into `cheatsheets/`. The filename (minus `.md`) becomes the
lookup name. That's the whole "plugin system" — no registration, no config.

```
cheatsheets/
├── find.md
├── git-rebase.md
├── ssh.md
└── tar.md
```

### Optional: install as a `cheat` command

```
chmod +x cheat.py
ln -s "$(pwd)/cheat.py" ~/.local/bin/cheat   # ensure ~/.local/bin is on PATH
cheat tar
```

### Shell completion

Get tab-completion for cheatsheet names:

```bash
# bash — append to ~/.bashrc (or source it separately)
cheat --completion bash >> ~/.bashrc

# zsh — add to ~/.zshrc or eval in your shell
eval "$(cheat --completion zsh)"
```

The completion list stays in sync automatically as you add or remove cheatsheets.

### Syncing community cheatsheets

Pull the latest cheatsheets from the project's GitHub repo into your local `cheatsheets/` folder:

```
cheat --sync
```

Files that are new are added; files that have changed upstream are updated; identical files are left alone. A summary is printed at the end.

You can point `--sync` at any GitHub contents-API URL to pull from a fork or a different repo:

```
cheat --sync https://api.github.com/repos/you/your-fork/contents/cheatsheets
```

---

## Shipping now: `dashboard` — self-hosted personal start page

A single-file, self-hosted personal start page. Reads a TOML config and renders
a clean, read-only HTML page with bookmarks, to-dos, and notes. Zero dependencies
— pure Python standard library, requires **Python 3.11+** (for `tomllib`).

### Usage

```
python3 dashboard.py                     # start server on port 8765
python3 dashboard.py --config my.toml    # use a specific config file
python3 dashboard.py --port 9000         # bind a specific port
python3 dashboard.py --render            # print HTML to stdout (no server)
```

### Config format

```toml
[page]
title = "My Dashboard"
columns = 2          # grid columns (default: 1, max: 6)

[[widget]]
type = "bookmarks"
title = "Dev"
span = 2             # span both columns
links = [
    { name = "GitHub", url = "https://github.com" },
]

[[widget]]
type = "todos"
title = "Today"
items = [
    { text = "Ship MVP", done = false },
]

[[widget]]
type = "notes"
title = "Scratch"
body = "Quick notes."
```

Three widget types: `bookmarks`, `todos`, `notes`. Declaration order in the TOML
file determines top-to-bottom page order. Use `columns` to set a multi-column grid
layout and `span` to make individual widgets occupy multiple columns.

### Requirements

Python 3.11+ (for `tomllib` in the standard library). No `pip install` needed.

---

## Development

```
python3 -m pytest                    # run all tests (83 tests)
python3 tests/test_cheat.py          # cheat tests without pytest
python3 tests/test_dashboard.py      # dashboard tests without pytest
```

## License

MIT — see [`LICENSE`](LICENSE). Use it, fork it, ship it.
