# Fresh R-5 stopped-run cleanup result — 2026-10-03

Authority:
[HARD STOP acceptance and cleanup authority](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md)

Operator: Codex  
Host: `oracle-test`  
Scope: read-only capacity diagnosis, deletion of the six explicitly authorized
retained paths, and verification only

## Diagnosis

The server's root filesystem was not exhausted:

```text
/dev/sda1 ext4 45G total, 5.9G used, 39G available (14% used)
```

`/tmp` is a separate memory-backed filesystem with its own fixed capacity and
user-quota mount option:

```text
tmpfs on /tmp: size=486792k (475.4 MiB), usrquota
before cleanup: 380.3 MiB used, 95.1 MiB available
inodes before cleanup: 7.8K used of 1.0M
```

The `quota` userspace command is not installed, so it reported no per-user
limit. The mount capacity alone explains the failure: retained fresh-run paths
used approximately 377 MiB, principally 94 MiB for the checkout, 64 MiB for
the package cache and 219 MiB for the incomplete build root. Inodes were not
exhausted.

## Cleanup

Codex deleted exactly the six paths enumerated in the authority record. The
post-delete check reported every path `ABSENT`.

After cleanup:

```text
/tmp: 4.8 MiB used, 470.6 MiB available (2% used)
inodes: 258 used of 1.0M
```

The deletion is permanent; the stopped run remains preserved by its closed
repository handback and review, not by its disposable host directories.

## Consequence for the new run

Cleanup restored the tmpfs but did not remove its 475.4 MiB ceiling. A new run
must not place its checkout, caches, provisioned root, work tree, evidence or
pytest tree under `/tmp`. The suitable existing filesystem is `/var/tmp` on
the root ext4 filesystem, which had 39 GiB available at inspection. The new
assignment must re-observe capacity before creation and retain the original
first-failure HARD STOP behavior.

Bounded inspection and cleanup authority is now exhausted. No current
`oracle-test` access is authorized until a reviewed new assignment is accepted
and activated.
