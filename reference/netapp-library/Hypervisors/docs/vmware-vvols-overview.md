# VMware vSphere Virtual Volumes (vVols) overview
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vvols-overview.html
Fetched: 2026-07-07

ONTAP has been a leading storage solution for VMware vSphere environments for over two decades and continues to add innovative capabilities to simplify management while reducing costs. This document covers ONTAP capabilities for VMware vSphere Virtual Volumes (vVols), including product information, use cases, best practices, and other information to streamline deployment and reduce errors.

> **Note:** This documentation replaces previously published technical report *TR-4400: VMware vSphere Virtual Volumes (vVols) with ONTAP*. It has been updated to include new vVols features from vSphere 8.0 update 1, supported with ONTAP tools 9.12.

## Virtual Volumes (vVols) overview

NetApp began working with VMware to support vSphere APIs for Storage Awareness (VASA) for vSphere 5 in 2012 — an early VASA Provider defined storage capabilities in a profile used to filter datastores during provisioning and check compliance afterward. This evolved to add more provisioning automation and Virtual Volumes (vVols), where individual storage objects (LUNs, files, and now — with vSphere 8 — NVMe namespaces) are used for VM files and disks. NetApp was a VMware reference partner for vVols at release with vSphere 6 (2015), and a design partner for vVols using NVMe over Fabrics in vSphere 8.

**Key components:**

- **VASA Provider**: The software component handling communication between vSphere and the storage system. For ONTAP, it runs in the ONTAP tools for VMware vSphere appliance, which also includes a vCenter plugin, an SRA for VMware Site Recovery Manager, and a REST API server for custom automation. Once configured/registered with vCenter, nearly all storage needs can be managed from the vCenter UI or REST API.
- **Protocol Endpoint (PE)**: A proxy for I/O between ESXi hosts and the vVols datastore. The ONTAP VASA Provider creates these automatically — one PE LUN (4MB) per FlexVol volume in the datastore, or one NFS mount point per NFS LIF on the node hosting a FlexVol volume in the datastore. ESXi mounts PEs directly rather than individual vVol LUNs/files; PEs are created/mounted/unmounted/deleted automatically.
- **Virtual Protocol Endpoint (vPE)**: New in vSphere 8 for NVMe-oF vVols — the ESXi host instantiates a vPE automatically for each ANA group when the first VM powers on. ONTAP auto-creates ANA groups per FlexVol volume. No VASA Provider bind requests are needed (the ESXi host handles vVol binding internally via the vPE), reducing the risk of a "vVol bind storm" impacting service.
- **Virtual Volume datastore**: A logical datastore representation of a vVols container created/maintained by a VASA Provider, representing a pool of capacity from managed storage systems. ONTAP tools supports allocating multiple FlexVol volumes (backing volumes) to a single vVols datastore, spanning multiple cluster nodes and combining flash/hybrid systems with different capabilities.
- **Virtual Volumes (vVols)**: The actual VM files/disks stored in the vVols datastore. ONTAP creates NVMe namespaces, LUNs, or files depending on the datastore's protocol. Common types: Config (metadata files), Data (virtual disk/VMDK), Swap (created at VM power-on). VMware VM-encrypted vVols are type "Other" (not to be confused with ONTAP volume/aggregate encryption).

## Policy based management

VASA lets a VM admin use required storage capabilities without interacting with the storage team. vCenter admins define storage capabilities that vCenter users consume to provision VMs; the mapping between VM storage policy and datastore storage capability profile lets vCenter show compatible datastores, and also enables automation via Aria Automation (formerly vRealize) or Tanzu Kubernetes Grid.

**Two elements:**
- **Storage Capability Profile (SCP)**: A storage template defining required features (performance, protocol, storage efficiency, etc.) without needing to know ONTAP management details. Created via the ONTAP tools for VMware vSphere menu in vCenter, or via REST API — manually (selecting capabilities) or auto-generated from existing traditional datastores.
- **VM Storage Policy**: Created in vCenter under Policies and Profiles. For vVols, build a ruleset using rules from the NetApp vVols storage type provider; ONTAP tools simplifies this by letting you select an SCP directly instead of specifying individual rules.

Once a VM is provisioned, the VASA Provider continuously checks compliance and alerts the VM admin (vCenter alarm) if the backing volume becomes non-compliant.

## NetApp vVols support

ONTAP has supported the VASA specification since its 2012 initial release. Beyond ONTAP 9 on AFF/ASA/FAS, NetApp supports VMware workloads on ONTAP Select, Amazon FSx for NetApp with VMware Cloud on AWS, Azure NetApp Files with Azure VMware Solution, Cloud Volumes Service with Google Cloud VMware Engine, and NetApp Private Storage in Equinix (functionality varies by provider/connectivity). Access from vSphere guests to Cloud Volumes ONTAP is also available.

At publication time, hyperscaler environments are limited to traditional NFS v3 datastores only — vVols are available only with on-premises ONTAP systems, or cloud-connected systems offering full on-premises functionality (e.g., NetApp partner/service-provider hosted systems).

## Benefits of using vVols with ONTAP

VMware introduced vVols with VASA 2.0 in 2015 as "an integration and management framework delivering a new operational model for external storage (SAN/NAS)."

**Policy based management benefits:**
- **Increase velocity**: ONTAP tools removes the need for the vCenter admin to open tickets with the storage team for provisioning, while RBAC roles in vCenter and ONTAP still allow independent team/activity restrictions if desired.
- **Smarter provisioning**: Storage capabilities exposed via VASA APIs let provisioning workflows use advanced capabilities without the VM admin needing to manage the storage system directly.
- **Faster provisioning**: Different storage capabilities can coexist in a single datastore and be auto-selected per VM policy.
- **Avoid mistakes**: Storage/VM policies are predefined and applied consistently; compliance alarms flag drift from defined policies.
- **Better capacity management**: VASA and ONTAP tools expose capacity down to the individual aggregate level with multiple alerting layers for low capacity.

**VM granular management on the modern SAN:** Traditional FC/iSCSI SAN lacked per-VM/file management (LUNs provisioned, VMFS manages individual files) — vVols bring NFS-like storage granularity to SAN. With vSphere 8 and ONTAP tools 9.12+, these same granular controls now extend to NVMe over Fabrics for greater performance at scale; vSphere 8.0 update 1 enables a complete end-to-end NVMe solution using vVols with no I/O translation in the hypervisor storage stack.

**Greater storage offload capabilities:** VAAI can't offload VMware-managed snapshots to storage for SAN, and NFS VAAI has limitations on VM native snapshots and can't offload clone operations for hot (powered-on) Storage vMotion migrations (VM must be powered off for VAAI-offloaded migration on traditional NFS datastores). Because vVols use individual LUNs/namespaces/files per VM disk, ONTAP can clone them quickly and efficiently for VM-granular snapshots without delta files. The VASA Provider in ONTAP tools enables near-instant, storage-efficient clones for both hot and cold migrations, and near-instant cross-volume vVol copies.

## Common use cases for vVols

- **On-demand VM provisioning**: private cloud/service-provider IaaS; automation/orchestration via Aria (vRealize) suite, OpenStack, etc.
- **First Class Disks (FCDs)**: VMware Tanzu Kubernetes Grid (TKG) persistent volumes; Amazon EBS-like services via independent VMDK lifecycle management.
- **On-demand provisioning of temporary VMs**: test/dev labs, training environments.

## Common benefits with vVols

- Clones are created quickly within a single volume or across multiple volumes in an ONTAP cluster — an advantage over traditional VAAI clones — and are storage efficient. In-volume clones use ONTAP file clone (like FlexClone volumes), storing only changes from the source vVol file/LUN/namespace. Production VMs can be created quickly with minimal space and benefit from VM-level protection (NetApp SnapCenter plugin for VMware vSphere, VMware-managed snapshots, or VADP backup) and performance management (ONTAP QoS).
- vVols are ideal for TKG with vSphere CSI, providing discrete storage classes/capacities managed by the vCenter admin.
- Amazon EBS-like services are delivered through FCDs — an FCD VMDK is a first-class vSphere citizen with an independently manageable lifecycle, separate from any VM it's attached to.
