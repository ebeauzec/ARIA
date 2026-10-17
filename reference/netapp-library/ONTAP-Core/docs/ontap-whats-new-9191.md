# What's new in ONTAP 9.19.1
Source: https://docs.netapp.com/us-en/ontap/release-notes/whats-new-9191.html
Fetched: 2026-07-07

Last updated: 06/11/2026

Learn about the new capabilities available in ONTAP 9.19.1.

For details about known issues, limitations, and upgrade cautions in recent ONTAP 9 releases, refer to the [ONTAP 9 Release Notes](https://library.netapp.com/ecm/ecm_download_file/ECMLP2492508) (NetApp account sign-in required).

- [ONTAP MetroCluster new features](https://docs.netapp.com/us-en/ontap-metrocluster/releasenotes/mcc-new-features.html)
- [New and enhanced ONTAP software features for NetApp AFX storage systems](https://docs.netapp.com/us-en/ontap-afx/release-notes/whats-new-9171.html)
- [New and enhanced ONTAP software features for NetApp ASA r2 storage systems](https://docs.netapp.com/us-en/asa-r2/release-notes/whats-new-9171.html)
- [New and enhanced support for AFF, ASA, and FAS systems and supported switches](https://docs.netapp.com/us-en/ontap-systems/whats-new.html)
- [Updates to the ONTAP REST API](https://docs.netapp.com/us-en/ontap-automation/whats_new.html)
- To upgrade to the latest version of ONTAP, see [Prepare to upgrade ONTAP](https://docs.netapp.com/us-en/ontap/upgrade/create-upgrade-plan.html)

## Data protection

| Update | Description |
| --- | --- |
| [SnapMirror active sync supports transparent application failover for AIX](https://docs.netapp.com/us-en/ontap/snapmirror-active-sync/interoperability-reference.html) | SnapMirror active sync for symmetric active/active supports transparent failover with zero RPO for AIX on 2-node clusters. |
| [SnapMirror cloud support limits increased to 100 S3 buckets](https://docs.netapp.com/us-en/ontap/data-protection/cloud-backup-with-snapmirror-task.html#restore-from-the-cloud) | SnapMirror cloud increases the number of S3 buckets supported to 100. |
| [SnapMirror synchronous supports tamperproof snapshot locking](https://docs.netapp.com/us-en/ontap/snaplock/snapshot-lock-concept.html) | You can use tamperproof snapshot locking with SnapMirror synchronous. |
| [SnapMirror synchronous supports replicating scheduled snapshots to the destination volume](https://docs.netapp.com/us-en/ontap/data-protection/snapmirror-synchronous-disaster-recovery-basics-concept.html) | You can replicate scheduled snapshots to the destination volume with SnapMirror synchronous. |

## NAS

| Update | Description |
| --- | --- |
| [NAS performance enhancement](https://docs.netapp.com/us-en/ontap/flexcache/index.html) | ONTAP 9.19.1 allows more CPU resources to process listing requests of small NAS directories. This benefits customers with hundreds to thousands of clients simultaneously listing the same small NAS directory (2 MB or less, ~25,000 files). Reduces the need for workarounds such as local FlexCache volumes to support high client counts performing directory listings. For lower client counts, performance is not negatively impacted. Automatic, no configuration required. |

## Networking

| Update | Description |
| --- | --- |
| Manage the NFS versions the SVM supports | NFSv4.2 support is managed independently of NFSv4.1 settings, allowing each SVM to advertise or suppress NFSv4.2 capabilities as needed. NFSv4.2 is enabled by default on a new NFS service unless explicitly disabled. See: [Enable or disable NFSv4.2 for ONTAP SVMs](https://docs.netapp.com/us-en/ontap/nfs-admin/enable-disable-nfs-task.html), [Enable NAS storage for Linux servers using NFS with ONTAP System Manager](https://docs.netapp.com/us-en/ontap/task_nas_enable_linux_nfs.html) |
| [LIF failover enhancement](https://docs.netapp.com/us-en/ontap/concepts/path-failover-concept.html#nas-path-failover) | The system-defined failover group policy dynamically expands failover targets for NAS data LIFs to potentially include any available ports in the broadcast domain on any available node in the cluster. Applicable to any failover group. Prior to 9.19.1, LIFs with this policy could fail over to only one other node in the cluster; if that node was out of quorum, the LIF would not fail over even if other nodes were available. |

## SAN

| Update | Description |
| --- | --- |
| [Support for direct-attachment FC configurations](https://docs.netapp.com/us-en/ontap/san-config/configure-fc-nvme-hosts-ha-pairs-reference.html) | FC switches are not needed to connect FC and FC-NVMe hosts to ONTAP storage; hosts can connect directly to FC adapter ports on AFF, ASA, and FAS systems. Useful for remote sites and hybrid environments. |
| [Support for active-active multipathing on AFF systems](https://docs.netapp.com/us-en/ontap/san-admin/multipath-automatic-lif-failover-support.html) | AFF systems support active-active multipathing in SAN environments. All paths within the HA pair owning the LUN/namespace are active-optimized, so on storage failover the host does not wait for ALUA/ANA transition of failover paths to resume I/O — reducing failover time, previously available only on ASA systems. |
| [Enhanced support for automatic SAN LIF failover](https://docs.netapp.com/us-en/ontap/san-admin/multipath-automatic-lif-failover-support.html) | Automatic LIF failover is supported on AFF and ASA systems for iSCSI protocol LIFs in active-active and active-active-scsi-only multipath configurations, and for NVMe/TCP protocol LIFs in active-active multipath configurations. |
| [Foreign LUN import support for iSCSI protocol](https://docs.netapp.com/us-en/ontap-fli/get-started/learn-about-data-migration.html) | Foreign LUN Import (FLI) supports the iSCSI protocol for backend connectivity. |

## S3 object storage

| Update | Description |
| --- | --- |
| [ONTAP S3 support for conditional writes and deletes with enforcement](https://docs.netapp.com/us-en/ontap/s3-config/create-modify-bucket-policy-task.html) | Conditions can enforce conditional writes for object uploads and conditional deletes for object deletes, preventing overwrites or unintended deletes. |
| [ONTAP S3 keys](https://docs.netapp.com/us-en/ontap/s3-config/regenerate-access-keys.html) | To maintain user access to S3 resources if the original access key expires, cluster administrators can generate a second access key for each S3 user. |

## Security

| Update | Description |
| --- | --- |
| ARP workload characteristics removed from System Manager UI | System Manager no longer displays Autonomous Ransomware Protection (ARP) workload characteristics (baseline/surge statistics) since surge activity was frequently misinterpreted as an actual attack or something requiring manual adjustment. ARP behavior/detection is unchanged; only the System Manager presentation is affected. Surge statistics remain available via ONTAP CLI and REST API for advanced analysis. |
| [ARP support for SnapMirror synchronous and SnapMirror active sync](https://docs.netapp.com/us-en/ontap/anti-ransomware/use-cases-restrictions-concept.html#supported-configurations) | ARP/AI supports volumes participating in SnapMirror synchronous (NAS and SAN) and SnapMirror active sync SAN relationships on supported platforms: primary volumes in SnapMirror synchronous relationships on FAS, AFF, and AFX; primary volumes in SnapMirror active sync SAN relationships on AFF and ASA r2. Runs on the active read-write primary volume, creating primary-only ARP snapshots with ML-based ransomware detection. |
| [TLS offload configuration](https://docs.netapp.com/us-en/ontap/networking/configure-tls-offload.html) | You can configure TLS offload to improve TLS post-handshake performance using resources on supported Ethernet cards, offloading encryption/decryption to reduce CPU overhead and improve performance. |

## Storage resource management enhancements

| Update | Description |
| --- | --- |
| [Enhanced volume space reporting](https://docs.netapp.com/us-en/ontap/concepts/capacity-measurements.html) | `volume show-space` output now includes the directory used for the space reporting. |
| [Support for modifying default settings controlling automatic QoS throughput ceiling increases](https://docs.netapp.com/us-en/ontap/performance-admin/guarantee-throughput-qos-task.html) | You can modify default settings that control how QoS policy groups automatically increase the throughput ceiling in response to short-term higher-performance needs. Not modifiable in ONTAP 9.18.1 and earlier. |

## System Manager

| Update | Description |
| --- | --- |
| [New SVM dashboard](https://docs.netapp.com/us-en/ontap/concept-svm-admin-dashboard-sm.html) | A dedicated dashboard lets SVM administrators monitor and manage their own SVMs — particularly useful in tenanted ONTAP environments where the cluster admin can provide a per-tenant SVM dashboard. |

## Upgrade

| Update | Description |
| --- | --- |
| [Enhanced reporting for automated upgrade pre-checks](https://docs.netapp.com/us-en/ontap/upgrade/automated-pre-checks.html) | Errors and warnings are now displayed separately during automated pre-upgrade checks, to help identify issues that must be resolved before upgrading. |
