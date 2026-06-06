# Roadmap

This repo ships small, useful open-source tools one at a time. Each tool follows
the same arc: **MVP that runs → tests + docs → one stretch goal that makes it
stand out.** Nothing ships until it actually works and has tests.

The full pool of candidate tools is in [`IDEAS.md`](IDEAS.md). This roadmap is
the delivery order and the definition of "done" for each.

## Status legend

- ✅ Shipped — runs, tested, documented
- 🚧 In progress
- ⬜ Planned

---

## Milestone 1 — `cheat`: offline command cheatsheets ✅

The first tool. Done means:

- [x] Single-file CLI, zero dependencies (Python stdlib only)
- [x] `cheat <command>`, `--list`, `--search` all working
- [x] Fuzzy "did you mean?" suggestions on typos
- [x] Drop-in Markdown cheatsheet format (no registration needed)
- [x] Test suite (runs with or without pytest)
- [x] **Stretch:** clipboard copy (`cheat -c <command>`)
- [x] **Stretch:** shell completion (`cheat --completion bash|zsh`)
- [ ] **Stretch:** community cheatsheet sync command

## Milestone 2 — Personal dashboard / start page ⬜

A single self-hosted page: bookmarks, weather, to-dos, a couple of API widgets.

- [ ] Static page + small backend for the widgets
- [ ] Config-driven layout (no code changes to rearrange)
- [ ] Tests for the widget data layer
- [ ] **Stretch:** pluggable widget API so others can add their own

## Milestone 3 — Pick the next from `IDEAS.md` ⬜

Candidates: a Markdown-to-anything converter, a local-first habit tracker, a
regex playground, a tiny static-site generator. Chosen based on what proves most
useful while building Milestones 1–2.

---

## Working principles

1. **Finish before starting.** A tool isn't on the list until the previous one
   has tests and docs.
2. **Boring tech wins.** Prefer the standard library and zero-dependency designs
   so anyone can run the tools with no setup.
3. **Tests are non-negotiable.** Every shipped tool has a runnable test suite.
4. **AI accelerates, human decides.** AI assistance scaffolds and refactors; the
   design taste and the "is this good?" call stay human.
