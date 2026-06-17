# Development Guide

<cite>
**Referenced Files in This Document**
- [cheat.py](file://cheat.py)
- [README.md](file://README.md)
- [tests/test_cheat.py](file://tests/test_cheat.py)
- [cheatsheets/tar.md](file://cheatsheets/tar.md)
- [cheatsheets/git-rebase.md](file://cheatsheets/git-rebase.md)
- [IDEAS.md](file://IDEAS.md)
- [ROADMAP.md](file://ROADMAP.md)
- [.gitignore](file://.gitignore)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Testing Strategy](#testing-strategy)
9. [Contribution Guidelines](#contribution-guidelines)
10. [Debugging and Maintenance](#debugging-and-maintenance)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Conclusion](#conclusion)

## Introduction
This guide documents the development workflow for the cheat CLI tool, a zero-dependency, Python standard library–based command-line cheatsheet reader. It covers environment setup, testing with pytest, code quality standards, the file-based cheatsheet format, markdown parsing, data organization, testing strategy, contribution and release procedures, architectural decisions, extensibility points, debugging techniques, and maintenance practices.

## Project Structure
The repository is organized around a single CLI entry point, a directory of Markdown cheatsheets, and a focused test suite. The structure emphasizes simplicity and zero external dependencies.

```mermaid
graph TB
Root["Repository Root"]
CLI["cheat.py"]
Sheets["cheatsheets/"]
Tests["tests/"]
Docs["README.md"]
Ideas["IDEAS.md"]
Roadmap["ROADMAP.md"]
GitIgnore[".gitignore"]
Root --> CLI
Root --> Sheets
Root --> Tests
Root --> Docs
Root --> Ideas
Root --> Roadmap
Root --> GitIgnore
Sheets --> SheetTar["tar.md"]
Sheets --> SheetGit["git-rebase.md"]
Tests --> TestFile["test_cheat.py"]
```

**Diagram sources**
- [cheat.py](file://cheat.py)
- [README.md](file://README.md)
- [tests/test_cheat.py](file://tests/test_cheat.py)
- [cheatsheets/tar.md](file://cheatsheets/tar.md)
- [cheatsheets/git-rebase.md](file://cheatsheets/git-rebase.md)
- [IDEAS.md](file://IDEAS.md)
- [ROADMAP.md](file://ROADMAP.md)
- [.gitignore](file://.gitignore)

**Section sources**
- [cheat.py](file://cheat.py)
- [README.md](file://README.md)
- [tests/test_cheat.py](file://tests/test_cheat.py)
- [cheatsheets/tar.md](file://cheatsheets/tar.md)
- [cheatsheets/git-rebase.md](file://cheatsheets/git-rebase.md)
- [IDEAS.md](file://IDEAS.md)
- [ROADMAP.md](file://ROADMAP.md)
- [.gitignore](file://.gitignore)

## Core Components
- CLI entrypoint and argument parsing: [cheat.py](file://cheat.py)
- Markdown cheatsheet directory: [cheatsheets/](file://cheatsheets/)
- Test suite: [tests/test_cheat.py](file://tests/test_cheat.py)
- Project documentation: [README.md](file://README.md), [IDEAS.md](file://IDEAS.md), [ROADMAP.md](file://ROADMAP.md)
- Version control ignores: [.gitignore](file://.gitignore)

Key responsibilities:
- CLI: parse arguments, route to features (render, search, copy, completion, sync, tags, list, raw).
- Markdown parsing: highlight headings, blockquotes, and code blocks; extract command lines from fenced code blocks.
- Data organization: flat cheatsheet directory keyed by filename (without .md).
- Testing: unit and integration tests for rendering, search, clipboard copy, completion scripts, sync, and tag parsing.

**Section sources**
- [cheat.py](file://cheat.py)
- [README.md](file://README.md)
- [tests/test_cheat.py](file://tests/test_cheat.py)

## Architecture Overview
The CLI is a single-file application leveraging Python’s standard library. It reads Markdown files from a local directory, applies lightweight syntax highlighting, and exposes commands for listing, searching, copying, tagging, completion, and syncing.

```mermaid
graph TB
subgraph "CLI Layer"
ArgParse["Argument Parser<br/>cheat.py:292–411"]
Main["main(argv)"]
end
subgraph "Domain Layer"
Available["available()"]
Render["render(name)"]
Highlight["_highlight(markdown)"]
Search["search(term)"]
Extract["extract_commands(markdown)"]
ParseTags["parse_tags(markdown)"]
AllTags["all_tags()"]
Completion["completion_script(shell)"]
Sync["sync(api_url, dest_dir, fetch)"]
Raw["_raw_markdown(name)"]
end
subgraph "System Layer"
FS["Filesystem<br/>cheatsheets/"]
Net["HTTP Fetch<br/>urllib.request"]
Subproc["Clipboard Tools<br/>subprocess"]
Diff["Fuzzy Matching<br/>difflib"]
end
Main --> ArgParse
Main --> Render
Main --> Search
Main --> Extract
Main --> Completion
Main --> Sync
Main --> AllTags
Main --> Available
Main --> Raw
Render --> Highlight
Render --> FS
Search --> FS
Extract --> FS
ParseTags --> FS
AllTags --> FS
Completion --> Main
Sync --> Net
Sync --> FS
Extract --> Subproc
Render --> Diff
```

**Diagram sources**
- [cheat.py](file://cheat.py)

## Detailed Component Analysis

### CLI Argument Parsing and Routing
The CLI uses argparse to define subcommands and options. It routes to feature functions and handles errors with helpful messages and suggestions.

```mermaid
sequenceDiagram
participant User as "User"
participant CLI as "main()"
participant Parser as "argparse"
participant Feature as "Feature Functions"
User->>CLI : "cheat [options] [command]"
CLI->>Parser : "parse_args(argv)"
Parser-->>CLI : "Parsed args"
alt "--completion"
CLI->>Feature : "completion_script(shell)"
Feature-->>CLI : "Script text"
CLI-->>User : "Print script"
else "--sync"
CLI->>Feature : "sync(api_url, dest_dir, fetch)"
Feature-->>CLI : "Result summary"
CLI-->>User : "Print summary"
else "--tags"
CLI->>Feature : "all_tags()"
Feature-->>CLI : "Tags map"
CLI-->>User : "List tags or filtered sheets"
else "--list"
CLI->>Feature : "available()"
Feature-->>CLI : "Sorted names"
CLI-->>User : "Print names"
else "--search"
CLI->>Feature : "search(term)"
Feature-->>CLI : "Matching names"
CLI-->>User : "Print hits"
else "--raw"
CLI->>Feature : "_raw_markdown(name)"
Feature-->>CLI : "Raw Markdown"
CLI-->>User : "Print raw"
else "-c/--copy"
CLI->>Feature : "_raw_markdown(name)"
Feature-->>CLI : "Raw Markdown"
CLI->>Feature : "extract_commands(md)"
Feature-->>CLI : "Command lines"
CLI->>Feature : "copy_to_clipboard(text)"
Feature-->>CLI : "Tool used or None"
CLI-->>User : "Success or fallback to stdout"
else default
CLI->>Feature : "render(name)"
Feature-->>CLI : "Highlighted Markdown"
CLI-->>User : "Print rendered"
end
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

### Markdown Rendering and Highlighting
The renderer highlights headings, blockquotes, and code blocks. It preserves indentation and uses ANSI color codes conditionally.

```mermaid
flowchart TD
Start(["render(name)"]) --> CheckName["Check availability"]
CheckName --> |Unknown| Suggest["get_close_matches(...)"]
Suggest --> Raise["Raise KeyError(name, suggestions)"]
CheckName --> |Known| Read["Open file and read()"]
Read --> Highlight["_highlight(markdown)"]
Highlight --> Headings{"Line starts with '#'?"}
Headings --> |Yes| ColorHead["Apply bold yellow"]
Headings --> |No| Blockquote{"Line starts with '>'?"}
Blockquote --> |Yes| ColorQuote["Apply dim"]
Blockquote --> |No| CodeBlock{"Inside code fence?"}
CodeBlock --> |Yes| Cyan["Apply cyan for command lines"]
CodeBlock --> |No| Plain["Keep plain"]
ColorHead --> Join["Join lines"]
ColorQuote --> Join
Cyan --> Join
Plain --> Join
Join --> End(["Return rendered"])
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

### Command Extraction and Clipboard Integration
Command extraction parses fenced code blocks and copies combined commands to the system clipboard using platform-specific tools.

```mermaid
flowchart TD
Start(["extract_commands(markdown)"]) --> Iterate["Iterate lines"]
Iterate --> Fence{"Line starts with '
```'?"}
    Fence -->|Yes| Toggle["Toggle in_code flag"]
    Fence -->|No| InCode{"in_code?"}
    InCode -->|Yes| Collect["Append line to list"]
    InCode -->|No| Skip["Skip"]
    Toggle --> Iterate
    Collect --> Iterate
    Skip --> Iterate
    Iterate --> Done(["Return list"])
```

Clipboard tool selection prioritizes platform-specific tools and falls back to stdout when none are available.

```mermaid
sequenceDiagram
participant Caller as "Caller"
participant Extract as "extract_commands()"
participant Copy as "copy_to_clipboard(text)"
participant Tools as "Clipboard Tools"
participant OS as "OS"
Caller->>Extract : "Markdown"
Extract-->>Caller : "Command lines"
Caller->>Copy : "text"
loop "For each tool"
Copy->>Tools : "shutil.which(tool)"
Tools-->>Copy : "Path or None"
alt "Tool available"
Copy->>OS : "subprocess.run([tool, ...], input=text)"
OS-->>Copy : "Success"
Copy-->>Caller : "Return tool name"
else "No tool"
Copy-->>Caller : "None"
end
end
alt "No tool found"
Copy-->>Caller : "Print text to stdout"
end
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

### Tag Parsing and Tag Indexing
Tags are parsed from comment lines and indexed by tag name to sheet names.

```mermaid
flowchart TD
Start(["parse_tags(markdown)"]) --> Lines["Split into lines"]
Lines --> Loop{"For each line"}
Loop --> Strip["Strip whitespace"]
Strip --> Check{"Starts with '<!-- tags:' and ends with ' --> '?"}
Check --> |No| Next["Next line"]
Check --> |Yes| Inner["Extract inner text"]
Inner --> NonEmpty{"Inner non-empty?"}
NonEmpty --> |No| Next
NonEmpty --> |Yes| Split["Split by ',' and strip"]
Split --> Append["Append to tags list"]
Append --> Next
Next --> End(["Return tags"])
```

Tag indexing aggregates all tags across sheets.

```mermaid
flowchart TD
Start(["all_tags()"]) --> Iterate["Iterate available sheets"]
Iterate --> Read["Open and read()"]
Read --> Parse["parse_tags()"]
Parse --> Group{"For each tag"}
Group --> Add["Append sheet name to tags[tag]"]
Add --> Iterate
Iterate --> End(["Return {tag: [sheets]}"])
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

### Sync from Community Repository
The sync function fetches a GitHub contents listing, compares local vs remote content byte-for-byte, and writes changes only when needed.

```mermaid
flowchart TD
Start(["sync(api_url, dest_dir, fetch)"]) --> FetchListing["fetch(api_url) -> JSON"]
FetchListing --> Parse["json.loads(...)"]
Parse --> EnsureDir["os.makedirs(dest_dir, exist_ok=True)"]
EnsureDir --> ForEach["For each entry"]
ForEach --> TypeCheck{"type == 'file'?"}
TypeCheck --> |No| NextEntry["Next entry"]
TypeCheck --> |Yes| ExtCheck{"name ends with '.md'?"}
ExtCheck --> |No| NextEntry
ExtCheck --> |Yes| Download["fetch(download_url)"]
Download --> LocalExists{"Local file exists?"}
LocalExists --> |No| WriteNew["Write bytes -> added"]
LocalExists --> |Yes| Compare["Compare bytes"]
Compare --> Changed{"Bytes differ?"}
Changed --> |Yes| WriteUpdated["Write bytes -> updated"]
Changed --> |No| MarkUnchanged["Mark unchanged"]
WriteNew --> NextEntry
WriteUpdated --> NextEntry
MarkUnchanged --> NextEntry
NextEntry --> Done(["Return {added, updated, unchanged}"])
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

### File-Based Cheatsheet Format
Cheatsheets are plain Markdown files placed under the cheatsheets directory. The filename (without .md) becomes the lookup key. Tags are declared via comment lines.

```mermaid
erDiagram
SHEET {
string name PK
string path
datetime last_modified
}
TAG {
string name PK
string sheet_name FK
}
SHEET ||--o{ TAG : "has"
```

Principles:
- Filename without .md is the command name.
- Tags are declared with a comment line format and parsed into a normalized list.
- Code blocks are treated as executable commands for copy operations.

**Diagram sources**
- [cheat.py](file://cheat.py)
- [cheatsheets/tar.md](file://cheatsheets/tar.md)
- [cheatsheets/git-rebase.md](file://cheatsheets/git-rebase.md)

**Section sources**
- [cheat.py](file://cheat.py)
- [cheatsheets/tar.md](file://cheatsheets/tar.md)
- [cheatsheets/git-rebase.md](file://cheatsheets/git-rebase.md)

## Dependency Analysis
The project relies solely on Python standard library modules. External dependencies are intentionally avoided to ensure portability and ease of installation.

```mermaid
graph LR
Cheat["cheat.py"]
Arg["argparse"]
Json["json"]
Os["os"]
Shutil["shutil"]
Subproc["subprocess"]
Sys["sys"]
Urllib["urllib.request"]
Difflib["difflib"]
Cheat --> Arg
Cheat --> Json
Cheat --> Os
Cheat --> Shutil
Cheat --> Subproc
Cheat --> Sys
Cheat --> Urllib
Cheat --> Difflib
```

**Diagram sources**
- [cheat.py](file://cheat.py)

**Section sources**
- [cheat.py](file://cheat.py)

## Performance Considerations
- File I/O: Reading all available sheets and iterating through each file during search and tag indexing is linear in the number of sheets. For typical repositories with dozens of sheets, performance is negligible.
- Network I/O: Sync uses a fixed timeout and minimal payload; bandwidth is bounded by the number of files and their sizes.
- CPU: Highlighting and tag parsing are simple string operations; complexity is linear in the number of lines.
- Memory: Entire files are loaded into memory for rendering and search; this is acceptable given the modest size of cheatsheets.

Optimization opportunities:
- Lazy loading: defer reading files until needed.
- Caching: cache parsed tags and rendered content for repeated lookups.
- Streaming: process files in chunks for very large sheets.

[No sources needed since this section provides general guidance]

## Testing Strategy
The project uses a comprehensive test suite that validates both unit and integration scenarios. Tests are designed to run with or without pytest.

Coverage areas:
- Availability and rendering of known cheatsheets.
- Fuzzy suggestion behavior for typos.
- Search functionality across filenames and content.
- Command extraction from fenced code blocks.
- Clipboard copy behavior and fallback to stdout.
- Shell completion script generation for bash and zsh.
- Sync behavior: added, updated, unchanged files.
- Tag parsing and tag indexing.
- Raw output printing and error handling.

Manual verification checklist:
- Run CLI with various commands and options.
- Verify color output on TTY and disablement with NO_COLOR.
- Confirm completion scripts integrate with bash/zsh.
- Validate sync updates and summaries.
- Ensure tag filtering and listing work as expected.

**Section sources**
- [tests/test_cheat.py](file://tests/test_cheat.py)
- [README.md](file://README.md)

## Contribution Guidelines
- Scope: Keep contributions focused and aligned with the zero-dependency philosophy.
- Tests: Add tests for new features and behaviors; ensure they pass locally.
- Documentation: Update README and internal docstrings as needed.
- Style: Follow Python conventions; maintain readability and simplicity.
- Review: Submit PRs with clear descriptions and rationale.

[No sources needed since this section provides general guidance]

## Debugging and Maintenance
Common debugging techniques:
- Enable verbose output by printing intermediate results in feature functions.
- Use NO_COLOR to disable ANSI output when diagnosing color-related issues.
- Temporarily replace network fetch with a mock to isolate network failures.
- Inspect filesystem permissions and paths when encountering I/O errors.

Maintenance procedures:
- Periodically update cheatsheets directory with new content.
- Validate sync behavior against upstream changes.
- Monitor test coverage and add tests for edge cases.

**Section sources**
- [cheat.py](file://cheat.py)

## Troubleshooting Guide
- No cheatsheets found: Ensure the cheatsheets directory exists and contains .md files.
- Unknown command: Verify spelling; the CLI suggests close matches.
- Clipboard copy fails: Install a supported clipboard tool or run without -c to print commands.
- Sync errors: Check network connectivity and API URL correctness; inspect returned error messages.
- Completion not working: Confirm shell type and that the generated script is sourced.

**Section sources**
- [cheat.py](file://cheat.py)
- [README.md](file://README.md)

## Conclusion
The cheat CLI tool exemplifies a minimal, robust design built on Python’s standard library. Its architecture, centered on file-based cheatsheets and simple parsing, enables rapid iteration and broad portability. The comprehensive test suite and clear contribution guidelines support ongoing development and maintenance.

[No sources needed since this section summarizes without analyzing specific files]