# NetApp Cloud Tiering technical FAQ
Source: https://docs.netapp.com/us-en/bluexp-tiering/faq-cloud-tiering.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-cloud-tiering/faq-cloud-tiering.html

Last updated: 11/10/2025

## Cloud Tiering service

**What are the benefits of using the Cloud Tiering service?**
Effortless data center extension to the cloud (up to 50x more space); average storage savings of 70%; average 30% reduction in TCO; no need to refactor applications.

**What kind of data is useful to tier to the cloud?**
Any data considered inactive on primary or secondary storage — snapshots, historical records, finished projects on primary; all DR/backup copy volumes on secondary.

**Can I tier data from both NAS volumes and SAN volumes?**
Yes. NAS data can go to public or private clouds (e.g., StorageGRID). SAN-protocol data should use private clouds because SAN is more sensitive to connectivity issues than NAS.

**What is the definition of inactive/infrequently used data?**
Volume blocks (metadata excluded) not accessed for an amount of time, controlled by the tiering policy's cooling-days attribute.

**Will Cloud Tiering retain my storage efficiency savings in the cloud tier?**
Yes — compression, deduplication, and compaction are preserved.

**What is the difference between FabricPool and Cloud Tiering?**
FabricPool is the underlying ONTAP tiering technology (self-managed via CLI/System Manager, or managed as-a-service via Cloud Tiering). Cloud Tiering turns FabricPool into a managed service with advanced automation and visibility across hybrid/multi-cloud deployments.

**Can tiered data be used for disaster recovery or backup/archive?**
No — volume metadata is never tiered, so tiered data cannot be accessed directly. However, Cloud Tiering can achieve cost-effective backup/DR by tiering data on secondary systems and SnapMirror destination (DP) volumes.

**Is Cloud Tiering applied at the volume or aggregate level?**
Enabled at the volume level (tiering policy per volume); cold-data identification happens at the block level.

**How does Cloud Tiering determine which blocks to tier?**
The volume's tiering policy defines the type of blocks (snapshots, user data, or both) and the cooling period.

**How does Cloud Tiering affect volume capacity?**
No effect on volume capacity — affects the aggregate's performance-tier usage.

**Does Cloud Tiering enable Inactive Data Reporting (IDR)?**
Yes, on each aggregate, to identify the amount of inactive data eligible for tiering.

**How long until IDR shows information?**
After the configured cooling period passes. ONTAP 9.7 and earlier: fixed 31-day cooling period. ONTAP 9.8+: configurable up to 183 days.

## Licenses and costs

**How much does Cloud Tiering cost?**
PAYGO: $0.05/GB/month. Annual (BYOL): starting from $0.033/GB/month. No cost when tiering to StorageGRID.

**Can I have both BYOL and PAYGO for the same cluster?**
Yes, or a combination.

**What happens if BYOL capacity limit is reached or license expires?**
Tiering of new cold data stops (previously tiered data remains accessible/retrievable, moved back to performance tier on retrieval) — unless you have a PAYGO marketplace subscription, in which case new cold data continues to tier and you're billed per-use.

**Does the license include cloud egress charges?**
No.

**Is rehydration subject to cloud provider egress cost?**
Yes — all reads from the public cloud incur egress fees.

**How can I estimate cloud charges?**
Use the cloud provider's calculator (AWS, Azure, Google Cloud) or the Cloud Tiering TCO calculator (via "Calculate potential tiering savings" on the Clusters page).

**Extra charges for reading/retrieving tiered data?**
Yes — see the cloud provider's S3/Blob/Cloud Storage pricing pages.

**MetroCluster billing?**
Total tiering license applies to combined usage of both clusters (e.g., a 100 TiB license is shared across both clusters' used capacity).

## ONTAP

- Supports ONTAP 9.2 and higher.
- Supported on single-node and HA AFF, FAS, and ONTAP Select clusters; also FabricPool Mirror and MetroCluster configurations.
- HDD-only FAS aggregates supported starting ONTAP 9.8.
- AFF joined to a cluster with FAS/HDD nodes: supported regardless of controller type or cluster heterogeneity.
- Cloud Volumes ONTAP: visible on the Clusters page for a full view, but read-only from Cloud Tiering — set up tiering for CVO from the ONTAP system in the NetApp Console instead.

## Object storage

**Supported providers**: Amazon S3, Microsoft Azure Blob, Google Cloud Storage, NetApp StorageGRID, S3-compatible storage (e.g., MinIO), IBM Cloud Object Storage (FabricPool config done via System Manager/CLI).

**Can I use my own bucket/container?** Yes — new or existing.

**Supported S3 storage classes**: Standard, Standard-Infrequent Access, One Zone-Infrequent Access, Intelligent Tiering, Glacier Instant Retrieval. (S3 Glacier Flexible and Deep Archive are NOT supported — Cloud Tiering needs quickly accessible data; those classes have retrieval times of minutes to 48 hours.)

**Azure Blob access tiers supported**: Hot, Cool.

**Google Cloud Storage classes supported**: Standard, Nearline, Coldline, Archive.

**Lifecycle management**: Supported — transitions data to a more cost-effective tier after a set number of days; applies to all objects in the selected bucket (S3/GCS) or all containers in the selected storage account (Azure Blob).

**One object store per cluster or per aggregate?** Typically one per cluster; since August 2022, Advanced Setup lets you add additional object stores and attach different stores to different aggregates, or two stores to one aggregate for mirroring (max two buckets per aggregate, can be different providers/locations).

**Different buckets to different aggregates in the same cluster?** Yes, though a single bucket to multiple aggregates is generally best practice; public cloud object storage has IOPS limits that may necessitate multiple buckets.

**Volume migration between clusters**: All cold data is read from the cloud tier; the destination write location depends on tiering enablement/policy on source and destination.

**Volume move between nodes in the same cluster**: If destination aggregate has no attached cloud tier, data is read from source cloud tier and written entirely to destination local tier. If destination has an attached cloud tier, data is written first to local tier (for fast cutover), then later to cloud tier per policy. Starting ONTAP 9.6, if destination uses the same cloud tier as source, cold data doesn't move back to local tier.

**Bringing tiered data back on-premises**: Prior to ONTAP 9.8, use a volume move for full write-back. From ONTAP 9.8, the Tiering UI offers "Bring back all data" or "Bring back active file system".

**Controller head-swap**: Only aggregate ownership changes to the new controller — no data movement.

**Can I browse tiered objects directly via cloud console/explorers?**
No — tiered objects contain up to 1,024 4KB blocks from multiple files (not single files); volume metadata always stays on the local tier.

## Console agents

- The Console agent is software running on a compute instance (cloud or on-premises) enabling the NetApp Console to securely manage cloud resources; required for Cloud Tiering.
- Agent location: S3 — AWS VPC or on-premises; Blob — Azure VNet or on-premises; Google Cloud Storage — must reside in a GCP VPC; StorageGRID/other S3-compatible — must reside on-premises.
- Agent can be deployed on-premises (downloaded and manually installed on a Linux host).
- A cloud provider account is required before defining object storage and for agent setup in a VPC/VNet.
- If the Console agent fails, only visibility into tiered environments is impacted — data remains accessible and new cold data continues to be tiered automatically.

## Tiering policies

**Four policies**: None (always hot); Cold Snapshots (Snapshot-only, cold snapshot blocks only); Cold User Data and Snapshots (Auto, both types); All User Data (All, entire volume immediately).

**When is data "cold"?** After not being accessed for the minimum-cooling-days period: 2–63 days (ONTAP 9.7 and earlier) or 2–183 days (ONTAP 9.8+).

**Default cooling period**: Cold Snapshot policy — 2 days; Cold User Data and Snapshots — 31 days. Not applicable to the All policy.

**Full backup and tiered data**: All cold data is read during full backup. With All / Cold User Data and Snapshots policies, cold data isn't written back to performance tier. With Cold Snapshots, only an old snapshot used for backup has its cold blocks retrieved.

**Can I set a tiering size per volume?** No — you choose eligible volumes, data type, and cooling period via the policy.

**Is All User Data the only option for DP volumes?** No — any of the three policies can apply; source/destination policy combination determines write location.

**Does resetting a volume's policy to None rehydrate cold data?** No — it only prevents new cold blocks from moving to the cloud.

**Can I change the tiering policy after data is already tiered?** Yes — behavior after the change depends on the new policy.

**How do I ensure certain data never moves to the cloud?** Don't associate a tiering policy with the volume containing that data.

**Where is file metadata stored?** Always locally on the performance tier — never tiered.

## Networking and security

- ONTAP cluster initiates an HTTPS connection over port 443 to the object storage provider (object storage never initiates). For StorageGRID, ONTAP initiates over a user-specified port (configurable during setup).
- The Console agent needs outbound HTTPS (port 443) to ONTAP clusters, the object store, and the Cloud Tiering service.
- Monitoring/reporting tools: Active IQ Unified Manager, digital advisor (Active IQ), in addition to Cloud Tiering itself.
- If the network link to the cloud provider fails: local performance tier stays online (hot data accessible); already-tiered blocks become inaccessible until connectivity is restored.
- Bandwidth: no strict requirement, but 10 Gbps intercluster LIF ports recommended for adequate performance. You can throttle transfer bandwidth via the "Maximum transfer rate" setting (during setup or later from the Clusters page). No bandwidth recommendation/limitation for the agent itself.
- Latency: cloud tiers cannot match local-tier latency. Use the Cloud Performance Test (based on the ONTAP object store profiler) to estimate latency/throughput before enabling tiering.
- Security: AES-256-GCM encryption maintained on both performance and cloud tiers; TLS 1.2 encrypts data in transit between tiers and between agent/ONTAP/object store.
- An intercluster LIF must be configured on an Ethernet port on each HA-pair node hosting volumes with data to be tiered.
- Permissions: AWS — S3 bucket management permissions; Azure — no extra permissions beyond what's needed for the NetApp Console; Google Cloud — Storage Admin permissions for a service account with storage access keys; StorageGRID — S3 permissions; S3-compatible — S3 permissions.
