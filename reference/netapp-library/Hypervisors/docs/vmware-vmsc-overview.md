# vSphere Metro Storage Cluster with ONTAP
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware_vmsc_overview.html
Fetched: 2026-07-07

VMware's vSphere hypervisor can be deployed as a stretched cluster referred to as a vSphere Metro Storage Cluster (vMSC).

vMSC solutions are supported with both NetApp MetroCluster and SnapMirror active sync (formerly SnapMirror Business Continuity / SMBC), providing advanced business continuity if one or more failure domains suffer a total outage. Resilience to different failure modes depends on the configuration chosen.

> **Note:** This documentation replaces previously published technical report *TR-4128: vSphere on NetApp MetroCluster*.

## Continuous availability solutions for vSphere environments

ONTAP is a flexible, scalable storage platform providing SAN (FCP, iSCSI, NVMe-oF) and NAS (NFS v3 and v4.1) services for datastores. NetApp AFF, ASA, and FAS systems also offer S3 and SMB/CIFS for guest storage access.

**NetApp MetroCluster** uses ONTAP HA (controller failover/CFO) to protect against controller failures, plus local SyncMirror technology, Cluster Failover On Disaster (CFOD), hardware redundancy, and geographic separation for high availability. SyncMirror synchronously mirrors data across both halves of the MetroCluster config — writing to a local plex (actively serving) and a remote plex (normally not serving). Hardware redundancy covers controllers, storage, cables, switches (fabric MetroCluster), and adapters.

**NetApp SnapMirror active sync**, available on non-MetroCluster systems and ASA r2 systems, offers datastore-granular protection with FCP and iSCSI SAN protocols. You can protect the entire vMSC or selectively protect high-priority workloads. It offers active-active access to both local and remote sites (unlike MetroCluster's active-standby model). Beginning with ONTAP 9.15.1, SnapMirror active sync supports symmetric active/active capability — bidirectional synchronous replication lets both LUN copies serve I/O locally. Before 9.15.1, only asymmetric active/active was supported (secondary site I/O proxied to the primary LUN copy).

To build a VMware HA/DRS cluster across two sites: ESXi hosts are managed by a vCenter Server Appliance (VCSA); vSphere management, vMotion, and VM networks connect via a redundant network between sites; the vCenter Server managing the HA/DRS cluster connects to ESXi hosts at both sites and should use vCenter HA.

See also:
- "How Do You Create and Configure Clusters in the vSphere Client" (VMware docs)
- "VMware vSphere Metro Storage Cluster Recommended Practices" (VMware docs)

## What is vSphere Metro Storage Cluster?

vMSC is a certified configuration protecting VMs and containers against failures, using stretched storage concepts with ESXi host clusters distributed across failure domains (racks, buildings, campuses, cities). NetApp MetroCluster and SnapMirror active sync provide RPO=0 protection to host clusters, ensuring data availability even if a complete physical/logical site fails. A storage device used in vMSC must undergo VMware's vMSC certification process — see the VMware Storage Compatibility Guide.

Related design guidance:
- "VMware vSphere support with NetApp MetroCluster" (VMware KB 2031038)
- "VMware vSphere support with NetApp SnapMirror Business Continuity" (VMware KB 83370, now SnapMirror active sync)

NetApp MetroCluster deployment options for vSphere:
- Stretch MetroCluster
- Fabric MetroCluster

See MetroCluster documentation for specific design/deployment guidance.

SnapMirror active sync deployment options:
- Asymmetric
- Symmetric Active Sync (ONTAP 9.15.1+)

See the SnapMirror Business Continuity (smbc) docs at docs.netapp.com/us-en/ontap/smbc/index.html for specific design/deployment guidance.

*Page last updated: 08/05/2025*
