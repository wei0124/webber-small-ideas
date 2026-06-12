# awk — field processing & reporting
<!-- tags: text-processing, scripting -->

## Print columns
```
awk '{print $1}' file.txt              # print first column
awk '{print $1, $3}' file.txt          # print columns 1 and 3
awk '{print NR, $0}' file.txt          # add line numbers
```

## Field separators
```
awk -F: '{print $1}' /etc/passwd       # split on colon
awk -F, '{print $2}' data.csv          # split on comma
awk -F'\t' '{print $1}' data.tsv       # split on tab
```

## Filter rows
```
awk '$3 > 100' file.txt                # rows where column 3 > 100
awk '$1 == "error"' app.log            # rows where column 1 is "error"
awk '/WARN/ {print $0}' app.log        # rows matching regex
awk 'NF > 0' file.txt                  # skip blank lines
```

## Math & aggregation
```
awk '{sum += $1} END {print sum}' file.txt        # sum column 1
awk '{sum += $1} END {print sum/NR}' file.txt     # average column 1
awk '{if ($1 > max) max=$1} END {print max}' f    # find max value
awk 'END {print NR}' file.txt                     # count total lines
```

## Formatting output
```
awk '{printf "%-20s %s\n", $1, $3}' file.txt     # left-aligned columns
awk -F: '{printf "User: %-15s Home: %s\n", $1, $6}' /etc/passwd
```

## BEGIN and END blocks
```
awk 'BEGIN {print "---"} {print $1} END {print "---"}' f
awk 'BEGIN {FS=","; OFS="\t"} {print $1,$2}' data.csv
```

> `$0` = whole line, `$1..$N` = fields, `NR` = row number, `NF` = field count — `-F` sets the delimiter.
