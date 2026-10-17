# SAN (FC, FCoE, NVMe/FC, iSCSI), RDM
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vsphere-datastores-san.html
Fetched: 2026-07-07

In vSphere, there are four ways to use block storage devices:

- With VMFS datastores
- With raw device mapping (RDM)
- As an iSCSI-connected LUN or NVMe/TCP-connected namespace accessed and controlled by a software initiator from a VM guest OS
- As a vVols datastore

VMFS is a high-performance clustered file system that provides datastores that are shared storage pools. VMFS datastores can be configured with LUNs accessed using FC, iSCSI, FCoE, or with NVMe namespaces accessed using the NVMe/FC or NVMe/TCP protocols. VMFS allows storage to be accessed simultaneously by every ESX server in a cluster. The maximum LUN size is generally 128TB beginning with ONTAP 9.12.1P2 (and earlier with ASA systems); therefore, a maximum-size VMFS 5 or 6 datastore of 64TB can be created using a single LUN.

> **Tip:** Extents let you "stitch" multiple LUNs together into a single larger datastore. Never use extents to reach a desired datastore size — a single LUN is the best practice for a VMFS datastore.

vSphere includes built-in multipath support. It detects the storage device type for supported storage systems and automatically configures the multipathing stack to match the storage system's capabilities, regardless of protocol or whether using ASA, AFF, FAS, or software-defined ONTAP.

Both vSphere and ONTAP support Asymmetric Logical Unit Access (ALUA) for FC/iSCSI active/optimized vs. active/non-optimized paths, and Asymmetric Namespace Access (ANA) for NVMe namespaces (NVMe/FC, NVMe/TCP). An ALUA/ANA-optimized path uses a direct data path via a target port on the node hosting the LUN/namespace. ALUA/ANA is on by default in both vSphere and ONTAP; vSphere's multipathing software recognizes an ONTAP cluster as ALUA/ANA and uses the native plug-in with round-robin load balancing.

With NetApp ASA systems, LUNs/namespaces are presented with symmetric pathing (all paths active/optimized); vSphere recognizes ASA as symmetric and uses the native plug-in with round-robin load balancing.

> **Tip:** See "Recommended ESXi host and other ONTAP settings" for optimized multipathing settings.

ESXi does not see LUNs, namespaces, or paths beyond its configured limits. In a larger ONTAP cluster it's possible to reach the path limit before the LUN limit — ONTAP addresses this with Selective LUN Map (SLM), available since 8.3.

> **Note:** See the VMware Configuration Maximums tool for up-to-date supported ESXi limits.

SLM limits which nodes advertise paths to a given LUN. Best practice: at least two LIFs per node per SVM, and use SLM to limit advertised paths to the LUN-hosting node and its HA partner. Other paths exist but aren't advertised by default; modify with `add`/`remove` reporting-node arguments. LUNs created before 8.3 advertise all paths and must be modified to restrict to the hosting HA pair. See TR-4080 section 5.9 for more on SLM. Portsets can further reduce visible paths for initiators in an igroup.

- SLM is enabled by default — no additional config needed unless using portsets.
- For LUNs created before Data ONTAP 8.3, run `lun mapping remove-reporting-nodes` to restrict LUN access to the owning node and its HA partner.

SCSI-based block protocols (iSCSI, FC, FCoE) access LUNs via LUN IDs/serial numbers and unique names — FC/FCoE use WWNNs/WWPNs, iSCSI uses IQNs — to establish paths via LUN-to-igroup mappings filtered by portsets and SLM. NVMe-based protocols assign the namespace an auto-generated namespace ID to an NVMe subsystem, mapped to the host's NVMe Qualified Name (NQN) — regardless of FC or TCP, mapping uses NQN not WWPN/WWNN. The host creates a software-defined controller for the mapped subsystem. The internal ONTAP path to LUNs/namespaces is meaningless to block protocols — a volume containing only LUNs doesn't need to be mounted, and no junction path is needed for LUN-only volumes.

## Other best practices

- Check "Recommended ESXi host and other ONTAP settings" for NetApp/VMware-recommended settings.
- Ensure a LIF exists for each SVM on each ONTAP cluster node for availability/mobility. Best practice: two physical ports and LIFs per node, one per fabric. ALUA identifies active-optimized (direct) vs. active-nonoptimized paths for FC, FCoE, and iSCSI.
- For iSCSI/NVMe-TCP, use multiple VMkernel network interfaces on different unrouted subnets with NIC teaming when multiple vSwitches are present, or multiple physical NICs/switches for HA and throughput. On ONTAP, use a single-mode interface group for failover (2+ links to 2+ switches), or LACP/multimode interface groups for HA plus link aggregation benefits. NVMe/TCP must be enabled per-VMkernel-port and per-physical-interface, and these must align.
- If CHAP is used in ESXi for target auth, also configure it in ONTAP via CLI (`vserver iscsi security create`) or System Manager (Storage > SVMs > SVM Settings > Protocols > iSCSI > Initiator Security).
- Use ONTAP tools for VMware vSphere to create/manage LUNs and igroups — it auto-determines server WWPNs, creates igroups, configures LUNs per best practices, and maps to correct igroups.
- Use RDMs with care — harder to manage and consume limited paths. ONTAP LUNs support both physical and virtual compatibility mode RDMs.
- For NVMe/FC with vSphere 7.0, see the ONTAP NVMe/FC Host Configuration guide and TR-4684.

*Page last updated: 03/18/2026*
