# ssh — secure shell & tunnels
<!-- tags: networking, security, devops -->

## Connect
```
ssh user@host                     # basic connection
ssh -p 2222 user@host             # non-default port
ssh -i ~/.ssh/mykey user@host     # use a specific private key
```

## Keys
```
ssh-keygen -t ed25519 -C "you@example.com"   # generate a modern key
ssh-copy-id user@host                         # install your key on the server
```

## Port forwarding (tunnels)
```
ssh -L 8080:localhost:80 user@host   # local  : reach remote:80 via localhost:8080
ssh -R 9000:localhost:3000 user@host # remote : expose local:3000 on remote:9000
ssh -D 1080 user@host                # dynamic: SOCKS proxy on localhost:1080
```

## Run a command & exit
```
ssh user@host "df -h"             # run one command remotely
ssh user@host < script.sh         # pipe a local script to the remote shell
```

> Add hosts to `~/.ssh/config` (Host, HostName, User, Port, IdentityFile) so you
> can just type `ssh myserver`.
