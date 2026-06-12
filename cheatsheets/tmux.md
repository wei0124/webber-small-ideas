# tmux — terminal multiplexer
<!-- tags: terminal, productivity -->

## Sessions
```
tmux                              # start a new session
tmux new -s work                  # start a named session
tmux ls                           # list all sessions
tmux attach -t work               # attach to a named session
tmux kill-session -t work         # kill a named session
tmux kill-server                  # kill all sessions
```

## Windows (tabs)
```
Ctrl-b c                          # create a new window
Ctrl-b n                          # next window
Ctrl-b p                          # previous window
Ctrl-b ,                          # rename the current window
Ctrl-b &                          # close the current window
Ctrl-b w                          # list windows (interactive)
```

## Panes (splits)
```
Ctrl-b %                          # split vertically (left / right)
Ctrl-b "                          # split horizontally (top / bottom)
Ctrl-b arrow                      # move to adjacent pane
Ctrl-b x                          # close the current pane
Ctrl-b {                          # swap pane with the previous one
Ctrl-b }                          # swap pane with the next one
Ctrl-b space                      # cycle through pane layouts
```

## Copy mode
```
Ctrl-b [                          # enter copy mode (scroll with arrows/PgUp/PgDn)
Ctrl-b ]                          # paste from tmux buffer
q                                 # quit copy mode
```

## Resize panes
```
Ctrl-b Ctrl-arrow                 # resize pane in a direction
Ctrl-b z                          # zoom (toggle full-screen pane)
```

## Session management
```
Ctrl-b d                          # detach from current session
Ctrl-b s                          # list sessions (interactive switch)
Ctrl-b $                          # rename the current session
```

> `Ctrl-b` is the prefix key — `c` for new window, `%`/`"` to split, `d` to detach, `tmux ls` to see sessions.
