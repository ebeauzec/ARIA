# Learn about NetApp Ransomware Resilience
Source: https://docs.netapp.com/us-en/data-services-ransomware-resilience/concept-ransomware-resilience.html
Fetched: 2026-07-07

Ransomware attacks can block access to data; attackers demand ransom for release/decryption. Per IDC, victims often experience multiple attacks; disruption can last one day to several weeks.

NetApp Ransomware Resilience protects data from ransomware attacks, covering file shares for NAS (NFS/CIFS) and SAN (FC, iSCSI, NVMe) storage. Supported on-premises and on Cloud Volumes ONTAP (AWS, Google Cloud, Azure), Azure NetApp Files, and Amazon FSx for NetApp ONTAP, all via NetApp Console. Backup targets: AWS, Google Cloud, Microsoft Azure, NetApp StorageGRID.

## Ransomware Resilience at the data layer

Security posture layers:
- **Outermost layer**: firewalls, IDS, VPNs
- **Network security**: segmentation, traffic monitoring, encryption
- **Identity security**: authentication, access controls, identity management
- **Data security**: data protection, backups, recovery — Ransomware Resilience operates here

## What you can do with Ransomware Resilience

- **Identify**: workloads across NetApp on-prem NAS/SAN systems and Console; recommends resiliency improvements
- **Protect**: enable backups, snapshots, ransomware protection strategies
- **Detect**: anomalies that might indicate ransomware attacks
- **Respond**: automatically initiate a locked point-in-time snapshot (cannot be deleted accidentally/maliciously); immutable end-to-end protection at source and destination
- **Recover**: orchestrate recovery across NetApp technologies; recommend best recovery options
- **Govern**: implement and monitor ransomware protection strategy

## Benefits

- Discovers workloads, existing snapshot/backup schedules, ranks importance
- Evaluates ransomware protection posture with dashboard and recommendations
- AI/ML-driven data protection recommendations, one-click access
- Protects file share data
- Real-time ransomware detection on primary storage using AI
- Automated response: snapshot creation, alerts
- Curated recovery to meet RPO policies via NetApp Backup and Recovery orchestration
- RBAC to govern feature/operation access

## Cost

New deployments get a 30-day free trial (no charge). If you have both Backup and Recovery and Ransomware Resilience, common protected data is billed by Ransomware Resilience only.

A workload counts as "protected" (against purchased capacity/PAYGO) when a detection policy is enabled with at least one snapshot or backup policy. Workloads with detection but no backup/snapshot policy are "at risk" and don't count against capacity. Billing is per GB of protected-workload data (as reported by ONTAP) before efficiencies, based on logical capacity of the active file system (snapshot space excluded).

## Licensing

Plans: free trial, pay-as-you-go subscription, or bring-your-own-license. Requires a NetApp ONTAP One license. The Ransomware Resilience license does not include other NetApp products, but can use Backup and Recovery even without a separate license for it.

For anomalous user behavior detection, uses NetApp Autonomous Ransomware Protection (ML model within ONTAP), included in the Ransomware Resilience license.

## NetApp Console

Ransomware Resilience is accessed through NetApp Console — centralized management of NetApp storage/data services across on-prem and cloud. No license/subscription needed to start using Console; charges apply only when deploying Console agents in the cloud. Some data services accessed via Console are licensed/subscription-based separately.

## How Ransomware Resilience works

| Feature | Description |
| --- | --- |
| IDENTIFY | Finds on-prem/cloud NAS (NFS/CIFS) and SAN (FC/iSCSI/NVMe) data across Console-attached systems; associates data from ONTAP and Backup/Recovery APIs with workloads; discovers protection level (snapshots, backup policies, on-box detection); assigns business priority based on protection posture and snapshot frequency |
| PROTECT | Actively monitors workloads; orchestrates Backup and Recovery + ONTAP APIs to apply policies |
| DETECT | Integrated ML model detects anomalous encryption/activity; dual-layer detection (primary storage detection + automated snapshot response); identifies suspect files, maps attacks to workloads via ARP/ARP-AI and FPolicy |
| RESPOND | Shows file activity, user activity, entropy for forensic review; initiates quick snapshots via ONTAP/ARP/FPolicy |
| RECOVER | Determines best snapshot/backup and recommended RPA via Backup and Recovery, ONTAP, ARP, FPolicy; orchestrates recovery of VMs, file shares, block storage |
| GOVERN | Assigns ransomware protection strategies; monitors outcomes |

### Attack types

| Attack type | Description |
| --- | --- |
| Encryption (entropy) | Abnormal IOPS patterns, data entropy, non-standard file suffixes |
| Encryption (user behavior) | Anomalous file read/write/rename activity by a specific user |
| Data breach | Anomalous file read access patterns by a specific user |
| Data destruction | Mass deletion of files by a specific user |
| Suspicious user behavior | Anomalous behavior beyond breach/destruction/encryption scope |

Note: identifying the specific responsible user requires configuring user behavior detection; check limitations for support.

## Supported backup targets, systems, workload data sources

Backup targets: AWS S3, Google Cloud Platform, Microsoft Azure Blob, NetApp StorageGRID.

Supported systems:

| Environment | Protocol | Supported versions |
| --- | --- | --- |
| Amazon FSx for NetApp ONTAP* | CIFS, NFS, SAN | N/A |
| Azure NetApp Files | CIFS & NFS | N/A |
| Cloud Volumes ONTAP for AWS | CIFS & NFS | 9.11.1+ |
| Cloud Volumes ONTAP for AWS | SAN (iSCSI/NVMe) | 9.17.1+ |
| Cloud Volumes ONTAP for GCP | CIFS & NFS | 9.11.1+ |
| Cloud Volumes ONTAP for GCP | SAN (iSCSI/NVMe) | 9.17.1+ |
| Cloud Volumes ONTAP for Azure | CIFS & NFS | 9.12.1+ |
| Cloud Volumes ONTAP for Azure | SAN (iSCSI/NVMe) | 9.17.1+ |
| ONTAP (on-premises) | CIFS & NFS | 9.11.1+ |
| ONTAP (on-premises) | SAN (iSCSI/NVMe) | 9.17.1+ |
| Google Cloud NetApp Volumes | CIFS, NFS, SAN (iSCSI/NVMe) | N/A |

*Amazon FSx for NetApp ONTAP uses ARP, not ARP/AI.

Notes:
- User activity detection not supported for Azure NetApp Files or Google Cloud NetApp Volumes.
- ARP/AI requires ONTAP 9.16+. ONTAP ransomware protection doesn't support FabricPool FlexCache, FlexGroup volumes, consistency group mount point volumes, mount path volumes, offline volumes, or DP volumes — review supported/unsupported ONTAP configurations separately.

Supported workload data sources: Block storage; Databases (Microsoft SQL Server, Oracle); File shares; VMware datastores.

## Key terms

- **Protection**: ensuring regular snapshots and immutable backups to a different security domain via protection policies
- **Workload**: a logical grouping of storage resources within a system (e.g., a file share)

Last updated: 06/08/2026
</content>
