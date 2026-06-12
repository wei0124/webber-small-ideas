# sed — stream editor for text transforms
<!-- tags: text-processing, scripting -->

## Substitute (find & replace)
```
sed 's/old/new/' file.txt              # replace first match per line
sed 's/old/new/g' file.txt             # replace ALL matches per line
sed 's|/old/path|/new/path|g' file.txt # use | delimiter for paths
```

## Edit in-place
```
sed -i 's/foo/bar/g' file.txt          # save changes back to file
sed -i.bak 's/foo/bar/g' file.txt      # save with a .bak backup
```

## Delete lines
```
sed '/^$/d' file.txt                   # delete blank lines
sed '/^#/d' file.txt                   # delete comment lines
sed '3d' file.txt                      # delete line 3
sed '2,5d' file.txt                    # delete lines 2 through 5
sed '$d' file.txt                      # delete the last line
```

## Print specific lines
```
sed -n '5,10p' file.txt                # print lines 5-10 only
sed -n '/error/p' file.txt             # print lines matching "error"
sed -n '1p;$p' file.txt                # print first and last line
```

## Transform text
```
sed 's/^/# /' file.txt                 # prepend "# " to every line
sed 's/$/ -- done/' file.txt           # append text to every line
sed 's/^[[:space:]]*//' file.txt       # strip leading whitespace
sed '2i\NEW LINE HERE' file.txt        # insert a line before line 2
sed '4a\NEW LINE HERE' file.txt        # append a line after line 4
```

> `s/old/new/g` is the bread and butter — `-i` saves in-place, `-n` + `p` prints only what you want.
