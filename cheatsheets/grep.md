# grep — search text with patterns
<!-- tags: text-processing, search -->

## Basic search
```
grep "error" app.log                   # find lines matching "error"
grep -i "warning" app.log              # case-insensitive match
grep -w "fail" app.log                 # match whole word only
grep -E "err|warn" app.log             # extended regex (OR patterns)
```

## Search files recursively
```
grep -r "TODO" src/                    # recursive search in directory
grep -rn "TODO" src/                   # ... with line numbers
grep -rl "TODO" src/                   # list filenames only
grep -rI "TODO" src/                   # skip binary files
```

## Context around matches
```
grep -n "panic" app.log                # show line numbers
grep -C 3 "panic" app.log              # 3 lines before AND after
grep -B 2 "panic" app.log              # 2 lines before match
grep -A 5 "panic" app.log              # 5 lines after match
```

## Invert, count, quiet
```
grep -v "debug" app.log                # invert: lines NOT matching
grep -c "error" app.log                # count matching lines
grep -q "error" app.log && echo found  # quiet: exit code only
```

## Combine with pipes
```
ps aux | grep nginx                    # find a running process
cat access.log | grep -c "404"         # count 404 responses
grep -rn "import" . | grep -v test     # exclude test files from results
```

> Use `-r` for recursive, `-n` for line numbers, `-v` to invert — stack them as `-rnv`.
