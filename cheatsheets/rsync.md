# rsync — fast file sync & transfer

## Basic sync
```
rsync -av src/ dest/                   # archive mode + verbose
rsync -av src/ dest/                   # trailing / = contents of src
rsync -av src dest/                    # no trailing / = src folder itself
```

## Useful flags
```
rsync -avh --progress src/ dest/       # show progress per file
rsync -av --dry-run src/ dest/         # preview without changes
rsync -av --delete src/ dest/          # delete files in dest not in src
rsync -av --stats src/ dest/           # summary statistics at the end
```

## Exclude patterns
```
rsync -av --exclude='*.log' src/ dest/         # skip .log files
rsync -av --exclude='node_modules' src/ dest/  # skip a directory
rsync -av --exclude-from=.rsyncignore src/ dest/  # patterns from file
```

## Over SSH (remote sync)
```
rsync -avz user@host:/remote/src/ ./local/    # pull from remote
rsync -avz ./local/ user@host:/remote/dest/   # push to remote
rsync -avz -e "ssh -p 2222" src/ user@host:dest/  # custom SSH port
```

## Backup & safety
```
rsync -av --backup --suffix=.old src/ dest/   # keep .old copies
rsync -av --update src/ dest/                 # skip newer files in dest
rsync -av --checksum src/ dest/               # compare by checksum, not time
```

## Mirror (exact copy)
```
rsync -av --delete --exclude='.git' src/ dest/   # mirror, skip .git
rsync -avzP user@host:/data/ ./backup/           # -P = progress + partial
```

> `-a` = archive (recursive, preserve perms/times), `-v` verbose, `-z` compress, `--delete` mirrors exactly.
