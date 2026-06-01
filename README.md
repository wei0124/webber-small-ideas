# Top 10 Vibe Coding Ideas

Small, useful projects you can build *fast* (a weekend or less) and publish on GitHub with pride. Each one is genuinely useful, has a clear scope you can finish, and leaves room to show off your taste.

> **Vibe coding** = lean on an AI assistant to scaffold and iterate quickly, while you steer the design, the polish, and the "does this actually feel good to use?" judgment calls.

For each idea you'll find: what it is, why it's worth building, a suggested stack, the smallest version that's still shippable (the **MVP**), and one stretch goal to make it stand out.

---

## 1. CLI Cheatsheet / TLDR Tool

**What:** A terminal command that prints concise, example-first usage for any command (`cheat tar`, `cheat git rebase`).

**Why it's good:** Everyone forgets flags. A fast, offline, example-driven helper is something you'll actually use every day — and so will others.

- **Stack:** Python or Go (single binary is a nice flex), Markdown cheatsheet files.
- **MVP:** Read Markdown files from a local folder and pretty-print the matching one with syntax highlighting.
- **Stretch:** Fuzzy search, community cheatsheet repo sync, `--copy` to put a command on your clipboard.

## 2. Personal Dashboard / Start Page

**What:** A single self-hosted page with your bookmarks, weather, to-dos, and a few API widgets.

**Why it's good:** It's the homepage you'll set in your browser, so polish pays off immediately. Great for showing front-end taste.

- **Stack:** Vanilla JS or Svelte, no backend needed (localStorage), deploy on GitHub Pages.
- **MVP:** Editable bookmark grid + clock + a greeting that changes with time of day.
- **Stretch:** Theme switching, a config-as-JSON system so others can fork and customize easily.

## 3. Markdown → Anything Converter

**What:** Drop in Markdown, get out a styled HTML page, a PDF, or slides.

**Why it's good:** Useful, demoable in seconds, and the "before/after" makes for a great README GIF.

- **Stack:** Node + a Markdown parser (e.g. `marked`/`markdown-it`), Puppeteer for PDF.
- **MVP:** `md2html input.md` producing a clean, themed HTML file.
- **Stretch:** Live preview server, multiple themes, a "presentation mode" that splits on `---`.

## 4. Habit / Streak Tracker

**What:** Tiny app to check off daily habits and visualize streaks (think GitHub contribution graph for your life).

**Why it's good:** Satisfying to use, visually rewarding, and the data model is trivial.

- **Stack:** React/Svelte + localStorage, or SQLite if you want a backend.
- **MVP:** Add habits, tap to mark done today, see a streak count.
- **Stretch:** A heatmap calendar, export/import, gentle reminders via the Notifications API.

## 5. API Status / Uptime Pinger

**What:** A small service that pings a list of URLs on a schedule and shows up/down history.

**Why it's good:** Practical for anyone running side projects, and teaches scheduling, storage, and a clean status UI.

- **Stack:** Node or Python + a cron loop, SQLite, a minimal status page.
- **MVP:** Config file of URLs → ping every N minutes → log results → show a green/red dashboard.
- **Stretch:** Email/Discord/Slack alerts on downtime, latency graphs, a public status page.

## 6. Smart Clipboard Manager

**What:** A history of everything you've copied, searchable, with quick re-paste.

**Why it's good:** A genuinely missing OS feature for many people; pure quality-of-life.

- **Stack:** Electron/Tauri (Tauri = tiny binaries), or a menu-bar app.
- **MVP:** Capture clipboard changes, store last N items, click to copy back.
- **Stretch:** Pin favorites, snippet expansion (`;email` → your email), fuzzy search.

## 7. Regex / Cron / JSON Playground

**What:** A browser tool that explains and tests a regex (or cron expression, or JSON path) live.

**Why it's good:** Single-purpose, instantly useful, and easy to make beautiful. High "share-on-Twitter" potential.

- **Stack:** Pure front-end, deploy to GitHub Pages — zero hosting cost.
- **MVP:** Input + test string + highlighted matches + plain-English explanation.
- **Stretch:** Save/share via URL hash, a library of common patterns, dark mode.

## 8. Expense Splitter

**What:** Split a bill among friends, track who owes whom, settle up with the fewest transactions.

**Why it's good:** A real algorithm at the core (debt simplification) wrapped in a friendly UI — shows you can do both.

- **Stack:** Svelte/React + localStorage; no accounts needed.
- **MVP:** Add people, add expenses with payer, compute balances.
- **Stretch:** "Minimize transactions" settle-up algorithm, shareable group links, currency support.

## 9. Static Site / Portfolio Generator

**What:** Point it at a folder of Markdown + a config, get a deployable personal site.

**Why it's good:** You'll use it for your *own* portfolio, so it dogfoods itself — and that story sells the repo.

- **Stack:** Node + a templating engine, output static HTML for GitHub Pages.
- **MVP:** Markdown posts → themed blog index + post pages.
- **Stretch:** Themes, RSS feed, one-command `deploy` to GitHub Pages.

## 10. AI-Powered Commit Message / PR Summarizer

**What:** A CLI that reads your staged `git diff` and drafts a clear commit message (or PR description).

**Why it's good:** On-trend, immediately useful to developers (your GitHub audience), and a clean intro to wiring up an LLM API.

- **Stack:** Python/Node + an LLM API (Claude, etc.), reads `git diff --staged`.
- **MVP:** `aicommit` → prints a suggested Conventional Commits message you can accept or edit.
- **Stretch:** Git hook integration, PR body generation, configurable tone/format.

---

## Tips for Shipping Fast

- **Pick the smallest version that's still useful.** Ship the MVP, then iterate in public.
- **Write the README first.** It clarifies scope and becomes your demo. Add a screenshot or GIF.
- **One clear thing, done well** beats five half-features. Vibe = polish on the path users actually walk.
- **Add a license** (MIT is a safe default) and a couple of "good first issue" notes to invite contributors.
- **Deploy it.** A live link (GitHub Pages, a tiny VPS, or a free tier) turns a repo into a project people try.

Happy building. 🚀
