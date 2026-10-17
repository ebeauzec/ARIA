# Learn about NetApp Disaster Recovery
Source: https://docs.netapp.com/us-en/bluexp-disaster-recovery/get-started/dr-intro.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-disaster-recovery/get-started/dr-intro.html

Last updated: 05/12/2026

Disaster recovery to the cloud is a resilient and cost-effective way of protecting workloads against site outages and data corruption events. NetApp Disaster Recovery is a cloud-based disaster recovery service that automates disaster recovery workflows. With NetApp Disaster Recovery, you can protect your on-premises Kubernetes clusters, NFS-based workloads, and VMware vSphere virtual machine file system (VMFS) datastores for iSCSI and FC running NetApp storage to one of the following:

- Amazon Elastic VMware Service (EVS) with Amazon FSx for NetApp ONTAP
- VMware Cloud (VMC) on AWS with Amazon FSx for NetApp ONTAP
- Azure VMware Solution (AVS) with NetApp Cloud Volumes ONTAP (iSCSI) (Private preview)
- Google Cloud VMware Engine (GCVE) with Google Cloud NetApp Volumes
- Another on-premises NFS and/or VMFS-based (iSCSI/FC) VMware environment with ONTAP storage

NetApp Disaster Recovery uses ONTAP SnapMirror technology with integrated native VMware orchestration to protect VMware VMs and their associated on-disk OS images, while retaining all storage efficiency benefits of ONTAP. This enables industry-best storage efficiency (compression and deduplication) on primary and secondary sites.

## NetApp Console

NetApp Disaster Recovery is accessible through the NetApp Console, which provides centralized management of NetApp storage and data services across on-premises and cloud environments. The Console is required to access and use NetApp data services. You don't need a license or subscription to start using NetApp Console — you only incur charges when you need to deploy Console agents in your cloud, or for licensed/subscription-based data services.

## Benefits

- Simplified user experience for vCenter discovery and recovery of applications with multiple point-in-time recovery operations.
- Lower total cost of ownership with reduced cost of operations and ability to create and adjust disaster recovery plans with minimal resources.
- Continuous disaster recovery readiness with virtual failover testing that does not disrupt operations.
- Faster time to value with dynamic changes in your IT environment.
- Manage both storage and virtual layers through backend orchestration of ONTAP and VMware together, without virtual server appliances (VSAs).
- Because Disaster Recovery uses ONTAP SnapMirror technology (vs. VSA-based VM-layer replication used by many DR solutions), it retains ONTAP's native data compression and deduplication efficiencies with an incremental-forever replication model.

## Capabilities

- Replicate VMware apps on your on-premises production site to a disaster recovery remote site in the cloud or on-premises using SnapMirror replication.
- Migrate VMware workloads from your original site to another site.
- Conduct a failover test: the service creates temporary VMs by making a new FlexClone volume from the selected snapshot; a temporary datastore backed by the FlexClone volume is mapped to the ESXi hosts. This doesn't consume additional physical capacity, doesn't modify the original source volume, and replica jobs can continue during the test.
- In case of disaster, fail over your primary site on demand to the DR site (VMware Cloud on AWS with FSx for NetApp ONTAP or an on-premises VMware environment with ONTAP).
- After the disaster is resolved, fail back on demand from the DR site to the primary site.
- Group VMs or datastores into logical resource groups for efficient management.

> Note: You must configure the vSphere server outside of NetApp Disaster Recovery in vSphere Server.

## Cost

NetApp doesn't charge for the trial version. NetApp Disaster Recovery can be used with a NetApp license or an annual subscription-based plan through AWS.

> Important: Some releases include a technology preview; NetApp doesn't charge for previewed workload capacity.

## Licensing

- 30-day free trial.
- Pay-as-you-go (PAYGO) subscription via AWS Marketplace or Microsoft Azure Marketplace — fixed protected capacity license without long-term commitment.
- Bring Your Own License (BYOL) — a NetApp License File (NLF) obtained from your NetApp Sales Rep; activate via serial number in the NetApp Console.

Disaster Recovery is licensed based on the amount of data hosted on protected ONTAP volumes. The service maps protected VMs to their vCenter datastores; each datastore is hosted on an ONTAP volume or LUN, and the used capacity reported by ONTAP for that volume/LUN is used for licensing.

> Note: Charges are based on used capacity of datastores on the source site when at least one VM has a replication plan. Capacity for a failed-over datastore is not included in the capacity allowance. For BYOL, if data exceeds allowed capacity, service operations are limited until you obtain additional capacity or upgrade the license.

## 30-day free trial

After the trial, obtain a PAYGO subscription from your cloud provider or purchase a BYOL license from NetApp. You can purchase a license at any time and won't be charged until the trial ends.

## How NetApp Disaster Recovery works

NetApp Disaster Recovery is hosted within the NetApp Console SaaS environment. It automates recovery from the SnapMirror level, through VM registration to VMware Cloud on AWS, to network mappings directly on VMware NSX-T (included with all VMC environments).

It uses ONTAP SnapMirror technology for highly efficient, application-consistent replication so data is usable immediately after failover.

When a disaster occurs, the service recovers VMs in the other on-premises VMware environment or VMC by breaking the SnapMirror relationships and making the destination site active. It also supports failback to the original source location, and non-disruptive test failovers (recovering VMs to an isolated network via a FlexClone of the volume). For failover/test failover you can choose the latest (default) or a selected snapshot.

**Components of Disaster Recovery**

- **NetApp Console**: UI for managing disaster recovery plans, replication plans, resource groups, and failover operations.
- **Console agent**: Lightweight software running in your cloud-hosted network or on-premises VMware environment; communicates with the NetApp Console and manages data replication. Installed on a VM in your VMware environment.
- **ONTAP storage clusters**: Primary storage systems hosting your VMware workloads (on-premises arrays or cloud-based solutions like Amazon FSx for NetApp ONTAP), managed via ONTAP storage APIs.
- **vCenter servers**: VMware management server for ESXi hosts and datastores; the Console agent communicates with vCenter to register ONTAP LUNs/volumes as datastores, reconfigure VMs, and start/stop VMs.

**Protection workflow**

When a replication plan is assigned to a resource group, Disaster Recovery performs a discovery check, then:

1. For each VM in the target resource group, identify the hosting VMware datastore.
2. For each datastore, identify the hosting ONTAP FlexVol volume or LUN.
3. For each ONTAP volume/LUN, determine if a SnapMirror relationship already exists between source and destination; if not, create new destination volumes and a new SnapMirror relationship (if one exists, use it).

At each scheduled backup:

1. For VMs flagged "application consistent," use VMtools to place the supported application into a backup state.
2. Create a new snapshot of all ONTAP volumes hosting protected VMware datastores.
3. Perform a SnapMirror update to replicate snapshots to the destination ONTAP cluster.
4. Delete extraneous snapshots from source and destination once retention count is exceeded.

## Supported protection targets and datastore types

**Datastore types**: NFS datastores hosted on ONTAP FlexVol volumes; VMware VMFS datastores using iSCSI or FC protocol.

**Protection targets**: VMware Cloud (VMC) on AWS with Amazon FSx for NetApp ONTAP; another on-premises NFS-based VMware environment with ONTAP storage or an on-premises FC/iSCSI VMFS; Amazon Elastic VMware Service; Azure VMware Solution (AVS) with NetApp Cloud Volumes ONTAP (iSCSI, Private preview); Google Cloud VMware Engine (GCVE) with Google Cloud NetApp Volumes.

## Terminology

- **Datastore**: A VMware vCenter data container using a file system to hold VMDK files (NFS, VMFS, vSAN, vVol). Disaster Recovery supports NFS and VMFS, each hosted on a single ONTAP volume or LUN.
- **Replication plan**: Rules governing backup frequency and failover handling; assigned to one or more resource groups.
- **Recovery point objective (RPO)**: Maximum acceptable data loss in a disaster, defined by the replication schedule.
- **Recovery time objective (RTO)**: Maximum acceptable time to recover from a disaster (time to fail over and restart all VMs).
- **Resource group**: Logical container for managing multiple VMs as a single unit (a VM belongs to only one resource group at a time).
- **Site**: Logical container typically tied to a physical datacenter or cloud location hosting one or more vCenter clusters and ONTAP storage.
