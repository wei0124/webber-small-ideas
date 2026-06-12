# kubectl — Kubernetes CLI
<!-- tags: devops, containers, orchestration -->

## Cluster info
```
kubectl cluster-info                          # show cluster endpoint
kubectl get nodes                             # list all nodes
kubectl get namespaces                        # list namespaces
kubectl config current-context                # show current context
```

## Pods
```
kubectl get pods                              # list pods in default namespace
kubectl get pods -A                           # list pods across all namespaces
kubectl get pods -o wide                      # extra info (IP, node)
kubectl describe pod <name>                   # detailed pod info
kubectl logs <pod>                            # show pod logs
kubectl logs -f <pod>                         # follow logs
kubectl exec -it <pod> -- /bin/sh             # shell into a pod
```

## Deployments
```
kubectl get deployments                       # list deployments
kubectl create deployment web --image=nginx   # create a deployment
kubectl scale deployment web --replicas=3     # scale replicas
kubectl rollout status deployment web         # check rollout progress
kubectl rollout undo deployment web           # rollback last update
kubectl set image deployment/web nginx=nginx:1.25  # update container image
```

## Services & networking
```
kubectl get services                          # list services
kubectl expose deployment web --port=80 --type=LoadBalancer
kubectl port-forward svc/web 8080:80          # local port forwarding
kubectl get ingress                           # list ingress resources
```

## Config & secrets
```
kubectl get configmaps                        # list config maps
kubectl create configmap app --from-file=app.conf
kubectl get secrets                           # list secrets
kubectl create secret generic db --from-literal=password=s3cret
```

## Cleanup
```
kubectl delete pod <name>                     # delete a pod
kubectl delete deployment <name>              # delete a deployment
kubectl delete -f manifest.yaml               # delete from manifest
kubectl delete all --all                      # nuclear option
```

> `kubectl get` for listing, `kubectl describe` for details, `kubectl logs` for debugging — `-A` for all namespaces.
