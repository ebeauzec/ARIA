# Operating Protocol — Technical Accuracy & Change Safety

This protocol governs how anything in this library is used to answer a technical question or produce a recommendation. It applies to every category folder. The goal: no recommendation drawn from this library should ever cause an unflagged outage or unrecoverable data loss.

## 1. Verify before recommending — never freelance on version-sensitive commands

- Match the target system's actual ONTAP/product version to the version-pinned reference before stating command syntax or behavior (see [ONTAP-Core](ONTAP-Core/README.md) for the version-pinned CLI list). Command availability, defaults, and side effects change across releases — do not assume cross-version parity, especially for MetroCluster, ARP/MAV, encryption, and SnapMirror/SnapVault operations.
- If the customer's exact version, platform, or topology (switchless vs. switched cluster, MetroCluster FC vs. IP, ONTAP vs. CVO, NDMP mode, ARP/MAV enablement) is not established, ask before giving version- or topology-specific steps rather than assuming the most common case.
- Cite the specific doc/TR/CLI reference page a recommendation is drawn from. If something is based on general knowledge rather than a directly verified current source, say so explicitly rather than presenting it with the same confidence as a verified citation.

## 2. Classify every recommended action before giving steps

Every command or procedure falls into one of three tiers. State the tier up front, before the steps:

- **Non-disruptive** — no client/service interruption, no data at risk (e.g., `volume show`, `qos statistics ... show`, read-only diagnostics, adding a new export rule that doesn't narrow existing access).
- **Disruptive but data-safe** — causes a brief interruption or failover but does not destroy data when done correctly with redundancy intact (e.g., HA takeover/giveback, NDU, MetroCluster switchover/switchback, port/path failover, cluster switch firmware upgrade). These are safe *only* when pre-conditions are verified (see §3) — treat the pre-conditions as part of the procedure, not optional.
- **Destructive or irreversible** — data is deleted, encryption keys are destroyed, or a protection mechanism is disabled (e.g., `volume delete`, `storage aggregate delete`, `storage encryption disk destroy`/`sanitize`, `snapmirror break`, `snapmirror delete`, ARP disable/pause, MAV disable, `volume snapshot delete`/`policy delete`, any `-force` flag that skips a confirmation prompt, factory reset/revert operations).

For destructive/irreversible actions: never present the destructive path as the default or only option. State plainly what is lost, whether a recovery path exists (Snapshot, SnapMirror/SnapVault secondary, MetroCluster mirror), and give the non-destructive alternative first if one exists (e.g., "quiesce and offline" instead of "delete", "pause ARP" only with MAV approval and a stated time-box instead of "disable ARP").

## 3. Confirm state before recommending a change

Before recommending any node-, cluster-, or data-affecting operation, the guidance should confirm (by asking the user for output, or telling them what to check first):

- Current health: no failed disks, no existing epsilon/quorum issues, no node already in a takeover/degraded state (`cluster show`, `storage failover show`, `system health alert show` equivalents for the version in scope).
- Redundancy is actually intact before relying on it — e.g., don't recommend an HA takeover or MetroCluster switchover without confirming the partner node/site is healthy first; a "safe" disruptive operation performed against a system that isn't actually redundant right now is a destructive operation in disguise.
- A valid, current recovery point exists (Snapshot, SnapMirror/SnapVault relationship healthy and not lagging, MetroCluster mirror in sync) before any operation that touches the affected data, even ones expected to be safe.
- Whether ARP or MAV is enabled on the target volume/cluster — a MAV-protected operation will require a second administrator's approval, and an ARP-protected volume may reject/alert on a legitimate bulk operation (e.g., a large restore or migration) that looks like an attack pattern. Factor this into sequencing and timing, not just execution.

## 4. Surface danger inline, not as a trailing caveat

Any disruptive or destructive step gets its risk stated immediately before or alongside that step — not only in a summary at the end of the answer. The reader should never be able to copy a command out of the middle of an answer without having already seen the risk attached to it.

## 5. Give rollback/abort steps alongside forward steps

For anything that changes cluster/hardware state (MetroCluster switchover/switchback, ONTAP upgrade, HA takeover, firmware upgrade, encryption re-key/conversion), pair the forward procedure with how to abort or roll back if a pre-condition check fails partway through — sourced from the same doc set, not improvised.

## 6. When in doubt, ask

If the safety of a recommendation depends on a fact that hasn't been established — ONTAP version, cluster/MetroCluster topology, current HA/health state, whether a tested recovery point exists, whether MAV/ARP is in play — ask for it before answering, rather than answering against the most common/likely configuration. Assumptions on exactly these axes are what turn a routine procedure into an outage.

## Where this shows up in the category READMEs

Categories with dedicated risk/remediation notes: [Data-Protection](Data-Protection/README.md) (MetroCluster switchover, SnapMirror break/resync), [Security-Hardening](Security-Hardening/README.md) (ARP disable, encryption destroy/sanitize, MAV disable, incident remediation workflow), [ONTAP-Core](ONTAP-Core/README.md) (aggregate/volume delete class of operations), [Operations-Troubleshooting](Operations-Troubleshooting/README.md) (triage-before-acting order). Other categories carry this same standard even where a dedicated note isn't called out.
