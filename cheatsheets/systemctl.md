# systemctl — manage systemd services

## Service lifecycle
```
systemctl start nginx                  # start a service
systemctl stop nginx                   # stop a service
systemctl restart nginx                # restart a service
systemctl reload nginx                 # reload config (no restart)
systemctl status nginx                 # show status + recent logs
```

## Enable at boot
```
systemctl enable nginx                 # start on boot
systemctl disable nginx               # don't start on boot
systemctl is-enabled nginx            # check if enabled
```

## Inspect services
```
systemctl list-units --type=service           # list all services
systemctl list-units --type=service --state=running
systemctl cat nginx                           # view the unit file
systemctl show nginx                          # all properties
systemctl daemon-reload                       # reload after editing a unit
```

## Logs with journalctl
```
journalctl -u nginx                  # all logs for a service
journalctl -u nginx -f               # follow logs in real-time
journalctl -u nginx --since today    # logs since midnight
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -n 50           # last 50 log lines
journalctl -p err                   # errors only (priority)
```

## Troubleshoot
```
systemctl --failed                   # list failed units
systemctl reset-failed               # clear failed state
journalctl -xe                       # recent errors + context
```

> `systemctl status` first — then `journalctl -u <name> -f` to follow logs live.
