# docker — container basics
<!-- tags: containers, devops, networking -->

## Containers
```
docker ps                              # list running containers
docker ps -a                           # list all (including stopped)
docker run -d --name web -p 8080:80 nginx     # run detached, map port
docker run -it ubuntu bash             # run interactive shell
docker exec -it <id> bash              # shell into a running container
docker stop <id>                       # stop a container
docker rm <id>                         # remove a stopped container
docker logs -f <id>                    # follow container logs
```

## Images
```
docker images                          # list local images
docker pull nginx:latest               # pull an image
docker build -t myapp:1.0 .           # build from Dockerfile
docker rmi <image>                     # remove an image
docker image prune -a                  # remove all unused images
```

## Docker Compose
```
docker compose up -d                   # start services detached
docker compose down                    # stop and remove services
docker compose logs -f                 # follow all service logs
docker compose ps                      # list running services
docker compose exec web bash           # shell into a service
```

## Cleanup
```
docker system prune                    # remove unused data (safe)
docker system prune -a --volumes       # remove ALL unused (aggressive)
docker volume ls                       # list volumes
docker volume prune                    # remove unused volumes
```

> `docker ps` to see what's running, `docker logs -f` to watch output, `docker system prune` to reclaim disk.
