# Learn about ONTAP Autonomous Ransomware Protection
Source: https://docs.netapp.com/us-en/ontap/anti-ransomware/
Fetched: 2026-07-07

Beginning with ONTAP 9.10.1, ONTAP administrators can enable Autonomous Ransomware Protection (ARP) to perform workload analysis in NAS (NFS and SMB) environments to proactively detect and warn about abnormal activity that might indicate a ransomware attack. ARP is built directly into ONTAP for integrated control and coordination with ONTAP's other features. ARP operates in real-time, processing data as it's written to or read from the file system.

ARP creates locked snapshots at regular intervals in addition to scheduled snapshots. Snapshot retention is adjusted dynamically: snapshots are recycled quickly when no unusual activity is detected, and snapshots taken before a detected attack are retained longer for investigation and recovery.

## Licenses and enablement

ARP requires a license, included with the ONTAP One license.

| ONTAP releases | License |
| --- | --- |
| ONTAP 9.11.1 and later | `Anti_ransomware` |
| ONTAP 9.10.1 | `MT_EK_MGMT` (Multi-Tenant Key Management) |

- Upgrading from 9.10.1 to 9.11.1+ with ARP already configured: no new license needed. New ARP configurations require the new license.
- Reverting from 9.11.1+ to 9.10.1 with ARP enabled via Anti_ransomware license: warning message, may need reconfiguration.

### Enablement options

- **Automatic default enablement on new volumes**: Beginning with ONTAP 9.18.1, ARP is enabled by default automatically on all new volumes for AFF A-series, AFF C-series, ASA, and ASA r2 systems (not applied to unsupported volumes/configs). Takes effect after a 12-hour grace period following upgrade, or immediately for new 9.18.1 installs, provided an ARP license is installed. You can opt out during the grace period at the cluster level (System Manager or CLI). Must manually enable ARP on existing volumes.
- **Manual default enablement on new volumes**: If disabled at cluster level, can manually enable ARP by default at the SVM level. For ONTAP 9.17.1 and earlier, this is the only way to enable ARP by default on new volumes.
- **ARP enablement on all/specific existing volumes**: Beginning with 9.18.1, enable ARP on all existing volumes from the cluster level (Cluster > Security > Anti-ransomware > Enable on all existing volumes), or enable per-volume.

## ONTAP ransomware protection strategy

Effective protection requires layered defenses: FPolicy, snapshots, SnapLock, Active IQ Digital Advisor, plus ARP as an additional layer.

## What ARP detects

ARP protects against denial-of-service style attacks (data withheld until ransom paid), using:

- Identification of incoming data as encrypted or plain text
- **Entropy** (NAS and SAN): randomness of data in a file
- **File extension types** (NAS only): non-conforming extensions
- **File IOPS** (NAS only, 9.11.1+): surge in abnormal volume activity with data encryption

ARP detects the spread of most ransomware attacks after only a small number of files are encrypted, responds automatically, and alerts. No ransomware detection system guarantees complete safety — ARP is an extra layer of defense.

## ARP modes

After enablement, ARP enters a learning period to establish a baseline before transitioning to active detection. Behavior differs by ONTAP version, volume type, and protocol.

### NAS environments

| Mode | Description | Volume types/versions |
| --- | --- | --- |
| Learning | Develops alert profile from entropy, file extension, file IOPS. Recommended 30 days; 9.13.1+ automates the switch (may occur earlier). Beginning 9.16.1, FlexVol volumes only have active mode (auto-transition). 9.16.1–9.17.1: FlexGroup volumes not yet ARP/AI-supported, still use older model with learning period. Beginning 9.18.1: only active mode for FlexVol and FlexGroup. | FlexVol 9.10.1–9.15.1; FlexGroup 9.13.1–9.17.1 |
| Evaluation | 2–4 week evaluation to determine baseline encryption behavior; detection/alerts can occur during this period. Check via `security anti-ransomware volume show` → Block device detection status. | NAS volumes with ONTAP-detected hypervisor virtual disks, ONTAP 9.17.1P5+ |
| Active | Evaluate flagged extensions; act or mark false positive (updates alert profile). | All supported versions, FlexVol and FlexGroup |

### SAN environments

| Mode | Description | Volume types/versions |
| --- | --- | --- |
| Evaluation | 2–4 week evaluation for baseline encryption behavior; ARP/AI provides immediate active protection during evaluation. | FlexVol, ONTAP 9.17.1+ |
| Active | Check via `security anti-ransomware volume show` → Block device detection status = `Active_suitable_workload` means entropy monitoring successful; ARP auto-adjusts adaptive threshold. | FlexVol, ONTAP 9.17.1+ |

## Threat assessment and ARP snapshots

### ARP thresholds

- **Low**: Earliest abnormality detection (e.g., new file extension). Only in versions prior to 9.16.1 (pre-ARP/AI). Customizable detection parameters from 9.11.1. In 9.10.1, escalation threshold to moderate is 100+ files.
- **Moderate**: High entropy detected or multiple never-seen-before-extension files. Baseline detection level in 9.16.1+ with ARP/AI. Triggers EMS notification. Low threats don't alert by default; 9.14.1+ allows modifying default alert settings.

View moderate threats in System Manager Events or via `security anti-ransomware volume show`.

### ARP snapshots

Created proactively on early attack signs; may occur at regular intervals for legitimate apps too (not necessarily anomalous). If attack confirmed, probability escalates to Moderate with notification.

Version differences:
- Modify retention settings: from 9.11.1
- Intervals/anomaly response: from 9.17.1, ARP snapshots generated at regular intervals for NAS and SAN plus anomaly response; prepended identifiable name
- SnapMirror synchronous/active sync (9.19.1 RC+): ARP snapshots created/retained only on primary; not replicated to secondary; must re-enable ARP on recovery volume after failover

Note: Volume-level restore (`volume snapshot restore`) on SnapMirror sync/active sync SAN volumes might require temporarily quiescing/breaking the relationship; FlexClone or file-level restore from primary can often avoid this.

| Feature | ONTAP 9.17.1+ | ONTAP 9.16.1 and earlier |
| --- | --- | --- |
| Creation trigger | Fixed 4-hour intervals + attack confirmation ("periodic"/"attack" snapshot) | High entropy, new file extension (≤9.15.1), file ops surge (≤9.15.1) |
| Prepended name | "Anti_ransomware_periodic_backup" / "Anti_ransomware_attack_backup" | "Anti_ransomware_backup" |
| Deletion behavior | Locked, cannot be deleted by admin | Locked, cannot be deleted by admin |
| Max snapshot count | 6 (configurable) | 6 (configurable) |
| Retention | Normally 12 hours. NAS: if attack confirmed, retained until clear-suspect. SAN/VM datastores: if confirmed, retained 10 days (configurable) | Based on trigger conditions; retained until clear-suspect if attack confirmed |
| Clear-suspect action | 24h false-positive / 7 days true-positive | 24h false-positive / 7 days true-positive (not available pre-9.16.1) |
| Expiration time | Set for all snapshots | None |

## Recovering data after an attack

ARP builds on ONTAP data protection/DR to respond. Confirm attack vs false positive first; restore volume using ARP snapshot if confirmed. Locked snapshots can't be deleted normally; marking false positive deletes the locked copy. Can recover individual files from snapshots instead of full volume revert.

## Multi-admin verification protection for ARP

Beginning with ONTAP 9.13.1, recommended to enable MAV so two or more authenticated admins are required for ARP configuration changes.

## ARP with Artificial Intelligence (ARP/AI)

Beginning with ONTAP 9.16.1, ARP adopts a machine-learning model detecting evolving ransomware forms with 99% accuracy in NAS environments. Pre-trained outside ONTAP on open-source forensic datasets (no customer data used); model included on-box, not accessible/modifiable via CLI/API.

No learning period with ARP/AI — active immediately for:
- NAS FlexVol: ONTAP 9.16.1+
- NAS FlexGroup: ONTAP 9.18.1+
- SAN: ONTAP 9.17.1+ (active even during evaluation period)

Existing/new volumes with ARP already enabled get ARP/AI protection automatically after upgrade to a supported version.

### ARP/AI automatic updates

Frequent automatic updates outside regular ONTAP release cadence, via automatic updates setting or manually. Beginning 9.16.1, security updates available via System Manager.

## ARP vs ARP/AI comparison

| Feature | ARP | ARP/AI |
| --- | --- | --- |
| ONTAP versions | 9.10.1–9.15.1 | 9.16.1+ (9.15.1 tech preview) |
| Detection method | File activity, entropy, extension types | ML model trained on forensic datasets; entropy + file behavior |
| Learning period | 30-day (auto-switch 9.13.1+) | None — active immediately |
| Volume support | FlexVol 9.10.1+; FlexGroup 9.13.1+; SAN not supported | FlexVol 9.16.1+; FlexGroup 9.18.1+; SAN 9.17.1+ (with evaluation) |
| Snapshot creation | Triggered by entropy/extension/ops surge | Fixed 4-hour intervals + attack confirmation |
| Snapshot retention | Until admin clears suspect | 12h default; 24h (false positive) / 7 days (confirmed) |
| Updates | Static, updated with ONTAP upgrades | Automatic, independent of ONTAP releases |
| Deployment | Manual per-volume/SVM default | Manual per-volume/SVM default; cluster-level default enablement 9.18.1+ for supported systems |
| Evaluation period | N/A | Required for SAN (2-4 weeks) |

Last updated: 04/08/2026
</content>
