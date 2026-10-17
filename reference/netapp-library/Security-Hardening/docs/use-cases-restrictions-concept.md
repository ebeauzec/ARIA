# ONTAP Autonomous Ransomware Protection use cases and considerations
Source: https://docs.netapp.com/us-en/ontap/anti-ransomware/use-cases-restrictions-concept.html
Fetched: 2026-07-07

Autonomous Ransomware Protection (ARP) is available for NAS workloads beginning with ONTAP 9.10.1 and SAN workloads beginning in ONTAP 9.17.1. Before deploying ARP, you should be aware of the recommended uses, supported configurations, and performance implications.

## Supported and unsupported configurations

### Suitable workloads

- Databases on NFS or SAN storage
- Windows or Linux home directories (without ARP/AI, greater possibility of false positives during the learning period since new file extensions may be created)
- Images and video (e.g., health care records, EDA data)

### Unsuitable workloads

- Workloads with a high frequency of file create/delete operations (hundreds of thousands of files in a few seconds; e.g., test/dev). ARP cannot distinguish application-driven file surges from ransomware activity.
- Workloads where the application or host encrypts data — reduces ARP effectiveness for entropy analysis, though ARP can still work based on file activity (delete, overwrite, create/rename with new extension) and file type.

### Supported configurations

- NAS NFS and SMB FlexVol volumes: beginning ONTAP 9.10.1
- SAN FlexVol volumes (iSCSI, FC, NVMe): beginning ONTAP 9.17.1
- MetroCluster: beginning ONTAP 9.10.1

Feature support by ONTAP version (Y = supported):

| Feature | 9.18.1 | 9.17.1 | 9.16.1 | 9.15.1 | 9.14.1 | 9.13.1 | 9.12.1 | 9.11.1 | 9.10.1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SnapMirror asynchronous (volumes) | Y | Y | Y | Y | Y | Y | Y | N | N |
| SVM disaster recovery (SnapMirror async) | Y | Y | Y | Y | Y | Y | Y | N | N |
| SVM data mobility (`vserver migrate`) | Y | Y | Y | Y | Y | Y | Y | N | N |
| FlexGroup volumes | Y | Y | Y | Y | Y | Y | N | N | N |
| Multi-admin verification | Y | Y | Y | Y | Y | Y | N | N | N |
| ARP/AI with automatic updates | Y | Y | Y | N | N | N | N | N | N |
| ARP/AI default enablement | Y | N | N | N | N | N | N | N | N |

Note: ONTAP 9.16.1 and 9.17.1 do not provide ARP/AI support for FlexGroup volumes — after upgrade, FlexGroup volumes enabled for ARP continue with the pre-ARP/AI model. Beginning in ONTAP 9.18.1, FlexGroup volumes use ARP/AI.

ARP/AI default enablement (9.18.1+) applies to AFF A-series/C-series, ASA, and ASA r2 systems: automatically enables ARP/AI on all new volumes after a 12-hour grace period post-upgrade, or immediately for new 9.18.1 installs. Existing volumes must be enabled manually.

#### SnapMirror and ARP interoperability

Beginning with ONTAP 9.12.1, ARP is supported on SnapMirror asynchronous destination volumes. ARP is NOT supported with SnapMirror synchronous or SnapMirror active sync.

If a SnapMirror source volume is ARP-enabled, the destination automatically acquires the ARP configuration state (dry-run/enabled), training data, and ARP-created snapshots — no explicit enablement required. No ARP processing occurs on the read-only destination; when converted to read-write, ARP is automatically enabled with no additional learning required.

In ONTAP 9.10.1 and 9.11.1, SnapMirror does NOT transfer ARP state/training data/snapshots — ARP must be explicitly enabled in learning mode after RW conversion.

#### ARP and virtual machines

ARP is supported with VMs on VMware; detection behaves differently for changes inside vs. outside the VM. Not recommended for workloads with many highly compressed (7z, ZIP) or encrypted files (password-protected PDF/DOC/ZIP) within the VM.

- **Changes outside the VM**: ARP can detect file extension changes on an NFS volume outside the VM if a new extension enters encrypted or a file extension changes.
- **Changes inside the VM**: If ransomware changes files inside the VM without external changes, ARP detects the threat if default entropy is low (e.g., .txt, .docx, .mp4). For ONTAP 9.16.1 and earlier, ARP creates a protective snapshot but does NOT generate a threat alert (external extensions untampered). Beginning with SAN support in ONTAP 9.17.1, ARP additionally generates a threat alert if it detects an entropy anomaly inside the VM. If files are naturally high entropy (.gzip, password-protected), detection is limited — snapshots may still be taken but no alerts triggered.
- For SAN, ARP analyzes entropy statistics at the volume level.

Note: Detection of attacks occurring within a VM is available only for FlexVol volumes; not available if the VM datastore is on a FlexGroup volume in ONTAP 9.18.1+.

### Unsupported configurations

ARP is not supported in ONTAP S3 environments. Unsupported volume configurations:

- FlexGroup volumes (ONTAP 9.10.1–9.12.1). Supported (pre-ARP/AI model) beginning 9.13.1–9.17.1; ARP/AI-supported beginning 9.18.1.
- FlexCache volumes (supported on origin FlexVol, not cache volumes)
- Offline volumes
- SnapLock volumes
- SnapMirror active sync
- SnapMirror synchronous
- SnapMirror asynchronous (ONTAP 9.10.1 and 9.11.1 only; supported from 9.12.1)
- Restricted volumes
- Root volumes of storage VMs
- Volumes of stopped storage VMs
- FlexVol to FlexGroup conversion (ARP must be disabled before conversion)

## ARP performance and frequency considerations

ARP has minimal impact on throughput and peak IOPS, depending on workload:

| Workload characteristics | Recommended volume limit per node | Performance degradation when exceeded |
| --- | --- | --- |
| Read-intensive or compressible data | 150 | 4% of maximum IOPS |
| Write-intensive, incompressible data | 60 | NAS: 10% (ONTAP 9.15.1-), 5% (9.16.1+); SAN: 5% (9.17.1+) |

System performance is not degraded beyond these percentages regardless of how many volumes exceed the recommended limits. Because ARP analytics run in a prioritized sequence, analytics run less frequently per volume as protected volume count increases.

Note: Enabling ARP by default on large numbers of new volumes might increase system resource usage; consider space demands from competing processes like snapshots.

## Volume limits for ARP by platform

Beginning with ONTAP 9.18.1, ARP supports increased volume limits by platform/CPU core count:

| Platform type | Maximum ARP-enabled volumes per node |
| --- | --- |
| Low-end (up to 20 CPU cores) | 250 |
| Medium (up to 64 CPU cores) | 500 |
| High-end (more than 64 CPU cores) | 1000 |

Note: CPU core count applies to each individual node in a 2-node HA pair.

## Multi-admin verification with ARP-protected volumes

Beginning with ONTAP 9.13.1, MAV can be enabled for additional security with ARP — ensures 2+ authenticated admins are required to turn off ARP, pause ARP, or mark a suspected attack as false positive on a protected volume. Requires defining MAV group administrators and creating MAV rules for `security anti-ransomware volume disable`, `security anti-ransomware volume pause`, and `security anti-ransomware volume attack clear-suspect` commands. Each administrator in the MAV group must approve each new rule request.

Beginning with ONTAP 9.14.1, ARP offers alerts (disabled by default) for ARP snapshot creation and new file extension observation, settable at volume or SVM level via `security anti-ransomware vserver event-log modify` or `security anti-ransomware volume event-log modify`.

## Next steps

- Enable Autonomous Ransomware Protection
- Enable MAV for ARP-protected volumes

Last updated: 04/03/2026
</content>
