# vSphere datastore and protocol features overview
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vsphere-datastores-top.html
Fetched: 2026-07-07

Six protocols are used to connect VMware vSphere to datastores on a system running ONTAP:

- FCP
- NVMe/FC
- NVMe/TCP
- iSCSI
- NFS v3
- NFS v4.1

FCP, NVMe/FC, NVMe/TCP, and iSCSI are block protocols that use the vSphere Virtual Machine File System (VMFS) to store VMs inside ONTAP LUNs or NVMe namespaces that are contained in an ONTAP FlexVol volume. NFS is a file protocol that places VMs into datastores (which are simply ONTAP volumes) without the need for VMFS. SMB (CIFS), iSCSI, NVMe/TCP, or NFS can also be used directly from a guest OS to ONTAP.

The following tables present vSphere-supported traditional datastore features with ONTAP. This information does not apply to vVols datastores, but it does generally apply to vSphere 6.x and later releases using supported ONTAP releases. You can also consult the [VMware Configuration Maximums tool](https://configmax.broadcom.com/guest?vmwareproduct=vSphere&release=vSphere%208.0&categories=2-0) for specific vSphere releases to confirm specific limits.

## Datastore limits by protocol

| Capability/Feature | FC | iSCSI | NVMe-oF | NFS |
| --- | --- | --- | --- | --- |
| Format | VMFS or raw device mapping (RDM) | VMFS or RDM | VMFS | n/a |
| Maximum number of datastores or LUNs | 1024 LUNs per ESXi host, up to 32 paths per LUN, up to 4096 total paths per host, up to 128 hosts per datastore | 1024 LUNs per ESXi host, up to 32 paths per LUN, up to 4096 total paths per host, up to 128 hosts per datastore | 256 Namespaces per ESXi host, up to 32 paths per namespace per host, 2048 total paths per host, up to 16 hosts per datastore | 256 NFS connections per host (impacted by nconnect and session trunking). Default NFS.MaxVolumes is 8. Use ONTAP tools for VMware vSphere to increase to 256. |
| Maximum datastore size | 64TB | 64TB | 64TB | 300TB FlexVol volume or greater with FlexGroup volume |
| Maximum datastore file size | 62TB | 62TB | 62TB | 62TB with ONTAP 9.12.1P2 and later |
| Optimal queue depth per LUN or file system | 64-256 | 64-256 | Autonegotiated | Refer to NFS.MaxQueueDepth in "Recommended ESXi host and other ONTAP settings" |

## Supported VMware storage-related functionality

| Capability/Feature | FC | iSCSI | NVMe-oF | NFS |
| --- | --- | --- | --- | --- |
| vMotion | Yes | Yes | Yes | Yes |
| Storage vMotion | Yes | Yes | Yes | Yes |
| VMware HA | Yes | Yes | Yes | Yes |
| Storage Distributed Resource Scheduler (SDRS) | Yes | Yes | Yes | Yes |
| VADP-enabled backup software | Yes | Yes | Yes | Yes |
| Microsoft Cluster Service (MSCS)/failover clustering in a VM | Yes | Yes (1) | Yes (1) | Not supported |
| Fault Tolerance | Yes | Yes | Yes | Yes |
| Live Site Recovery/Site Recovery Manager | Yes | Yes | No (2) | V3 only (2) |
| Thin-provisioned VMs (virtual disks) | Yes | Yes | Yes | Yes (default for all VMs on NFS when not using VAAI) |
| VMware native multipathing | Yes | Yes | Yes | NFS v4.1 session trunking requires ONTAP 9.14.1+ |

## Supported ONTAP storage management features

| Capability/Feature | FC | iSCSI | NVMe-oF | NFS |
| --- | --- | --- | --- | --- |
| Data deduplication | Savings in the array | Savings in the array | Savings in the array | Savings in the datastore |
| Thin provisioning | Datastore or RDM | Datastore or RDM | Datastore | Datastore |
| Resize datastore | Grow only | Grow only | Grow only | Grow, autogrow, and shrink |
| SnapCenter plug-ins (Windows/Linux, in guest) | Yes | Yes | Yes | Yes |
| Monitoring/host config via ONTAP tools for VMware vSphere | Yes | Yes | Yes | Yes |
| Provisioning via ONTAP tools for VMware vSphere | Yes | Yes | Yes | Yes |

## Supported backup features

| Capability/Feature | FC | iSCSI | NVMe-oF | NFS |
| --- | --- | --- | --- | --- |
| ONTAP snapshots | Yes | Yes | Yes | Yes |
| SRM supported by replicated backups | Yes | Yes | No (2) | V3 only (2) |
| Volume SnapMirror | Yes | Yes | Yes | Yes |
| VMDK image access | SnapCenter/VADP software | SnapCenter/VADP software | SnapCenter/VADP software | SnapCenter/VADP software, vSphere Client, datastore browser |
| VMDK file-level access | SnapCenter/VADP software, Windows only | SnapCenter/VADP software, Windows only | SnapCenter/VADP software, Windows only | SnapCenter/VADP software and 3rd-party apps |
| NDMP granularity | Datastore | Datastore | Datastore | Datastore or VM |

**Notes:**
1. NetApp recommends using in-guest iSCSI for Microsoft clusters rather than multiwriter-enabled VMDKs in a VMFS datastore. This is fully supported by Microsoft and VMware, offers flexibility with ONTAP (SnapMirror on-prem or to cloud), and can be protected with SnapCenter. vSphere 7 adds a clustered VMDK option (different from multiwriter, requires VMFS 6 with clustered VMDK support enabled). See VMware's Setup for Windows Server Failover Clustering documentation.
2. Datastores using NVMe-oF and NFS v4.1 require vSphere replication. Array-based replication for NFS v4.1 is not supported by SRM. Array-based replication with NVMe-oF is not currently supported by the ONTAP tools SRA.

## Selecting a storage protocol

ONTAP supports all major storage protocols. Historically there's little performance difference between protocols at similar line speeds, but NVMe-oF (NVMe/TCP and NVMe/FC) shows notable gains in IOPS, reduced latency, and up to 50%+ reduction in host CPU consumption. NFS offers the greatest flexibility and ease of management, especially for large VM counts. All protocols can be managed with ONTAP tools for VMware vSphere.

Factors to consider:
- **Current operating environment**: FC SAN fabric skills vs. Ethernet IP skills; ensure network isn't a general-purpose network unsuited for storage traffic.
- **Ease of setup**: Block protocols require FC fabric config (switches, cabling, zoning, HBA/firmware interoperability), plus LUN creation/mapping and guest OS discovery/formatting. NFS volumes just need mount after export — no special hardware qualification.
- **Ease of management**: SAN requires multiple steps to grow space (grow LUN, rescan, grow file system) and cannot shrink LUNs. NFS can be resized up or down, and this can be automated. SAN supports space reclamation via guest OS DEALLOCATE/TRIM/UNMAP; not possible with NFS.
- **Storage space transparency**: NFS shows thin-provisioning, dedup, and cloning savings immediately across a datastore/volume. VM density is typically greater on NFS, improving dedup savings and reducing datastore management overhead.

## Datastore layout

- NFS datastores provide high performance, ease of management, and much higher VM-to-datastore ratios than block storage (up to 10x datastore density reduction). Use at least four datastores (FlexVol volumes) per node for maximum performance from hardware resources (not required for FlexGroup volumes, which scale by design). Multiple datastores also let you set different recovery policies per datastore.
- **NetApp recommends** FlexVol volumes for most NFS datastores. FlexGroup volumes (supported since ONTAP 9.8) are recommended for certain use cases. Qtrees are not generally recommended — not supported by ONTAP tools for VMware vSphere or SnapCenter plugin for VMware vSphere.
- A good FlexVol datastore size is 4TB–8TB — balances performance, manageability, and data protection. Start small and grow as needed (max 300TB). Smaller datastores recover faster and move faster across the cluster. Consider ONTAP autosize; the ONTAP tools Datastore Provisioning Wizard uses autosize by default.
- VMFS datastores use LUNs or NVMe namespaces (storage units on ASA) accessed via FC, iSCSI, NVMe/FC, or NVMe/TCP. VMFS datastores can be up to 64TB, consisting of up to 32 x 2TB LUNs (VMFS 3) or a single 64TB LUN (VMFS 5). ONTAP max LUN size is 128TB on AFF/ASA/FAS. **Always use a single, large LUN per datastore rather than extents.**
- Older guest OSs needed storage alignment; modern OSs (Microsoft, Red Hat) no longer require it. For legacy OSs needing alignment, search NetApp KB for "VM alignment" or request TR-3747.
- Avoid defragmentation utilities in guest OS — no performance benefit, affects storage efficiency and snapshot space. Turn off search indexing in guest OS for VDI.
- AFF systems provide default inline dedup and compression across all volumes in an aggregate — no need to group similar OS/app types in one datastore for savings.
- Consider guest-owned file systems (NFS, SMB, NVMe/TCP, iSCSI) managed directly by the guest instead of a datastore — see application-specific NetApp TRs (e.g., Oracle Databases on ONTAP virtualization section).
- First Class Disks (Improved Virtual Disks) allow vCenter-managed disks independent of a VM (vSphere 6.5+) — useful with vVols, especially with OpenStack/Kubernetes tools. Supported by ONTAP and ONTAP tools for VMware vSphere.

## Datastore and VM migration

- Use Storage vMotion to migrate the bulk of VMs to ONTAP nondisruptively — ONTAP storage efficiency (dedup/compression) processes data as it migrates. Use vCenter to select multiple VMs (Ctrl+click Actions) and schedule migration.
- It's often simpler to migrate in bulk first and reorganize later, especially if different datastores are needed for different Snapshot schedules. Storage vMotion can use VAAI offloads to move VMs between datastores on the same cluster without host-based copy. Note: NFS does not offload storage vMotion of powered-on VMs; VMFS does.
- For databases/apps using attached storage, use the application's own migration tools (e.g., Oracle RMAN/ASM, SQL Server Management Studio, SnapManager for SQL Server, or SnapCenter). See "Migration of Oracle databases to ONTAP storage systems."

## ONTAP tools for VMware vSphere

The most important best practice is installing and using ONTAP tools for VMware vSphere (formerly Virtual Storage Console) — a vCenter plug-in that simplifies storage management, enhances availability, and reduces costs for SAN or NAS on ASA, AFF, FAS, or ONTAP Select. It applies best practices for datastore provisioning and optimizes ESXi multipath/HBA timeout settings. It also enables installing the NFS Plug-In for VMware VAAI (copy offload for VM cloning, thick-disk space reservation, ONTAP snapshot offload).

> **Note:** On image-based vSphere clusters, add the NFS Plug-In to your image so hosts don't go out of compliance when ONTAP tools installs it.

ONTAP tools is also the management interface for the VASA Provider for ONTAP, supporting storage policy-based management with vVols.

**NetApp recommends** using ONTAP tools for VMware vSphere within vCenter to provision both traditional and vVols datastores to ensure best practices are followed.

## General networking

- Separate storage network traffic from other networks (dedicated VLAN or separate switches). Use QoS/additional uplinks if sharing physical paths. Don't connect hosts directly to storage — use switches for redundant paths and VMware HA.
- Jumbo frames can be used (especially with iSCSI) if configured identically across all devices/VLANs in the path, including ESXi vSwitch, VMkernel port, and physical ports/interface groups on each ONTAP node.
- NetApp only recommends disabling network flow control on cluster interconnect ports within an ONTAP cluster; no other flow-control recommendation for data ports. See TR-4182 for background.
- Configure Ethernet ports as RSTP edge ports or use Cisco PortFast. Enable Spanning-Tree PortFast trunk feature where 802.1Q VLAN trunking is enabled to ESXi or ONTAP.
- Link aggregation best practices:
  - Use switches supporting multi-chassis link aggregation (e.g., Cisco vPC).
  - Disable LACP for switch ports connected to ESXi unless using dvSwitches 5.1+ with LACP configured.
  - Use LACP for ONTAP dynamic multimode interface groups with port or IP hash.
  - Use IP hash teaming policy on ESXi with static link aggregation (EtherChannel) and standard vSwitches, or LACP-based aggregation with vSphere Distributed Switches. If no link aggregation, use "Route based on the originating virtual port ID."

*Page last updated: 11/03/2025*
