# curl — transfer data with URLs
<!-- tags: networking, http, api -->

## GET requests
```
curl https://api.example.com/users             # basic GET
curl -s https://api.example.com/users          # silent (no progress)
curl -o file.zip https://example.com/file.zip  # save to file
curl -O https://example.com/file.zip           # save with remote name
```

## Headers & redirects
```
curl -I https://example.com                    # headers only (HEAD)
curl -H "Accept: application/json" URL         # set a request header
curl -H "Authorization: Bearer TOKEN" URL      # bearer auth
curl -L https://example.com                    # follow redirects
```

## POST requests
```
curl -X POST -d "name=alice" URL               # form-encoded POST
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"alice"}' URL                 # JSON body POST
curl -d @body.json URL                         # POST from a file
curl -F "file=@photo.jpg" URL                  # multipart file upload
```

## Auth & cookies
```
curl -u user:pass URL                          # basic auth
curl -c cookies.txt URL                        # save cookies
curl -b cookies.txt URL                        # send cookies
```

## Inspect & debug
```
curl -v https://example.com                    # verbose (show full exchange)
curl -w "\n%{http_code} %{time_total}s\n" -o /dev/null -s URL
curl -k https://self-signed.example.com        # skip TLS verify
```

## Download with progress
```
curl -# -L -o app.deb URL                      # progress bar + follow redirect
curl -C - -o bigfile.iso URL                   # resume interrupted download
```

> `-s` silent, `-L` follow redirects, `-H` headers, `-d` data — combine `-v` to debug the full exchange.
