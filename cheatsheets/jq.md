# jq — command-line JSON processor
<!-- tags: text-processing, json -->

## Extract fields
```
jq '.name' package.json                # get a top-level key
jq '.scripts.start' package.json       # get a nested key
jq '.dependencies | keys' package.json # list keys of an object
jq '.[] | .name' data.json             # get "name" from every item
```

## Format & inspect
```
jq '.' data.json                       # pretty-print JSON
jq 'keys' data.json                    # list top-level keys
jq 'length' data.json                  # count elements or keys
jq 'type' data.json                    # show type (object, array, etc)
```

## Filter arrays
```
jq '.[] | select(.age > 30)' users.json       # filter by condition
jq '.[] | select(.status == "active")' j      # filter by string match
jq '[.[] | select(.score > 80)]' scores.json  # wrap results back in []
jq '.[] | select(.name | startswith("A"))' j  # string prefix filter
```

## Transform with map
```
jq 'map(.name)' users.json             # extract one field from array
jq 'map({id, email})' users.json       # pick multiple fields
jq 'map(.price * 1.1)' items.json      # compute new values
jq 'group_by(.role) | map({role: .[0].role, count: length})' u.json
```

## Raw output & shell use
```
jq -r '.name' package.json             # raw string (no quotes)
jq -r '.[] | .email' users.json        # one email per line
curl -s api.example.com | jq '.data'   # pipe HTTP response into jq
jq -r '.[] | "\(.id) \(.name)"' j      # string interpolation
```

> `.` = current value, `.key` = access field, `[]` = iterate array, `|` = pipe — `-r` for raw output.
