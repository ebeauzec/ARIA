# Learn about NetApp Backup and Recovery
Source: https://docs.netapp.com/us-en/bluexp-backup-recovery/concept-backup-to-cloud.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-backup-recovery/concept-backup-to-cloud.html

Last updated: 06/25/2026

NetApp Backup and Recovery is a data service that provides efficient, secure, and cost-effective data protection for all your ONTAP workloads, including volumes, databases, virtual machines, and Kubernetes workloads.

A workload is a logical grouping of resources within a system that is managed as a single unit for protection, governance, detection, and recovery. In Backup and Recovery, a workload is the unit you protect. Its meaning depends on the data source: for Kubernetes a workload is an application, for VM environments it's a virtual machine, and for database environments it's a database.

Support for Backup and Recovery is already built in to all ONTAP systems, so there is no need for additional hardware or media gateways. This makes backup operations simple and cost effective. The NetApp Console simplifies the implementation of any backup strategy, including the full spectrum of 3-2-1 backup variants, without needing multiple resource managers or specialized personnel.

## What you can do with NetApp Backup and Recovery

- **ONTAP volume workloads**: Create local snapshots, replicate to secondary storage, and back up ONTAP volumes from on-premises ONTAP or Cloud Volumes ONTAP systems to object storage in your public or private cloud account. Create block-level, incremental forever backups stored on another ONTAP cluster and in object storage in the cloud. Can be used with SnapCenter.
- **Microsoft SQL Server workloads**: Back up SQL Server instances and databases from on-premises ONTAP, Cloud Volumes ONTAP, or Amazon FSx for NetApp ONTAP. Restore and clone databases. Used without SnapCenter.
- **VMware workloads**: Protect VMware VMs and datastores; back up to supported storage providers; restore data from the cloud back to on-premises vCenter, to the same or an alternate location. Used without SnapCenter Plug-in for VMware vSphere.
- **KVM workloads**: Back up/restore virtual machines, back up KVM storage pools, use protection groups to manage backup tasks.
- **Hyper-V workloads**: Back up/restore virtual machines, use protection groups.
- **Oracle Database workloads (Preview)**: Back up/restore databases and logs, protection groups, policies, 3-2-1 backup architecture, retention configuration, mount/unmount ARCHIVELOG backups.
- **Kubernetes workloads**: Manage and protect Kubernetes applications and resources; protection policies structure incremental backups; restore to same or different clusters/namespaces. Used without SnapCenter.

## Benefits

- **Efficient**: Block-level, incremental-forever replication reduces data replicated and stored, minimizing network traffic and storage costs.
- **Secure**: Encrypts data in transit and at rest; uses secure communication protocols.
- **Cost-effective**: Uses the lowest-cost storage tiers available in your cloud account.
- **Automated**: Automatically generates backups on a predefined schedule.
- **Flexible**: Restore data to the same or a different system.

## Cost

NetApp doesn't charge for the trial version, but you're responsible for cloud resource costs (storage, data transfer). There is no charge to create snapshots or replicated volumes beyond the disk space required.

**Resource charges** (paid to cloud provider):
- Object storage capacity and read/write of backup files.
- Because NetApp Backup and Recovery preserves source-volume storage efficiencies, you pay object storage costs for data *after* ONTAP efficiencies (post dedup/compression).
- Restoring via Search & Restore incurs a per-TiB cost for data scanned by search requests (not needed for Browse & Restore): AWS uses Amazon Athena/AWS Glue in a new S3 bucket; Azure uses Azure Synapse workspace and Azure Data Lake Storage; Google Cloud uses a new bucket plus BigQuery.
- Restoring from archival object storage incurs additional per-GiB retrieval fee and per-request fee.
- Scanning a backup file for ransomware during restore (if Datalock and Ransomware protection enabled) incurs extra egress costs.

**Service charges**:
- ONTAP volume workloads: charged only for volumes protected to object storage, based on logical used capacity of source volumes before efficiencies (Front-End Terabytes / FETB).
- Kubernetes workloads: charged based on combined size of all persistent volumes.
- All other workloads: charged for resources protected to at least one secondary or object storage target, based on logical size of source workload (database size for databases, VM size for VMs).

Three ways to pay: (1) subscribe from your cloud provider (pay per month), (2) purchase an annual contract, (3) purchase licenses directly from NetApp.

## Licensing

Free trial available without a license key for a limited time. A Backup license is only required for backup and restore operations involving object storage — creating snapshots/replicated volumes doesn't require a license.

- **Bring Your Own License (BYOL)**: Term-based (1, 2, or 3 years), capacity-based (1-TiB increments), purchased from NetApp; serial number activated in the NetApp Console; covers all source systems in your organization; renewal required at term/capacity limit.
- **Pay As You Go (PAYGO)**: Subscribe through cloud provider marketplace, pay per GiB of backed-up data, billed monthly, no upfront payment, 30-day free trial on first sign-up.
- **Annual Contract**: Available through AWS and Azure marketplaces for 1, 2, or 3 years. Two options: **Cloud Backup** (backs up Cloud Volumes ONTAP and on-premises ONTAP data) and **CVO Professional** (bundles Cloud Volumes ONTAP + NetApp Backup and Recovery with unlimited backups for CVO volumes — backup capacity not counted against license). CVO Professional has two charge types: resource charges (storage usage) and service charges (NetApp Backup and Recovery fees, free of charge if source volume is on a CVO Professional plan system).
- Google Cloud Platform: request a private offer from NetApp and select your plan during activation in Google Cloud Marketplace.

## Supported workloads, systems, and backup targets

**Supported workloads**: ONTAP volumes; Microsoft SQL Server instances/databases on physical disk and VMware VMDK over VMFS/NFS; VMware VMs and datastores; KVM workloads; Hyper-V workloads; Oracle Database workloads (Preview); Kubernetes workloads.

**Supported systems**: On-premises ONTAP SAN (iSCSI) and NAS (NFS/CIFS) with ONTAP 9.8+; Cloud Volumes ONTAP 9.8+ for AWS (SAN/NAS), Google Cloud (NFS/CIFS), Microsoft Azure (SAN/NAS); Amazon FSx for NetApp ONTAP (SQL Server workloads only).

**Supported backup targets**: Microsoft Azure Blob storage; AWS S3; Google Cloud Storage (ONTAP Volumes and Kubernetes workloads only); StorageGRID; ONTAP S3; S3 compatible storage (ONTAP Volumes workloads only).

## How NetApp Backup and Recovery works

When enabled, the service performs a full backup of your data; all subsequent backups are incremental, minimizing network traffic. Uses a 3-2-1 protection strategy. Note: Primary to object storage is also supported, not just secondary to object storage.

### Where backups reside in object store locations

Backup copies are stored in an object store created by the NetApp Console in your cloud account — one object store per cluster/system, named `netapp-backup-clusteruuid`. Do not delete this object store.

- AWS: the Console enables the Amazon S3 Block Public Access feature on the S3 bucket.
- Azure: the Console uses a new or existing resource group with a storage account for the Blob container and blocks public access to blob data by default.
- StorageGRID: the Console uses an existing storage account for the object store bucket.
- ONTAP S3: the Console uses an existing user account for the S3 bucket.

### Backup copies are associated with your NetApp Console organization

Backup copies are associated with the NetApp Console organization in which the Console agent resides. If you have multiple Console agents in the same organization, each displays the same list of backups.

## Terms

- **Protection**: Ensuring snapshots and immutable backups occur regularly to a different security domain using protection policies.
- **Workload**: ONTAP volumes, Microsoft SQL Server instances/databases, VMware VMs/datastores, or Kubernetes clusters/applications.
