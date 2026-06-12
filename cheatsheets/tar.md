# tar — archive & compress files
<!-- tags: files, compression -->

## Create archives
```
tar -czf archive.tar.gz folder/      # create gzip-compressed archive
tar -cjf archive.tar.bz2 folder/      # create bzip2 archive (smaller, slower)
tar -cf archive.tar folder/           # create uncompressed archive
```

## Extract archives
```
tar -xzf archive.tar.gz               # extract gzip archive
tar -xzf archive.tar.gz -C /tmp/out   # extract into a specific directory
tar -xf archive.tar                   # extract uncompressed archive
```

## Inspect without extracting
```
tar -tzf archive.tar.gz               # list contents of gzip archive
tar -tf  archive.tar                  # list contents of plain archive
```

## Handy flags
```
tar -czvf out.tar.gz folder/          # -v = verbose, show each file
tar --exclude='*.log' -czf a.tgz dir/ # skip files matching a pattern
```

> Mnemonic: **c**reate, e**x**tract, **t** list — add **z** for .gz, **f** before the filename.
