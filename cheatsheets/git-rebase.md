# git rebase — replay commits onto a new base
<!-- tags: git, version-control -->

## Basic rebase
```
git rebase main                   # replay current branch on top of main
git rebase --onto main old new    # move commits new..HEAD onto main
```

## Interactive rebase (clean up history)
```
git rebase -i HEAD~3              # edit the last 3 commits
```
In the editor, change `pick` to:
```
reword   # change the commit message
squash   # merge this commit into the previous one
fixup    # like squash, but discard this commit's message
drop     # delete the commit entirely
```

## When you hit conflicts
```
# edit the conflicting files, then:
git add <file>
git rebase --continue            # proceed to the next commit
git rebase --skip                # drop the current commit
git rebase --abort               # bail out, restore original state
```

> Golden rule: never rebase commits you've already pushed to a shared branch —
> it rewrites history and breaks everyone else's clone.
