# Recommended ESXi host and other ONTAP settings
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vsphere-settings.html
Fetched: 2026-07-07

NetApp has developed optimal ESXi host settings for both NFS and block protocols, plus specific guidance for multipathing and HBA timeout settings for proper behavior with ONTAP, based on NetApp/VMware internal testing.

These values are easily set via ONTAP tools for VMware vSphere: from the ONTAP tools overview page, scroll to the bottom and click "Apply recommended Settings" in the ESXi Host compliance portlet.

## Recommended host settings (all currently supported ONTAP versions)

**ESXi Advanced Configuration**

| Host Setting | NetApp Recommended Value | Reboot Required |
| --- | --- | --- |
| VMFS3.HardwareAcceleratedLocking | Keep default (1) | No |
| VMFS3.EnableBlockDelete | Keep default (0), can be changed if needed. See "Space Reclamation for VMFS5 Virtual Machines" | No |
| VMFS3.EnableVMFS6Unmap | Keep default (1). See "VMware vSphere APIs: Array Integration (VAAI)" | No |

**NFS Settings**

| Host Setting | NetApp Recommended Value | Reboot Required |
| --- | --- | --- |
| newSyncInterval | If not using vSphere CSI for Kubernetes, set per VMware KB 386364 | No |
| Net.TcpipHeapSize | vSphere 6.0+: 32. All other NFS configs: 30 | Yes |
| Net.TcpipHeapMax | 512MB for most vSphere 6.x releases. Default (1024MB) for 6.5U3, 6.7U3, and 7.0+ | Yes |
| NFS.MaxVolumes | vSphere 6.0+: 256. All other NFS configs: 64 | No |
| NFS41.MaxVolumes | vSphere 6.0+: 256 | No |
| NFS.MaxQueueDepth | vSphere 6.0+: 128 | Yes |
| NFS.HeartbeatMaxFailures | 10 for all NFS configs | No |
| NFS.HeartbeatFrequency | 12 for all NFS configs | No |
| NFS.HeartbeatTimeout | 5 for all NFS configs | No |
| SunRPC.MaxConnPerIP | vSphere 7.0–8.0: 128. Ignored in ESXi releases after 8.0 | No |

**FC/FCoE Settings**

| Host Setting | NetApp Recommended Value | Reboot Required |
| --- | --- | --- |
| Path selection policy | RR (round robin) when FC paths with ALUA are used; FIXED for all other (older, non-ALUA) configurations to prevent proxy I/O | No |
| Disk.QFullSampleSize | 32 for all configurations (helps prevent I/O errors) | No |
| Disk.QFullThreshold | 8 for all configurations (helps prevent I/O errors) | No |
| Emulex FC HBA timeouts | Use default value | No |
| QLogic FC HBA timeouts | Use default value | No |

**iSCSI Settings**

| Host Setting | NetApp Recommended Value | Reboot Required |
| --- | --- | --- |
| Path selection policy | RR (round robin) for all iSCSI paths | No |
| Disk.QFullSampleSize | 32 for all configurations | No |
| Disk.QFullThreshold | 8 for all configurations | No |

> **Note:** NFS advanced configuration option MaxQueueDepth may not work as intended on VMware vSphere ESXi 7.0.1 and 7.0.2. See VMware KB 86331.

## ONTAP tools default settings for FlexVol volumes and LUNs

| ONTAP Tool Setting | Default |
| --- | --- |
| Snapshot reserve (-percent-snapshot-space) | 0 |
| Fractional reserve (-fractional-reserve) | 0 |
| Access time update (-atime-update) | False |
| Minimum readahead (-min-readahead) | False |
| Scheduled snapshots | None |
| Storage efficiency | Enabled |
| Volume guarantee | None (thin provisioned) |
| Volume Autosize | grow_shrink |
| LUN space reservation | Disabled |
| LUN space allocation | Enabled |

## Multipath settings for performance

Not currently configured by ONTAP tools automatically — NetApp suggests these manually:

- For non-ASA systems in high-performance environments, or when testing a single-LUN datastore, consider changing the round-robin (VMW_PSP_RR) PSP load-balance setting from the default IOPS value of 1000 to a value of 1. See VMware KB 2069356.
- vSphere 6.7 U1 introduced a latency load-balance mechanism for Round Robin PSP (also available with HPP for NVMe namespaces, and with vSphere 8.0u2+ for iSCSI/FCP LUNs). It factors I/O bandwidth and path latency into path selection. **NetApp recommends the latency option** in environments with non-equivalent path connectivity (e.g., unequal hop counts) or when using a NetApp ASA system. See "Change Default Parameters for Latency Round Robin" in VMware docs.

## Additional documentation

- FCP/iSCSI with vSphere 7: "Use VMware vSphere 7.x with ONTAP"
- FCP/iSCSI with vSphere 8: "Use VMware vSphere 8.x with ONTAP"
- NVMe-oF with vSphere 7: "NVMe-oF Host Configuration for ESXi 7.x with ONTAP"
- NVMe-oF with vSphere 8: "NVMe-oF Host Configuration for ESXi 8.x with ONTAP"

*Page last updated: 07/30/2025*
