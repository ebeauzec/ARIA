# Learn about NetApp Cloud Tiering
Source: https://docs.netapp.com/us-en/bluexp-tiering/concept-cloud-tiering.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-cloud-tiering/concept-cloud-tiering.html

Last updated: 04/13/2026

> IMPORTANT (End of Availability): NetApp Cloud Tiering is no longer available for purchase or license renewal as of April 26, 2026. Existing customers can continue to use and receive support until their subscription/license contract expires; after expiration, access to Cloud Tiering features/support ends. NetApp recommends transitioning existing tiering licenses to ONTAP FabricPool licenses (which provides the underlying data tiering functionality in ONTAP). See [Install a FabricPool license on an ONTAP cluster](https://docs.netapp.com/us-en/ontap/fabricpool/install-license-aws-azure-ibm-task.html). See also the NetApp Cloud Tiering End of Availability Notice and FAQ (linked from the source page).

NetApp Cloud Tiering extends your data center to the cloud by automatically tiering inactive data from on-premises ONTAP clusters to object storage. This frees valuable space on the cluster for more workloads, without changes to the application layer, reduces data center costs, and enables a shift from CAPEX to OPEX.

Cloud Tiering leverages *FabricPool*, a NetApp Data Fabric technology that enables automated tiering of data to low-cost object storage. Active (hot) data remains on the local tier (on-premises ONTAP aggregates), while inactive (cold) data moves to the cloud tier, preserving ONTAP data efficiencies.

Originally supported on AFF, FAS, and ONTAP Select systems with all-SSD aggregates; starting with ONTAP 9.8 you can tier data from aggregates consisting of HDDs in addition to SSDs. Tiering can be configured for single-node clusters, HA-configured clusters, Tiering Mirror configurations, and MetroCluster configurations (via FabricPool Mirror). Cloud Tiering licenses are shared among all clusters.

## NetApp Console

NetApp Cloud Tiering is accessible through the NetApp Console, which provides centralized management of NetApp storage and data services across on-premises and cloud environments. No license/subscription is required to start using the Console — charges apply only when deploying Console agents or using licensed/subscription-based data services.

## Features

- Automation for setting up and managing data tiering from on-premises ONTAP clusters to the cloud.
- Choose the default cloud provider storage class/access tier, or use lifecycle management to assign a more cost-effective tier to older tiered data.
- Create connections to additional object stores for other aggregates in your cluster.
- Drag object stores to an aggregate for tiering and FabricPool mirroring via the UI.
- Single pane of glass — removes the need to independently manage FabricPool across multiple clusters.
- Reports show active/inactive data on each cluster; a tiering health status helps identify and correct issues.
- Cloud Volumes ONTAP systems appear on the Clusters page for a full hybrid-cloud tiering view (read-only from Cloud Tiering — set up tiering for CVO from the NetApp Console instead).

## Supported object storage providers

- Amazon S3
- Microsoft Azure Blob
- Google Cloud Storage
- NetApp StorageGRID
- S3-compatible object storage (e.g., MinIO)
- IBM Cloud Object Storage (FabricPool config must be set up via System Manager/ONTAP CLI; licensing completed via Cloud Tiering)

> Note: You can tier data from NAS volumes to public or private clouds (like StorageGRID). For SAN-protocol data, NetApp recommends private clouds due to connectivity considerations.

### Object storage tiers

ONTAP clusters can tier to a single object store or multiple object stores, adding a new or existing bucket/container plus a storage class/access tier. Cloud Tiering uses the cloud provider's default storage class/access tier, but you can apply a lifecycle rule to auto-transition data to a cheaper storage class after a set number of days (not available for StorageGRID or S3-compatible storage).

## Pricing and licenses

Pay via pay-as-you-go subscription, annual subscription, BYOL NetApp tiering license, or a combination. 30-day free trial for your first cluster. No charges for tiering to StorageGRID (no BYOL or PAYGO required). Because Cloud Tiering preserves source-volume storage efficiencies, you pay cloud object storage costs for tiered data after ONTAP efficiencies (post dedup/compression).

**30-day free trial**: Starts when you set up tiering to your first cluster (if no license). After it ends, pay via PAYGO, annual subscription, or BYOL. If you don't subscribe/license, ONTAP stops tiering new cold data (previously tiered data stays accessible; retrieved data moves back to performance tier).

**Pay-as-you-go subscription**: Consumption-based, subscribe via cloud provider marketplace, pay per GB tiered with no up-front payment, billed monthly by the cloud provider. Recommended even with a free trial or BYOL — ensures no disruption after trial ends, and covers tiering beyond BYOL capacity limits.

**Annual contract**: Available for tiering to Amazon S3 or Azure, in 1-, 2-, or 3-year terms. Not currently supported for Google Cloud.

**Bring your own license (BYOL)**: Purchase a Cloud Tiering license from NetApp (1-, 2-, or 3-year term, any tiering capacity starting at a 10 TiB minimum). Floating license usable across multiple on-premises ONTAP clusters — total capacity shared across all clusters. Add the license to the NetApp Console after purchase. Recommend also setting up PAYGO even with BYOL. Note: starting August 2021 the old FabricPool license was replaced by the Cloud Tiering license.

## How Cloud Tiering works

A NetApp-managed service using FabricPool technology to automatically tier inactive (cold) data from on-premises ONTAP clusters to public or private cloud object storage. Connections to ONTAP take place from a Console agent.

1. Discover your on-premises cluster from the NetApp Console.
2. Set up tiering: provide object storage details (bucket/container, storage class/access tier, lifecycle rules).
3. The Console configures ONTAP to use the object storage provider and discovers active/inactive data on the cluster.
4. Choose volumes to tier and the tiering policy to apply.
5. ONTAP starts tiering inactive data once it reaches the thresholds to be considered inactive.
6. If a lifecycle rule is applied (some providers only), older tiered data moves to a more cost-effective tier after a set number of days.

### Volume tiering policies

Choose a tiering policy per volume, determining when/whether user data blocks move to the cloud. Adjust the **cooling period** — days data must remain inactive before being moved: 2–183 days (ONTAP 9.8+) or 2–63 days (earlier versions); 2–63 is recommended best practice.

- **No Policy (None)**: Keeps all data in the performance tier; nothing moves to the cloud tier.
- **Cold snapshots (Snapshot only)**: Tiers cold Snapshot blocks not shared with the active file system. Reheated data returns to performance tier if read. Tiered only after an aggregate reaches 50% capacity and data reaches the cooling period (default 2 days, adjustable). Reheated data written back only if space available (if performance tier >70% full, blocks continue to be accessed from the cloud tier).
- **Cold user data & snapshots (Auto)**: Tiers all cold blocks (snapshots and cold user data), excluding metadata. Random reads reheat data to performance tier; sequential reads (e.g., index/antivirus scans) leave data cold in the cloud tier. Available from ONTAP 9.4. Tiered after 50% aggregate capacity and cooling period (default 31 days, adjustable). Same >70% reheat caveat as above.
- **All user data (All)**: All data (excluding metadata) immediately marked cold and tiered ASAP — no 48-hour wait for new blocks (existing blocks require 48 hours to become cold when policy is newly set). Read data stays cold in the cloud tier (not written back). Available from ONTAP 9.6. Considerations: reduces storage efficiencies (inline only); use only if cold data won't change (object storage isn't transactional and fragments under change); impacts SnapMirror (reads from cloud tier, slower, can delay queued SnapMirror ops) — consider before assigning to source volumes in data protection relationships; also affects NetApp Backup and Recovery.
- **All DP user data (Backup)**: All data on a DP volume immediately moved to cloud tier; cold blocks stay cold if read (ONTAP 9.4+). Available for ONTAP 9.5 or earlier — replaced by the **All** policy starting ONTAP 9.6.
