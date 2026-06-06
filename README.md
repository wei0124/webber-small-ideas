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

## Development

```
python3 -m pytest          # run the test suite (24 tests)
python3 tests/test_cheat.py # or run without pytest installed
```

## License

MIT — see [`LICENSE`](LICENSE). Use it, fork it, ship it.
