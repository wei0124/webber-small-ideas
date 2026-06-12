# find — search for files and directories
<!-- tags: files, search -->

## By name
```
find . -name "*.py"               # all .py files under current dir
find . -iname "readme*"           # case-insensitive name match
find /etc -maxdepth 1 -name "*.conf"
```

## By type
```
find . -type f                    # files only
find . -type d                    # directories only
find . -type l                    # symlinks only
```

## By size / time
```
find . -size +10M                 # larger than 10 megabytes
find . -mtime -1                  # modified in the last 24 hours
find . -mmin -30                  # modified in the last 30 minutes
```

## Act on results
```
find . -name "*.tmp" -delete                  # delete matches
find . -name "*.log" -exec rm {} \;           # run a command per match
find . -name "*.txt" -exec grep -l TODO {} +  # batch into fewer calls
```

> `-exec ... +` is much faster than `-exec ... \;` because it batches
> arguments instead of spawning one process per file.
