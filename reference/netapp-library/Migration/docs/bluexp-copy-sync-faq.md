# BlueXP copy and sync technical FAQ
Source: https://docs.netapp.com/us-en/bluexp-copy-sync/faq.html
Fetched: 2026-07-07

## Getting started

**How does BlueXP copy and sync work?**
BlueXP copy and sync uses the NetApp data broker software to sync data from a source to a target (a sync relationship). A data broker group controls the sync relationships between sources and targets. After setup, BlueXP copy and sync analyzes your source system and breaks it into multiple replication streams pushed to your selected target. After the initial copy, the service syncs changed data based on your schedule.

**How does the 14-day free trial work?**
Starts when you sign up. No NetApp charges for sync relationships for 14 days, but resource charges for deployed data brokers still apply.

**How much does it cost?**
Two cost types: service charges (pay-as-you-go, hourly, based on number of sync relationships; or licenses through your NetApp rep — each license enables 20 sync relationships for 12 months; free for Cloud Volumes Service and Azure NetApp Files) and resource charges (compute/storage costs for running the data broker in the cloud).

**How is it billed?**
Subscribe via AWS/Azure marketplace (pay-as-you-go or annual) or purchase licenses directly from NetApp. Subscription is managed through your provider marketplace, not the BlueXP UI.

**Can I use it outside the cloud?**
Yes — source, target, and data broker software can all reside on-premises. The data broker group still needs an internet connection to communicate with the service. Without a direct NetApp license, an AWS or Azure account is needed for PAYGO billing.

**How do I access it?**
From the BlueXP website, Sync tab.

**What's a data broker group?**
Each data broker belongs to a group; grouping improves sync relationship performance.

## Supported sources and targets

- Supports NFS version 3+ and SMB version 1+.
- Amazon S3 target storage classes: Standard (default), Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier Deep Archive, Glacier Flexible Retrieval, Glacier Instant Retrieval.
- Azure Blob storage tiers: Hot, Cool.
- Google Cloud Storage classes: Standard, Nearline, Coldline, Archive.

## Networking

Requires a data broker group connected to source and target via the selected protocol or object storage API (S3, Azure Blob, IBM COS). Data broker group needs outbound internet over port 443.

Proxy servers (with or without basic auth) are supported for HTTP/HTTPS traffic from the data broker; non-HTTP traffic (NFS/SMB) cannot be routed through a proxy. Data-in-flight encryption for NFS/Azure NetApp Files sync is sent over HTTPS and is not routable through a proxy.

## Data synchronization

- Default schedule: daily. Can be modified (days/hours/minutes), disabled, or deleted (deleting the schedule doesn't delete data, only the sync relationship).
- Minimum sync interval: every 1 minute.
- Data broker group retries a failed file transfer 3 times before skipping (configurable).
- For directories with 600,000+ files, contact NetApp — additional data broker memory may be required.

## Security

- All service networking connectivity uses Amazon SQS.
- Communication with S3, Azure Blob, GCS, IBM COS is via HTTPS.
- Recommended on-premises connectivity: AWS Direct Connect / Azure ExpressRoute / Google Cloud Interconnect (non-internet-routed), VPN, or private endpoints (Amazon Private S3 Endpoint, Azure VNet service endpoints, Private Google Access).
- Data-in-flight encryption supported between source/target NFS servers.
- SMB 3.0/3.11 server-side encrypted data is copied as-is (BlueXP copy and sync cannot encrypt SMB data itself).
- S3 targets: choice of AWS KMS or AES-256 encryption. Google Storage targets: default Google-managed key or customer KMS key.

## Data permissions

- SMB: ACLs preserved between source SMB share and target SMB share, and from source SMB share to object storage (except ONTAP S3). ACLs from object storage to SMB are not supported.
- NFS: NFSv3 copies permissions and user/group owner; NFSv4 copies ACLs.

## Object storage metadata

Object storage metadata is preserved for specific sync relationship pairs among Amazon S3, StorageGRID, Google Cloud Storage, and IBM Cloud Object Storage (see full matrix in source). For NFS/SMB sources, user ID, modification time, access time, and GID are replicated by default; ACL replication from CIFS is opt-in.

## Performance

- Progress indicator shows data broker group network adapter throughput (refreshes every 20 seconds; sums traffic across multiple brokers if accelerated).
- Large file transfers (multi-TiB) can take a long time; limiting concurrent transfers can help — contact NetApp.
- Azure NetApp Files: use Premium or Ultra service level to avoid failures/performance issues (avoid Standard).
- Cloud Volumes Service for AWS: use Premium or Extreme service level (avoid Standard).
- New relationships start with a single data broker; add more to a group to accelerate sync if bottlenecked. Check network bandwidth, latency, topology, broker VM specs, and storage performance first.

## Deleting things

- Deleting a sync relationship stops future syncs and terminates payment; already-synced target data remains as-is.
- Deleting an item from the source: by default not deleted from target on next sync unless the "delete on target" option is enabled for that relationship.
- Deleting an item from the target: not removed from source (relationship is one-way, source to target); next sync re-copies it from source.

## Data broker architecture

- Node.js application running on a Linux host.
- Deployment: AWS CloudFormation, Azure Resource Manager, Google Cloud Deployment Manager, or manual install on your own Linux host.
- Auto-upgrades itself to the latest version.
- Uses AWS SQS as a secure communication/control/monitoring channel and persistency layer.
- Additional data brokers can be added to a group to increase transfer speed and add high availability/resiliency.
