# make — build automation
<!-- tags: build, automation, scripting -->

## Basic usage
```
make                              # run the first (default) target
make <target>                     # run a specific target
make -f other.mk                  # use a different Makefile
make -n <target>                  # dry run: print commands without executing
```

## Common targets
```
make all                          # build everything
make clean                        # remove build artefacts
make install                      # install built artefacts
make test                         # run the test suite
make help                         # list available targets (if defined)
```

## Variables
```
make CC=clang                     # override a variable from the command line
make -j4                          # run 4 jobs in parallel
make -C subdir                    # run make in a subdirectory
```

## Debugging
```
make -d <target>                  # print debug info
make --trace <target>             # trace recipe execution
make -p                           # dump the internal database
```

## Useful flags
```
make -s                           # silent mode (don't echo commands)
make -k                           # keep going on errors
make -B <target>                  # force rebuild (always remake)
make --warn-undefined-variables   # warn on undefined variables
```

> `make` reads `Makefile` in the current directory — `-j` for parallel builds, `-n` to preview, `make clean` to start fresh.
