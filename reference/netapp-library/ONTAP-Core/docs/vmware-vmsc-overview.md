# vSphere Metro Storage Cluster with ONTAP
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware_vmsc_overview.html
Fetched: 2026-07-07

Last updated: 08/05/2025

VMware's industry-leading vSphere hypervisor can be deployed as a stretched cluster referred to as a vSphere Metro Storage Cluster (vMSC).

vMSC solutions are supported with both NetApp MetroCluster and SnapMirror active sync (formerly known as SnapMirror Business Continuity, or SMBC) and provide advanced business continuity if one or more failure domains suffer a total outage. The resilience to different modes of failure depends on which configuration options you choose.

Note: This documentation replaces previously published technical report *TR-4128: vSphere on NetApp MetroCluster*.

## Continuous Availability Solutions for vSphere Environments

ONTAP architecture is a flexible and scalable storage platform that provides SAN (FCP, iSCSI, and NVMe-oF) and NAS (NFS v3 and v4.1) services for datastores. The NetApp AFF, ASA, and FAS storage systems use the ONTAP operating system to offer additional protocols for guest storage access, like S3 and SMB/CIFS.

NetApp MetroCluster uses NetApp's HA (controller failover, CFO) function to protect against controller failures. It also includes local SyncMirror technology, cluster failover on disaster (CFOD), hardware redundancy, and geographical separation to achieve high levels of availability. SyncMirror synchronously mirrors data across the two halves of the MetroCluster configuration by writing data to two plexes: the local plex (on the local shelf) actively serving data and the remote plex (on the remote shelf) normally not serving data. Hardware redundancy is put in place for all MetroCluster components such as controllers, storage, cables, switches (used with fabric MetroCluster), and adapters.

NetApp SnapMirror active sync, available on non-MetroCluster systems and ASA r2 systems, offers datastore-granular protection with FCP and iSCSI SAN protocols. It allows you to either protect the entire vMSC or selectively protect high-priority workloads. It offers active-active access to both local and remote sites, unlike NetApp MetroCluster which is an active-standby solution. Beginning with ONTAP 9.15.1, SnapMirror active sync supports a symmetric active/active capability, enabling read and write I/O operations from both copies of a protected LUN with bidirectional synchronous replication, enabling both LUN copies to serve I/O operations locally. Before ONTAP 9.15.1, SnapMirror active sync only supports asymmetric active/active configurations, in which data on the secondary site is proxied to the primary copy of a LUN.

To create a VMware HA/DRS cluster across two sites, ESXi hosts are used and managed by a vCenter Server Appliance (VCSA). The vSphere management, vMotion, and virtual machine networks are connected through a redundant network between the two sites. The vCenter Server managing the HA/DRS cluster can connect to the ESXi hosts at both sites and should be configured using vCenter HA.

Refer to [How Do You Create and Configure Clusters in the vSphere Client](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-vcenter-esxi-management/GUID-F7818000-26E3-4E2A-93D2-FCDCE7114508.html) to configure vCenter HA.

You should also refer to [VMware vSphere Metro Storage Cluster Recommended Practices](https://www.vmware.com/docs/vmw-vmware-vsphere-metro-storage-cluster-recommended-practices).

## What is vSphere Metro Storage Cluster?

vSphere Metro Storage Cluster (vMSC) is a certified configuration that protects virtual machines (VMs) and containers against failures. This is achieved by using stretched storage concepts along with clusters of ESXi hosts, which are distributed across different failure domains such as racks, buildings, campuses, or even cities. The NetApp MetroCluster and SnapMirror active sync storage technologies are used to provide a zero recovery point objective (RPO=0) protection to the host clusters. The vMSC configuration is designed to ensure that data is always available even if a complete physical or logical "site" fails. A storage device that is part of the vMSC configuration must be certified after undergoing a successful vMSC certification process. All the supported storage devices can be found in the [VMware Storage Compatibility Guide](https://compatibilityguide.broadcom.com/).

Additional design guideline references:

- [VMware vSphere support with NetApp MetroCluster](https://kb.vmware.com/s/article/2031038)
- [VMware vSphere support with NetApp SnapMirror Business Continuity](https://kb.vmware.com/s/article/83370) (now known as SnapMirror active sync)

NetApp MetroCluster can be deployed in two different configurations for use with vSphere:

- Stretch MetroCluster
- Fabric MetroCluster

Refer to [MetroCluster documentation](https://www.netapp.com/support-and-training/documentation/metrocluster/) for specific design and deployment information for MetroCluster.

SnapMirror active sync can also be deployed in two different ways:

- Asymmetric
- Symmetric Active Sync (ONTAP 9.15.1+)

Refer to [NetApp Docs — SnapMirror active sync / SMBC](https://docs.netapp.com/us-en/ontap/smbc/index.html) for specific design and deployment information for SnapMirror active sync.

(Diagrams of MetroCluster and SnapMirror active sync/ONTAP Mediator topologies are provided on the source page as images and are not reproduced here in text form.)
