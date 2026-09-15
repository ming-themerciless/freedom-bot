# Proposed r6 amendment — D1 and D2

Date: 2026-09-14. Authorization: **C-P5.0-LAB-I-R1**.
Raised by: the [remediation handback](phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
Ruled on by: Codex's independent re-review and the Acceptance Authority.

**Accepted by Peter Duscha on 2026-09-15 and applied to
[runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).**
**r6 is now the contract; this file records what was proposed and approved.**

**Correction to the application, 2026-09-15.** The delta below only adds text.
Applied as written, it left r6's operative steps still specifying `renameat2`:
§1.3.2's permitted uses, P2, M1, §2.3.3, §2.4, T1, T6, §5.10, §6.2's syscall
list, V6, I3 and §10. It also replaced rather than extended §6.4's descriptor
row. Its §6.4 `ctypes` row claimed a route to `execveat` that nothing
establishes. And its interruption paragraph described a stop between `linkat`
and `unlinkat` as if nothing were published, when the final name already is.
Those are corrected in r6, with regressions, and listed in the
[correction handback](phase-5-0-reserved-laboratory-r6-d1-d2-correction-handback.md).
The handback returns to Codex for review before the separately authorized
read-only target preflight begins. The text below is left as approved, so the
difference stays visible.

*Historical, 2026-09-14:* Codex's 2026-09-13 review found both deviations
technically acceptable *"if the contract is amended"* and said in as many words
that the implementation is not retroactive authorization. So the amendment is
written here, as a separately reviewable delta, and r6 keeps saying what it
says until somebody accepts it.

**Before its acceptance** *(historical)*:

* **V6 stays a preflight item and is not closed.** The implemented publication
  path no longer depends on `RENAME_NOREPLACE`, which is a fact about the
  implementation and not a disposition of V6. The twelve unconfirmed target
  facts remain twelve.
* **D2's listing descriptor stays an addition to an accepted inventory**,
  reported rather than authorized. `descriptors.CONTRACT_GAPS` says so in the
  source.

---

## D1 — the exclusive publication substitute

### The finding

r6 §6.2 lists `renameat2(2)` with `RENAME_NOREPLACE` among the syscalls the
design newly reaches, and §§1.4.2 P2 and 2.3.3(9)–(10) specify it for every
exclusive publication. **It is not reachable.** Python 3.12's `os` module
exposes `renameat` and not `renameat2`, and the one `ctypes` exception in this
repository is granted to `case_program._prctl_get_securebits` and to nothing
else — `tests/phase_5_0_evidence/test_no_execution.py` asserts that shape
against the source, and widening it is a decision about the trusted computing
base rather than an implementation detail.

### The proposed amendment

**Add to §6.2, after the paragraph beginning "`RENAME_NOREPLACE` requires
filesystem support":**

> **Exclusive publication, and the substitute this design uses.** The
> `renameat2(RENAME_NOREPLACE)` above is not reachable from the interpreter the
> 2026-09-06 Option B ruling names: Python 3.12's `os` exposes `renameat` and
> not `renameat2`, and the single `ctypes` exception is granted elsewhere. The
> substitute is `linkat(dirfd, tmp, dirfd, name, 0)` followed by
> `unlinkat(dirfd, tmp, 0)`.
>
> `link(2)` fails with `EEXIST` when the destination exists **[D]**, so the
> final name is claimed exclusively by the kernel rather than by a check the
> caller performs, and there is no window in which the final name resolves to
> an object this run did not write.
>
> **The interruption state, named because it is the whole of the difference.**
> `renameat2` leaves no temporary on success. This sequence has **two
> syscalls** and therefore **two names**, and a process that stops between them
> leaves the temporary in place with both names referring to one inode. That
> state is already a refusal: §2.13.2b reports a leftover publication temporary,
> §5.9 blocks every successor on it, and nothing removes one automatically. The
> substitute therefore **fails closed**, and the recovery is the existing
> operator step that removes the temporary by absolute path.
>
> **The temporary is preserved and never cleaned by a retry.** A retry over an
> unexplained temporary is a write into a state nobody has established.

**Add to §6.4's table, replacing the `ctypes` row's "After" cell:**

> | The one `ctypes` exception | `case_program._prctl_get_securebits` | **unchanged.** `execveat` and the two ioctls are reached through `os` and `fcntl`; `renameat2` is not reached at all, and the substitute above is why |

**Add to §7, as a note under V6:**

> **V6's scope narrows and V6 does not close.** No publication path in this
> design depends on `RENAME_NOREPLACE` after the §6.2 amendment above: the
> exclusive publications use `linkat`/`unlinkat` and the non-exclusive ones use
> a plain `renameat`. V6 remains an unperformed preflight observation and one
> of the twelve unconfirmed target facts; what changes is that no other item
> now waits on it.

### What a reviewer is being asked to rule on

1. whether the two-syscall, two-name interruption state is acceptable given
   that it is already a blocking, reported, never-auto-cleaned condition; and
2. whether narrowing V6's scope — **without** closing it — is the right
   disposition, or whether V6 should be struck from the preflight entirely once
   nothing depends on it.

**The alternative this proposal rejects, and why.** A second `ctypes` exception
for `renameat2` would make the deviation unnecessary. It is rejected here
because it widens the trusted syscall surface to avoid documenting a decision,
which is precisely the move the prompt forbids.

---

## D2 — the listing descriptor

### The finding

r6 §2.5 makes `readdir` of the recovery parent **the** discovery mechanism —
*"no index file is needed and none is proposed"* — and §5.11's ledger survey
lists its directory. §1.3.3's inventory enumerates **no descriptor for either
listing**, and §1.3.2 lists `readdir` among neither the traversal descriptor's
permitted uses (`dirfd` of the `*at()` calls, and `fstat` of itself) nor the
synchronizable descriptor's (`fsync`, and `fstat` of itself).

So the accepted contract requires an operation it provides no descriptor for.
This is a gap in the contract rather than an implementation choice, which is
why it is raised rather than taken.

### The proposed amendment

**Add a row to §1.3.3's inventory, after D19:**

> | **D20** | **`listing_fd`** | **any directory this design lists: the recovery parent, `<run-id>`, the ledger directory and `/etc/postgresql/16/main`** | **`O_RDONLY\|O_NOFOLLOW\|O_DIRECTORY`, obtained by `openat(<that directory's **traversal** descriptor>, ".", …)`** | **one listing only, closed before the call that opened it returns** | **`getdents`/`readdir`, and nothing else** | **never** |

**Add to §1.3.2, after the two-column table:**

> **A third, short-lived descriptor exists for one operation.** `readdir`
> requires a descriptor with read access, which the traversal descriptor does
> not have **[D]**, and the synchronizable descriptor may not be used as a
> `dirfd`, which is how a reader tells the two apart by their use sites. D20 is
> opened `"."`-relative to the traversal descriptor of the directory being
> listed, so it resolves **one component that is the directory itself** and
> reaches no object the traversal descriptor does not already refer to. It is
> used for exactly one `readdir` and closed before the listing returns.
>
> It is **never** retained, never transferred, never synchronized and never used
> as a `dirfd`. A listing is a read of names and establishes nothing about any
> object those names resolve to; every such object is reached afterwards through
> the traversal descriptor and compared, exactly as it is today.

**Add to §6.2's syscall list:** `getdents64(2)`, on a directory descriptor
opened `O_RDONLY` for one listing.

**Add to §6.4's table:**

> | Descriptors opened per run | the chain in two modes | **unchanged in kind. One short-lived `O_RDONLY` directory descriptor per listing, closed immediately. No new privilege, no new path, no retained descriptor** |

### What a reviewer is being asked to rule on

1. whether the short-lived `"."`-relative descriptor is the right answer, or
   whether §1.3.2's permitted-use set should instead be widened so the
   **synchronizable** descriptor may also `readdir` — it already has read
   access, and the cost is that the two descriptors are then no longer told
   apart by their use sites, which is the property §1.3.2 relies on; and
2. whether the permission delta really stays at ten items. This proposal says
   it does: no new path, group, identity, capability, unit or retained
   descriptor is required.

---

## What neither amendment does

Neither adds a `ctypes` exception, widens the trusted syscall surface beyond
the two calls named above, changes the ten-item §7 provisioning delta, confirms
a target fact, closes a finding or authorizes any execution. Both are
documentation deltas for a maintainer to accept or refuse as a pair with the
implementation they describe.
