# What's new in Cloud Volumes ONTAP
Source: https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/whats-new.html
Fetched: 2026-07-07

Last updated: 06/11/2026

Learn what's new with Cloud Volumes ONTAP management in the NetApp Console.

The enhancements described on this page are specific to managing Cloud Volumes ONTAP through the Console. To learn what's new with the Cloud Volumes ONTAP software itself, go to the [Cloud Volumes ONTAP Release Notes](https://docs.netapp.com/us-en/cloud-volumes-ontap-relnotes/index.html).

## 11 June 2026

### Support for a new Azure region in Cloud Volumes ONTAP

You can now deploy Cloud Volumes ONTAP 9.12.1 GA and later in single and multiple availability zones in Azure in the Malaysia West (malaysiawest) region. This includes support for both single-node and high-availability (HA) deployments.

For a list of all regions, refer to the Global Regions Map under Azure (https://bluexp.netapp.com/cloud-volumes-global-regions).

## 08 June 2026

### Support for new EC2 instances for Cloud Volumes ONTAP in AWS

Cloud Volumes ONTAP 9.16.1 and later support M6id and M6idn EC2 instance families for both new and existing single-node and high-availability (HA) pair deployments in AWS. These 6th-generation instances offer faster processing power, stronger networking capabilities, and higher performance compared to the 5th generation general purpose systems.

- **M6id instances**: Provide a balance of compute and memory with high-speed, low-latency local NVMe storage. All M6id instance sizes support Flash Cache. These instances are well suited for workloads such as data logging and media processing.
- **M6idn instances**: Provide the same local NVMe storage capabilities as M6id instances. All M6idn instance sizes support Flash Cache.

We do not recommend the smaller-sized m6id.xlarge, m6id.2xlarge, m6idn.xlarge, and m6idn.2xlarge instance types for high-performance or memory-intensive workloads. For these workloads, use an instance type with a higher core count and larger memory.

For more information, refer to Supported configurations for Cloud Volumes ONTAP in AWS (https://docs.netapp.com/us-en/cloud-volumes-ontap-relnotes/reference-configs-aws.html).

## 18 May 2026

### Simplified Cloud Volumes ONTAP deployment in Azure

You can now use Quick create to deploy Cloud Volumes ONTAP in Azure for both single-node and high-availability (HA) configurations. This streamlined process reduces the number of steps compared to the advanced method, automatically sets default values on a single page, and minimizes navigation, making deployment faster and easier.

Related links:
- Deploy Cloud Volumes ONTAP in Azure with Quick create (https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-quick-deploy-azure.html)
- Deploy Cloud Volumes ONTAP using advanced options in Azure (https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-deploying-otc-azure.html)

## 12 May 2026

### Flexible billing for Cloud Volumes ONTAP and data services in AWS

NetApp offers enhanced billing options for your Cloud Volumes ONTAP subscriptions in AWS, giving you more control over how you pay for Cloud Volumes ONTAP capacity and NetApp data services, such as NetApp Backup and Recovery. Previously, all Cloud Volumes ONTAP and data services usage were billed together through the NetApp Intelligent Services (NIS) listing in the AWS marketplace.

Due to changes in AWS Enterprise Discount Program (EDP), NetApp has introduced a standalone Cloud Volumes ONTAP subscription in the AWS marketplace that allows you to separate the billing of Cloud Volumes ONTAP capacity from data services. This separation gives you more flexibility in managing your EDP credits and costs. NetApp recommends using the standalone subscription for better cost management of your Cloud Volumes ONTAP usage, while continuing to use the NIS subscription for billing data services after July 31, 2026, when the EDP requirements take effect.

The standalone Cloud Volumes ONTAP subscription in AWS supports only valid capacity-based Essentials or Freemium license packages. The Professional package is not supported. You can select the billing method that best suits your needs:

- **Standalone Cloud Volumes ONTAP subscription (Recommended)**: Pay for your Cloud Volumes ONTAP usage through the standalone subscription in the AWS marketplace, while continuing to bill data services through the NIS subscription. This is the recommended option for most customers who have both standalone and NIS subscriptions associated with their AWS account in the NetApp Console.
- **Combined NIS subscription**: Pay for both Cloud Volumes ONTAP and data services together through the existing NIS listing. The combined approach will be valid for existing customers who have only NIS subscriptions associated with their AWS account in the NetApp Console. However, NetApp recommends that you set your billing preference for your Cloud Volumes ONTAP usage and switch to the standalone subscription for better cost management.

Depending on your subscription type, you get these scenarios:

**Standalone subscription only (new customers)** — If you have only a standalone AWS subscription associated with your AWS account in the NetApp Console and no NIS subscriptions, you can select only the Essentials license package during deployment. The data services Backup and Recovery option is unavailable to you.

**Both standalone and NIS subscriptions (existing customers)** — If you have both NIS and standalone subscriptions associated with your AWS account, and you haven't set a billing preference through the Billing preferences tab in the NetApp Console, Cloud Volumes ONTAP usage continues to bill through NIS by default. This is also the default for any Cloud Volumes ONTAP instance running the Professional package, because the standalone listing does not support Professional. You can set a billing preference and choose how to bill each service:

- Set the standalone subscription as the preferred billing account for Cloud Volumes ONTAP (with Essentials package). If you have only the Professional package, you can convert it to an Essentials package and charge your Cloud Volumes ONTAP usage by setting the billing preference. We recommend this approach because it helps you manage your Cloud Volumes ONTAP EDP credits more effectively.
- Use the NIS subscription for billing data services, or the Cloud Volumes ONTAP usage through the Professional package. During deployment, enable the Backup and Recovery data service and select the Professional license package to bill data services through the NIS subscription.

**NIS subscription only (existing customers)** — This is applicable if you are an existing customer with NIS subscriptions associated with the AWS account. You can continue billing both Cloud Volumes ONTAP and data services together as you do now. However, NetApp recommends switching to the standalone subscription approach for better cost management of your Cloud Volumes ONTAP usage:

- Subscribe to a new standalone listing on the AWS portal.
- Link the standalone subscription to your AWS account.
- Set your billing preference to the standalone subscription for Cloud Volumes ONTAP usage with the Essentials package.
- (If applicable) Convert your Professional package to an Essentials package and set the billing preference.
- Continue billing data services through your NIS subscription.

> Note: No duplicate metering occurs when you use multiple subscription types or migrate between listings.

Related links:
- Set up licensing for Cloud Volumes ONTAP in AWS (https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-set-up-licensing-aws.html)
- Change charging methods for capacity licenses (https://docs.netapp.com/us-en/console-licenses-subscriptions/task-manage-capacity-licenses.html#change-charging-methods)

## 13 April 2026

### Improved Cloud Volumes ONTAP support with Google Cloud C3 VMs

Cloud Volumes ONTAP now has enhanced support for the Google Cloud C3 series VMs, enabling these additional capabilities:

- In your Cloud Volumes ONTAP deployments, you can switch instance types among different variants within the C3 family.
- When changing the instance type, if you select c3-standard-44 or c3-standard-88 and their LSSD variants as the target VM, the Google network service egress network tier Tier-1 is applied automatically. If you switch to any other C3 variant, the egress network tier is set to Standard. (Note: Changing the egress network tier to Tier-1 incurs additional costs. Plan the deployment and upgrade accordingly.)
- If you select the local SSD (LSSD) variants of C3, Flash Cache gets enabled by default. You can't switch between C3 LSSD variants in your Cloud Volumes ONTAP deployment, even if the target variant supports Flash Cache.
- On your C3 VMs, you can now add volumes to both new and existing aggregates.
- You can change the IOPS and throughput settings when adding volumes through the NetApp Console or by using the `PUT /gcp/vsa/aggregates/{workingEnvironmentId}/{aggregateName}` API.

Related links:
- Supported configurations for Cloud Volumes ONTAP in Google Cloud (https://docs.netapp.com/us-en/cloud-volumes-ontap-relnotes/reference-configs-gcp.html)
- Cloud Volumes ONTAP support for next generation Google Cloud VMs (see 17 February 2025 entry below)

## 10 March 2026

### Ability to manage Console agent proxy settings for Cloud Volumes ONTAP

You can now manage proxy settings on the NetApp Console agent for Cloud Volumes ONTAP, even if you lose connection or the proxy is set up incorrectly. Previously, if the Console agent could not connect to Cloud Volumes ONTAP for 20 minutes, it overwrote your manual proxy settings with default settings. This caused communication failures, including issues with AutoSupport messages. To retain your proxy settings for existing systems, run the following API call:

`PUT /occm/config`

Include the following parameter in the request body:

```json
{
  "proxyMode": "No_Overwrites"
}
```

The default mode is standard, which means the Console agent overwrites your proxy settings with defaults if it cannot connect to Cloud Volumes ONTAP for 20 minutes.

[Configure modifiable NetApp Console parameters](https://docs.netapp.com/us-en/console-automation/cvo/put-occm-config.html)

## 26 February 2026

### Support for Google Infrastructure Manager for private mode deployments

Cloud Volumes ONTAP 9.16.1 and later now support Google Cloud Infrastructure Manager (IM) instead of Cloud Deployment Manager (DM) for new private mode deployments in Google Cloud. Google will deprecate Deployment Manager as an infrastructure service in the near future for the more advanced Infrastructure Manager.

Beginning February 25, 2026, Cloud Volumes ONTAP uses Infrastructure Manager for new and existing private mode deployments. Basic workflows:

| Scenario | Action | New APIs for the agent | New permissions for the agent | New Google Cloud APIs for Cloud Volumes ONTAP | Doc resources |
|---|---|---|---|---|---|
| Existing agent and existing deployment in private mode | Upgrade to the latest version of NetApp Console agent by downloading the installer from the NetApp Support Site and then manually installing the agent on your host, so that it can use Infrastructure Manager APIs. Thereafter, convert the existing Cloud Volumes ONTAP systems to use Infrastructure Manager. | Cloud Infrastructure Manager API, Cloud Quotas API, Cloud Build API | All permissions listed for the Console release on 8 Dec 2025 and 09 Feb 2026, plus cloudbuild.workerpools.get | https://cloudbuild.googleapis.com/v1, https://www.googleapis.com/upload/storage/v1, https://config.googleapis.com/v1 | Configure existing Cloud Volumes ONTAP deployments for Google Cloud Infrastructure Manager (task-gcp-dm-im-conv.html) |
| New agent and new deployment | Create a new agent and deploy a new Cloud Volumes ONTAP system in private mode. | — | — | — | Create a Console agent from Google Cloud; Quick start for private mode deployments |

In private mode deployments, you need a few configuration changes for Cloud Volumes ONTAP to start using Infrastructure Manager. Refer to Infrastructure Manager configuration for private mode deployments (reference-networking-gcp.html#infrastructure-manager-configuration-for-private-mode-deployments).

Related links:
- NetApp Console Agent 4.2.0 Release Notes
- Permissions required for Google Cloud Infrastructure Manager

## 19 February 2026

### New regions supported in Azure

You can now deploy Cloud Volumes ONTAP 9.12.1 GA and later in single and multiple availability zones in Azure in the following regions. This includes support for both single-node and high-availability (HA) deployments.

- Japan West (japanwest)
- Indonesia Central (indonesiacentral)

For a list of all regions, refer to the Global Regions Map under Azure.

## 17 February 2026

### Cloud Volumes ONTAP support for next generation Google Cloud VMs

With 9.18.1, NetApp transitions new Cloud Volumes ONTAP deployments off N2 VMs to the next generation Google Cloud C3 series VMs for a faster and more scalable experience. You can now take advantage of C3 series VMs while deploying Cloud Volumes ONTAP 9.18.1 and later in Google Cloud. The C3 series machines offer improved performance and higher capacity limits by using Google Virtual NIC (gVNIC) and Hyperdisk Balanced disks that ensure dynamic performance for intensive workloads.

> Note: For now, Cloud Volumes ONTAP supports the C3 series only in single-node deployments.

If your Cloud Volumes ONTAP system runs 9.18.1 or later, the preconfigured packages that you use for easy single node deployments automatically use C3 VMs, while enabling you to customize the IOPS and throughput parameters based on your workload needs. Similarly, while creating aggregates, you can add Hyperdisk Balanced disks to achieve better performance and scalability in Google Cloud. Additionally, you can select the LSSD variants of the C3 series machines for default Flash Cache support.

You can't change the disk type for C3 VMs when adding volumes to aggregates because C3 supports only Hyperdisk Balanced disks. Similarly, when replicating a system with N2 VM types to a C3 VM, the disk type is set by default to Hyperdisk Balanced.

Related: Supported configurations for Cloud Volumes ONTAP in Google Cloud; Google documents: C3 machine series.

### VNet security for Cloud Volumes ONTAP in Azure

Cloud Volumes ONTAP 9.18.1 and later deployments in Azure single and multiple availability zones support Azure Virtual Network (VNet) encryption as part of its layered security strategy to protect data in transit. Cloud Volumes ONTAP leverages Azure's native Datagram Transport Layer Security (DTLS) protocol to secure communication between ONTAP nodes, management interfaces, and other Azure services, preventing interception and unauthorized access. This network-level encryption complements ONTAP's built-in storage and data-at-rest protections to deliver end-to-end security of your data.

Related: Networking for Azure VNet encryption (reference-networking-azure.html#networking-for-azure-vnet-encryption)

## 12 February 2026

### Support for Ebdsv5 and E104ids_v5 VMs in Azure

Beginning with Cloud Volumes ONTAP 9.18.1, you can deploy Ebdsv5 and E104ids_v5 VMs for single-node and high-availability (HA) deployments and upgrades.

Ebdsv5 VMs within the Eb family of Azure virtual machines are optimized for higher remote storage performance. You can use these VMs for memory-intensive and I/O-heavy enterprise workloads, such as relational databases, in-memory analytics, and other demanding business-critical applications.

E104ids_v5 is an isolated VM instance that helps you better handle scheduled maintenance windows. Compared to E80ids_v4, it offers much higher disk throughput and IOPS, along with better overall network performance.

Related: Supported configurations for Cloud Volumes ONTAP in Azure; Azure documentation: Edsv5 sizes series.

## 10 February 2026

### Cloud Volumes ONTAP 9.18.1 GA

You can now use the NetApp Console to deploy and manage the General Availability (GA) version of Cloud Volumes ONTAP 9.18.1 in AWS, Azure, and Google Cloud. Learn more about this release of Cloud Volumes ONTAP.

## 9 February 2026

### Support for Google Cloud Infrastructure Manager

Cloud Volumes ONTAP 9.16.1 and later now support Google Cloud Infrastructure Manager (IM) instead of Cloud Deployment Manager (DM) for new deployments in Google Cloud. Google will deprecate Deployment Manager as an infrastructure service in the near future for the more advanced Infrastructure Manager.

Beginning February 09, 2026, Cloud Volumes ONTAP uses Infrastructure Manager for new and existing deployments. Workflows:

| Scenario | Action | New APIs for the agent | New permissions for the agent | New Google Cloud APIs for Cloud Volumes ONTAP | Doc resources |
|---|---|---|---|---|---|
| Existing agent and existing Cloud Volumes ONTAP deployment | Add new APIs and permissions to the existing agent and convert the existing Cloud Volumes ONTAP system. | Cloud Infrastructure Manager API, Cloud Quotas API | All permissions listed for the Console release on 8 Dec 2025 and 09 Feb 2026 | https://www.googleapis.com/upload/storage/v1, https://config.googleapis.com/v1 | Configure existing Cloud Volumes ONTAP deployments for Google Cloud Infrastructure Manager |
| Existing agent and new Cloud Volumes ONTAP deployment | Add new APIs and permissions to the existing agent and deploy a new Cloud Volumes ONTAP system. | Cloud Infrastructure Manager API, Cloud Quotas API | Same as above | All steps for new deployment | Getting started with Cloud Volumes ONTAP in Google Cloud |
| New agent and new deployment | Create a new agent and deploy a new Cloud Volumes ONTAP system. | — | — | — | Create a Console agent from Google Cloud; Getting started with Cloud Volumes ONTAP in Google Cloud |

Now, deploy Cloud Volumes ONTAP to automatically use Infrastructure Manager or switch your existing deployments in Deployment Manager to Infrastructure Manager by running a conversion tool. The conversion is a one-time process, after which your systems will start using Infrastructure Manager. Refer to Configure existing Cloud Volumes ONTAP deployments for Google Cloud Infrastructure Manager for instructions on running the conversion tool.

Cloud Volumes ONTAP systems that use Infrastructure Manager use Google Cloud Storage buckets to store data and records in the zone of the first deployment to store deployment records, which are reused for subsequent deployments. You might incur extra costs for these buckets, but do not edit or delete the buckets or their content:

- `gs://netapp-cvo-infrastructure-manager-<project id>`: for ONTAP versions and SVM Terraform Templates used for new Cloud Volumes ONTAP deployments. Inside this, the `dm-to-im-convert` bucket contains the Cloud Volumes ONTAP Terraform files.
- `<gcp project number>-<region>-blueprint-config`: for storing Google Cloud Terraform artifacts.

Related links: Getting started with Cloud Volumes ONTAP in Google Cloud; NetApp Console Agent 4.2.0 Release Notes; Permissions required for Google Cloud Infrastructure Manager.

## 12 January 2026

### Preferred billing option for Cloud Volumes ONTAP

You can now select a preferred billing option for calculating your Cloud Volumes ONTAP usage and overages. Since the limited availability of the Bring Your Own Licenses (BYOL) licensing model on June 25, 2025, NetApp has added preferred charging methods in the Licensing and Subscriptions section of the NetApp Console. You can use either your annual marketplace subscription for billing and overages or the existing BYOL model as the preferred option. This gives you the flexibility to choose the charging method that best fits your organization's financial strategy and usage patterns.

Related: Billing preferences and overages (concept-licensing-charging.html#billing-preferences-and-overages).

## 10 December 2025

### Ability to enhance performance of Premium SSD v2 disks in Azure

You can now enhance the performance of Premium SSD v2 Managed Disks in Azure by modifying the IOPS and throughput parameters. Using this capability, you can optimize the storage performance of your systems based on your workload requirements.

Related: Manage Premium SSD v2 disk performance for Cloud Volumes ONTAP in Azure (task-manage-perf-params-azure.html).

### Overage charging for Essentials licenses simplified

For Cloud Volumes ONTAP marketplace annual contracts/private offers, overage calculations for Essentials licenses is now aligned with Bring Your Own License (BYOL) packages. Previously, overages were billed at hourly marketplace rates for the exact Essentials package. Now, if your marketplace annual contract includes multiple Essentials packages, the NetApp Console charges overages for an Essentials package against the available capacity of a higher-priced Essentials package in your subscription. This simplifies overage calculations for Essentials packages and ensures a smooth transition from BYOL licensing to a subscription-based model.

Related: How overages are charged for Essentials licenses (concept-licensing-charging.html#how-overages-are-charged-for-essentials-licenses).

### Support for Azure Edsv6 sizes series

Beginning with Cloud Volumes ONTAP 9.17.1, you can deploy Azure Edsv6 series VMs through the NetApp Console for new Cloud Volumes ONTAP instances. Cloud Volumes ONTAP 9.17.1 and later will support only Generation 2 VMs for new deployments. These Generation 2 machines are compatible with the latest technologies, such as Unified Extensible Firmware Interface (UEFI), Azure Boost systems, and NVMe. They are ideal for memory-intensive systems and applications that need fast, local storage, such as database servers and analytics engines.

Related: Supported configurations for Cloud Volumes ONTAP in Azure (reference-configs-azure.html#supported-configurations-by-license).

## 10 November 2025

### Enhanced NVMe-TCP Support

Earlier, when deploying Cloud Volumes ONTAP instances over NVMe-TCP, you would have to manually obtain and apply NVMe licenses before deployment. With this update, Cloud Volumes ONTAP now automatically installs the required NVMe licenses during deployment, simplifying the setup process.

For existing NVMe-TCP deployments that lack licenses, Cloud Volumes ONTAP applies the licenses automatically. You must restart the system for the licenses to take effect.

Related: Supported client protocols for Cloud Volumes ONTAP: NVMe-TCP (concept-client-protocols.html#nvme-tcp).

## 17 October 2025

### Cloud Volumes ONTAP in Azure now limited to latest supported versions

Cloud Volumes ONTAP deployments and upgrades in Azure through the NetApp Console are now restricted to the latest supported versions. This ensures compatibility with the latest generation hardware supported by Microsoft and provides the newest features and security enhancements. The Console will prompt you to upgrade to the supported versions.

Related: Supported ONTAP versions for Cloud Volumes ONTAP deployments (Azure section); Supported upgrade paths for Azure (task-updating-ontap-cloud.html#supported-upgrade-paths).

## 06 October 2025

### BlueXP is now NetApp Console

The NetApp Console, built on the enhanced and restructured BlueXP foundation, provides centralized management of NetApp storage and NetApp Data Services across on-premises and cloud environments at enterprise grade — delivering real-time insights, faster workflows, and simplified administration, that is highly secure and compliant.

For details on what has changed, see the NetApp Console release notes (bluexp-relnotes/index.html).

### Simplified Cloud Volumes ONTAP deployment in AWS

You can now deploy Cloud Volumes ONTAP in AWS using a quick deployment method for both single-node and high-availability (HA) configurations. This streamlined process reduces the number of steps compared to the advanced method, automatically sets default values on a single page, and minimizes navigation, making deployment faster and easier.

Related: Deploy Cloud Volumes ONTAP in AWS using quick deployment (bluexp-cloud-volumes-ontap/task-quick-deploy-aws.html).

## 04 September 2025

### Cloud Volumes ONTAP 9.17.1 RC

You can now use BlueXP to deploy and manage the Release Candidate 1 of Cloud Volumes ONTAP 9.17.1 in Azure and Google Cloud. However, this version is not available for deployment and upgrade in AWS.

## 11 August 2025

### End of availability of Optimized licenses

Beginning on August 11, 2025, the Cloud Volumes ONTAP Optimized license will be deprecated and will no longer be available for purchase or renewal in the Azure and Google Cloud marketplaces for pay-as-you-go (PAYGO) subscriptions. If you have an existing annual contract with an Optimized license, you can continue to use the license until the end of your contract. When your Optimized license expires, you can opt for Cloud Volumes ONTAP Essentials or Professional licenses in BlueXP.

However, the ability to add or renew Optimized licenses will be available through the APIs.

## 14 July 2025

### Support for transparent proxy

BlueXP now supports transparent proxy servers in addition to the existing explicit proxy connections. When creating or modifying the BlueXP Connector, you can configure a transparent proxy server to securely manage network traffic to and from Cloud Volumes ONTAP.

### New VM type supported for Cloud Volumes ONTAP in Azure

Beginning with Cloud Volumes ONTAP 9.13.1, L8s_v3 is supported as a VM type in Azure single and multiple availability zones, for both new and existing high-availability (HA) pair deployments.

## 25 June 2025

### Restricted availability of BYOL licensing for Cloud Volumes ONTAP

Beginning June 25, 2025, NetApp has restricted the bring your own license (BYOL) licensing model for Cloud Volumes ONTAP. The restriction applies to all customers and Cloud Volumes ONTAP deployments in AWS, Azure, and Google Cloud. The only exemptions are the U.S. Public Sector customers and China region deployments.

NetApp support and services will continue until your BYOL contract expires, but your expired licenses will not be renewed or extended. When your BYOL licenses expire, you must replace them with capacity-based licenses purchased through your cloud marketplace subscriptions. Contact your NetApp accounts team or customer success representatives to discuss your options of conversion.

## 29 May 2025

### Private mode deployments enabled for Cloud Volumes ONTAP 9.15.1

You can now deploy Cloud Volumes ONTAP 9.15.1 in private mode in AWS, Azure, and Google Cloud, for both single-node and high-availability (HA) deployments.

## 12 May 2025

### Discovery of deployments made through the Azure marketplace in BlueXP

BlueXP now has the capability of discovering the Cloud Volumes ONTAP systems deployed directly through the Azure marketplace, as working environments, just like any other Cloud Volumes ONTAP system.

## 16 April 2025

### New regions supported in Azure

New Cloud Volumes ONTAP 9.12.1 GA+ single/multi-AZ regions: Spain Central, Mexico Central.

## 14 April 2025

### Storage VM creation automated through the APIs in Google Cloud

You can now use the BlueXP APIs to automate storage VM creation in Google Cloud, for single node deployments (previously only HA). Create, rename, and delete additional data-serving storage VMs without manually configuring network interfaces, LIFs, and management LIFs.

## 03 April 2025

### Support for China regions for Cloud Volumes ONTAP 9.13.1 in AWS

Single-node deployments; only licenses purchased directly from NetApp are supported.

## 28 March 2025

### Private mode deployments enabled for Cloud Volumes ONTAP 9.14.1

Single-node and HA deployments in AWS, Azure, Google Cloud.

## 12 March 2025

### New regions supported for multiple availability zone deployments in Azure

Central US; US Gov Virginia — HA multiple AZ for 9.12.1 GA+.

## 10 March 2025

### Storage VM creation automated through the APIs in Azure

Create, rename, delete additional data-serving storage VMs including network interfaces, LIFs, and management LIF.

## 06 March 2025

### Cloud Volumes ONTAP 9.16.1 GA

Available in Azure and Google Cloud (not AWS for deployment/upgrade).

## 03 March 2025

### Support for New Zealand North region in Azure

Single node and HA for 9.12.1 GA+. Lsv3 instance type not supported in this region.

## 18 February 2025

### Introducing Azure marketplace direct deployment

Deploy Cloud Volumes ONTAP directly from the Azure marketplace without setting up the BlueXP Connector or other onboarding criteria.

## 10 February 2025

### User authentication enabled for accessing System Manager from BlueXP

BlueXP administrators can activate authentication for ONTAP users accessing ONTAP System Manager from BlueXP (standard and private modes).

### BlueXP Advanced View renamed to System Manager

### Introducing a simpler way to manage licenses with the BlueXP digital wallet

Improved navigation: Administration > Licenses and subscriptions > Overview/Direct Licenses tabs; View on Cloud Volumes ONTAP panel for advanced license insight; Switch to legacy view button available.

## 09 December 2024

### List of supported VMs updated for Azure to align with the best practices

DS_v2 and Es_v3 machine families no longer selectable for new deployments (only via API); retained for existing systems. New deployments supported only from 9.12.1. Recommend Es_v4 or later-compatible series.

## 11 November 2024

### End of availability for node-based licenses

EOA of node-based licensing began 11 November 2024; support ends 31 December 2024. Transition to capacity-based licensing using the BlueXP license conversion tool.

### Removal of node-based deployments from BlueXP

Deprecated except for: U.S. Public Sector customers, private mode deployments, China region AWS deployments, and valid non-expired by-node BYOL licenses.

### Addition of a cold tier for Cloud Volumes ONTAP data on Azure Blob storage

Cold tier added alongside hot and cool tiers for inactive capacity tier data.

### Option to restrict public access to storage account for Azure

Restrict public access to secure private IP even within the same VNet; disables data tiering; applies to single node and HA pairs.

### WORM enablement after deploying Cloud Volumes ONTAP

Activate WORM on an existing system even if not enabled at creation. Once enabled, cannot be disabled.

## 25 October 2024

### List of supported VMs updated for Google Cloud to align with the best practices

n1 series no longer selectable for new instances (only via API); retained for existing systems. New deployments supported only from 9.8. Recommend n2 series.

### Local Zones support for Amazon Web Services in private mode

AWS Local Zones support for HA extended from standard mode to include private mode. Not supported in restricted mode.

## 07 October 2024

### Enhanced user experience in version selection for upgrade

Guidance on default, latest, and compatible versions; select latest patch/major compatible version or manually enter a version.

## 09 September 2024

### WORM and ARP functionalities are no longer chargeable

WORM and ARP offered at no extra cost for new/existing BYOL and PAYGO/marketplace subscriptions across AWS, Azure, Google Cloud; applies to capacity-based and node-based licenses, single node and HA.

## 23 August 2024

### Canada West region now supported in AWS

For Cloud Volumes ONTAP 9.12.1 GA+.

## 22 August 2024

### Cloud Volumes ONTAP 9.15.1 GA

Deploy/manage in AWS, Azure, Google Cloud.

## 08 August 2024

### Edge Cache licensing packages deprecated

No longer available for future deployments (API still usable).

### Minimum version support for Flash Cache in Azure

Minimum version 9.13.1 GA required for Flash Cache in Azure.

### Free trials for marketplace subscriptions deprecated

30-day automatic free trial/evaluation license for PAYGO subscriptions removed; charging activated from first use.

## 10 June 2024

### Cloud Volumes ONTAP 9.15.0

Deploy/manage in AWS, Azure, Google Cloud.

## 17 May 2024

### Amazon Web Services Local Zones support

Available for Cloud Volumes ONTAP HA deployments (standard mode only; not restricted or private mode at this time).

## 23 April 2024

### New regions supported for multiple availability zone deployments in Azure

Germany West Central, Poland Central, West US 3, Israel Central, Italy North, Canada Central — HA multi-AZ for 9.12.1 GA+.

### Johannesburg region now supported in Google Cloud

africa-south1 region for 9.12.1 GA+.

### Volume templates and tags no longer supported

Removed along with the deprecated BlueXP remediation service.

## 08 March 2024

### Amazon Instant Metadata Service v2 support

Cloud Volumes ONTAP, Mediator, and Connector now support IMDSv2 for all functions (enhanced protection vs. IMDSv1-only previously).

## 05 March 2024

### Cloud Volumes ONTAP 9.14.1 GA

Deploy/manage in AWS, Azure, Google Cloud.

## 02 February 2024

### Support for Edv5-series VMs in Azure

Starting with 9.14.1: E4ds_v5, E8ds_v5, E20s_v5, E32ds_v5, E48ds_v5, E64ds_v5.

## 16 January 2024

### Patch releases in BlueXP

Available only for the latest three versions of Cloud Volumes ONTAP.

## 08 January 2024

### New VMs for Azure multiple availability zones

Starting from 9.13.1: L16s_v3, L32s_v3, L48s_v3, L64s_v3 (new and existing HA pair deployments).

## 06 December 2023

### Cloud Volumes ONTAP 9.14.1 RC1

Deploy/manage in AWS, Azure, Google Cloud.

### 300 TiB FlexVol volume max limit

Available via System Manager/ONTAP CLI starting 9.12.1 P2 and 9.13.0 P2; in BlueXP starting 9.13.1.

## 05 December 2023

### New region support in Azure

Single AZ: Tel Aviv, Milan. Multi-AZ: Central India, Norway East, Switzerland North, South Africa North, United Arab Emirates North — for 9.12.1 GA+.

## 10 November 2023

Connector 3.9.35. Berlin region now supported in Google Cloud for 9.12.1 GA+.

## 08 November 2023

Connector 3.9.35. Tel Aviv region now supported in AWS for 9.12.1 GA+.

## 01 November 2023

Connector 3.9.34. Saudi Arabia region now supported in Google Cloud for 9.12.1 GA+.

## 23 October 2023

Connector 3.9.34. New regions for HA multi-AZ deployments in Azure: Australia East, East Asia, France Central, North Europe, Qatar Central, Sweden Central, West Europe, West US 2.

## 06 October 2023

Connector 3.9.34. Cloud Volumes ONTAP 9.14.0 GA in AWS, Azure, Google Cloud.

## 10 September 2023

Connector 3.9.33. Support for Lsv3-series VMs in Azure: L48s_v3 and L64s_v3 for single node and HA pair (shared managed disks, single/multi-AZ), starting 9.13.1; support Flash Cache.

## 30 July 2023

Connector 3.9.32.

### Flash Cache and high write speed support in Google Cloud

For 9.13.1+: high write speed on all supported instance types; Flash Cache on n2-standard-16/32/48/64. Usable separately or together, single node and HA.

### Usage reports enhancements

TiB unit in column names; new "node(s)" field for serial numbers; new "Workload Type" column under Storage VMs usage report; working environment names included in Storage VMs/Volume usage reports; volume type "file" relabeled "Primary (Read/Write)"; "secondary" relabeled "Secondary (DP)".

## 26 July 2023

Connector 3.9.31. Cloud Volumes ONTAP 9.13.1 GA in AWS, Azure, Google Cloud.

## 02 July 2023

Connector 3.9.31.

### Support for HA multiple availability zone deployments in Azure

Japan East and Korea Central now support HA multi-AZ for 9.12.1 GA+.

### Autonomous Ransomware Protection support

ARP supported on Cloud Volumes ONTAP 9.12.1+.

## 26 June 2023

Connector 3.9.30. Cloud Volumes ONTAP 9.13.1 RC1 in AWS, Azure, Google Cloud.

## 04 June 2023

Connector 3.9.30. Cloud Volumes ONTAP upgrade version selector update: choose latest available version or an older version.

## 07 May 2023

Connector 3.9.29.

- Qatar region now supported in Google Cloud for 9.12.1 GA+.
- Sweden Central region now supported in Azure for 9.12.1 GA+.
- Support for HA multi-AZ in Azure Australia East for 9.12.1 GA+.

### Charging usage breakdown

Downloadable usage reports from digital wallet: Cloud Volumes ONTAP package usage, High-level usage, Storage VMs usage, Volumes usage.

### Notification now displays when accessing BlueXP without a marketplace subscription

### New permissions added to AWS IAM policy for HA mediators

sts:AssumeRole, ec2:DescribeSubnets.

## 04 April 2023

### Support for China regions for AWS

Starting with 9.12.1 GA: single-node systems only; only licenses purchased directly from NetApp.

## 3 April 2023

Connector 3.9.28.

### Turin region now supported in Google Cloud

For 9.12.1 GA+.

### BlueXP digital wallet enhancement

Now shows licensed capacity purchased with marketplace private offers.

### Support for comments during volume creation

For FlexGroup/FlexVol volumes via API.

### BlueXP user interface redesign for Cloud Volumes ONTAP Overview, Volumes, and Aggregates pages

Tile-based design with more comprehensive information.

### FlexGroup Volumes viewable through Cloud Volumes ONTAP

FlexGroup volumes created via System Manager/CLI now viewable through the redesigned Volumes tile (view only, not creatable in BlueXP yet).

## 13 March 2023

### Support for China regions in Azure

China North 3 supported for single node 9.12.1 GA and 9.13.0 GA; only BYOL licenses from NetApp. Fresh deployments in China regions supported only in 9.12.1 GA and 9.13.0 GA (can upgrade later); contact NetApp Support for later versions.

## 05 March 2023

Connector 3.9.27. Cloud Volumes ONTAP 9.13.0 in AWS, Azure, Google Cloud.

### 16 TiB and 32 TiB support in Azure

For HA deployments on managed disks.

### MTEKM license

Multi-tenant Encryption Key Management license now included with new/existing systems running 9.12.1 GA+; enables individual SVMs to maintain own keys via KMIP server with NetApp Volume Encryption.

### Support for environments without internet

Node-based licensing (BYOL) only; capacity-based not supported. Manually install Connector software, log in to BlueXP console on Connector, add BYOL license to digital wallet, deploy Cloud Volumes ONTAP.

### Flash Cache and high write speed in Google Cloud

Support for Flash Cache, high write speed, and high MTU (8,896 bytes) for select instances with 9.13.0.

## 05 February 2023

Connector 3.9.26.

### Placement group creation in AWS

New setting to bypass failed placement group creations for HA single AZ deployments.

### Private DNS zone configuration update

New setting to avoid creating link between private DNS zone and virtual network when using Azure Private Links (enabled by default).

### WORM storage and data tiering

Can now enable data tiering with WORM storage together for 9.8+ systems.

## 1 January 2023

Connector 3.9.25.

### Licensing packages available in Google Cloud

Optimized and Edge Cache capacity-based packages available as PAYGO or annual contract.

### Default configuration for Cloud Volumes ONTAP

MTEKM license no longer included by default in new deployments.

## 15 December 2022

### Cloud Volumes ONTAP 9.12.0

Deploy/manage in AWS and Google Cloud.

## 08 December 2022

### Cloud Volumes ONTAP 9.12.1

New features plus additional cloud provider regions.

## 04 December 2022

Connector 3.9.24.

### WORM + Cloud Backup now available during Cloud Volumes ONTAP creation

### Israel region now supported in Google Cloud

For 9.11.1 P3+.

## 15 November 2022

Connector 3.9.23.

### ONTAP S3 license in Google Cloud

Included on new/existing systems running 9.12.1+ in GCP.

## 06 November 2022

Connector 3.9.23.

### Moving resource groups in Azure

Move working environment between resource groups within the same subscription.

### NDMP-copy certification

NDMP-copy certified for use with Cloud Volumes ONTAP.

### Managed disk encryption support for Azure

New permission allows encrypting all managed disks upon creation.

## 18 September 2022

Connector 3.9.22.

### Digital Wallet enhancements

Summary of Optimized I/O package and provisioned WORM capacity across account; change from one charging method to Optimized charging method.

### Optimize cost and performance

Optimize Cost & Performance option from the Canvas to change instance type.

### AutoSupport notifications

BlueXP notification if a system is unable to send AutoSupport messages, with troubleshooting link.

## 31 July 2022

Connector 3.9.21.

### MTEKM license

Included with new/existing systems running 9.11.1+.

### Proxy server

BlueXP auto-configures Cloud Volumes ONTAP to use the Connector as a proxy server if outbound internet isn't available for AutoSupport. Requires Connector security group to allow inbound connections over port 3128.

### Change charging method

Change charging method for capacity-based licensed systems (e.g., Essentials to Professional) via Digital Wallet.

### Security group enhancement

Choose predefined security group to allow traffic within selected network only (recommended) or all networks.

## 18 July 2022

### New licensing packages in Azure

Optimized (pay for provisioned capacity and I/O operations separately) and Edge Cache (for Cloud Volumes Edge Cache), via Azure Marketplace subscription.

## 3 July 2022

Connector 3.9.20.

### Digital Wallet

Shows total consumed capacity and consumed capacity by licensing package.

### Elastic Volumes enhancement

AWS EBS Elastic Volumes support when creating a working environment via UI; enabled by default with gp3/io1 disks.

### ONTAP S3 license in AWS

Included on new/existing systems running 9.11.0+ in AWS.

### New Azure Cloud region support

West US 3 starting with 9.10.1.

### ONTAP S3 license in Azure

Included on new/existing systems running 9.9.1+ in Azure.

## 07 June 2022

Connector 3.9.19. Cloud Volumes ONTAP 9.11.1: new features plus additional cloud provider regions.

### New Advanced View

ONTAP System Manager embedded directly inside BlueXP (Preview, available 9.10.0+).

### Support for Amazon EBS Elastic Volumes

Better performance/capacity with automatic disk capacity increase; available with new 9.11.0 systems, gp3/io1 EBS types. Requires new AWS Connector permissions: ec2:DescribeVolumesModifications, ec2:ModifyVolume.

### Support for deploying HA pairs in shared AWS subnets

9.11.1 supports AWS VPC sharing; deploy HA pair in shared subnet using the API.

### Limited network access when using service endpoints

BlueXP limits network access when using VNet service endpoint (used if Azure Private Link disabled).

### Support for creating storage VMs in Google Cloud

Multiple storage VMs supported starting 9.11.1; create via API on HA pairs. Requires new GCP permissions: compute.instanceGroups.get, compute.addresses.get. Single-node systems still require ONTAP CLI/System Manager for storage VM creation.

## 02 May 2022

Connector 3.9.18. Cloud Volumes ONTAP 9.11.0.

### Enhancement to mediator upgrades

Validates new mediator image availability before deleting boot disk.

### K8s tab has been removed

### Annual contract in Azure

Essentials and Professional packages available via annual contract (private offer in Azure Marketplace).

### S3 Glacier Instant Retrieval

Tiered data can be stored in S3 Glacier Instant Retrieval storage class.

### New AWS permissions required for the Connector

ec2:DescribePlacementGroups, iam:GetRolePolicy — for optimized spread placement group creation for HA single AZ.

### New Google Cloud region support

Starting 9.10.1: Delhi (asia-south2), Melbourne (australia-southeast2), Milan (europe-west8, single node only), Santiago (southamerica-west1, single node only).

### Support for n2-standard-16 in Google Cloud

Starting 9.10.1.

### Enhancements to Google Cloud firewall policies

Display all existing firewall policies in a VPC (previously wouldn't display policies without a target tag); choose whether predefined firewall policy allows traffic within selected VPC only or all VPCs (single-node).

### Enhancement to Google Cloud service accounts

Display email address associated with each service account for easier distinction.

## 3 April 2022

### System Manager link has been removed

Can still connect via cluster management IP in a browser.

### Charging for WORM storage

Introductory special rate expired; now charged hourly per provisioned WORM capacity for new and existing systems.

## 27 February 2022

Connector 3.9.16.

### Redesigned volume wizard

Available when creating a volume on a specific aggregate via Advanced allocation option.

## 09 February 2022

### Marketplace updates

Essentials and Professional packages (by-capacity, hourly or annual) now available in all cloud provider marketplaces; existing subscribers auto-subscribed. By-node licensing from marketplaces deprecated for new subscribers (still available for existing active subscriptions).

## 06 February 2022

### Exchange unassigned licenses

Convert unused unassigned node-based Cloud Volumes ONTAP license to Cloud Backup, Cloud Data Sense, or Cloud Tiering license (revokes CVO license, creates dollar-equivalent license with same expiry).

## 30 January 2022

Connector 3.9.15.

### Redesigned licensing selection

Highlights by-capacity charging methods (introduced July 2021).

### Digital Wallet update

Consolidated Cloud Volumes ONTAP licenses into a single tab.

## 02 January 2022

Connector 3.9.14.

### Support for additional Azure VM types

Starting 9.10.1: E4ds_v4, E8ds_v4, E32ds_v4, E48ds_v4.

### FlexClone charging update

No longer charged for capacity used by FlexClone volumes under capacity-based licensing.

### Charging method now displayed

Shown for each working environment in the Canvas right panel.

### Choose your user name

Option to enter preferred user name instead of default admin during working environment creation.

### Volume creation enhancements

Redesigned create volume wizard; custom export policy option for NFS.

## 28 November 2021

Connector 3.9.13. Cloud Volumes ONTAP 9.10.1.

### NetApp Keystone Subscriptions

Pay-as-you-grow subscription service for Cloud Volumes ONTAP HA pairs; supported with all new deployable versions.

### New AWS region support

AWS Asia Pacific (Osaka) region (ap-northeast-3).

### Port reduction

Ports 8023 and 49000 no longer open on Azure Cloud Volumes ONTAP systems (single-node and HA), for new systems starting with Connector 3.9.13.

## 04 October 2021

Connector 3.9.11. Cloud Volumes ONTAP 9.10.0.

### Reduced deployment time

3-4 minutes shorter on average in Azure/Google Cloud with normal write speed enabled.

## 02 September 2021

Connector 3.9.10.

### Customer-managed encryption key in Azure

Use your own customer-managed key instead of Microsoft-managed key (create key vault + key in Azure, use API to create CVO working environment referencing the key).

## 07 July 2021

Connector 3.9.8.

### New charging methods

Capacity-based BYOL (Essentials or Professional package); Freemium (free, limited to 500 GiB provisioned capacity per system, up to 10 Freemium systems, no support contract).

### WORM storage available for general use

Out of Preview.

### Support for m5dn.24xlarge in AWS

Starting 9.9.1; PAYGO Premium, BYOL, Freemium charging methods.

### Select existing Azure resource groups

Option to select existing resource group for VM and associated resources. New permissions: Microsoft.Network/privateEndpoints/delete, Microsoft.Compute/availabilitySets/delete.

### Blob public access now disabled in Azure

Disabled by default when creating storage account.

### Azure Private Link enhancement

Private Link connection enabled by default on boot diagnostics storage account; all storage accounts now use private link.

### Balanced persistent disks in Google Cloud

Support for pd-balanced starting 9.9.1.

### custom-4-16384 no longer supported in Google Cloud

Existing systems can keep using it; recommend switching to n2-standard-4.

## 30 May 2021

Connector 3.9.7.

### New Professional Package in AWS

Bundles Cloud Volumes ONTAP and Cloud Backup Service via AWS Marketplace annual contract, per TiB; up to 2 PiB per system via EBS + S3 tiering (single node or HA); doesn't cover on-premises backup.

### Tags on EBS volumes in AWS

Tags added at creation time (previously added after deployment) — helps with SCP-based permission management.

### Minimum cooling period for auto tiering policy

Adjustable via API for volumes using auto tiering policy.

### Enhancement to custom export policies

Displayed in ascending order for new NFS volumes.

### Deletion of old cloud snapshots

Auto-deletes older root/boot disk cloud snapshots (created at deploy and each power-down); retains only two most recent per volume. Requires new Azure Connector permission: Microsoft.Compute/snapshots/delete.

## 24 May 2021

### Cloud Volumes ONTAP 9.9.1

## 11 Apr 2021

Connector 3.9.5.

### Logical space reporting

Enabled on initial storage VM.

### Support for gp3 disks in AWS

General Purpose SSD (gp3), starting 9.7 release; lowest-cost SSD balancing cost/performance.

### Cold HDD disks no longer supported in AWS

sc1 no longer supported.

### TLS 1.2 for Azure storage accounts

Storage accounts created by BlueXP now use TLS 1.2.

## 08 Mar 2021

Connector 3.9.4.

### Cloud Volumes ONTAP 9.9.0

### Support for the AWS C2S environment

Deploy 9.8 in AWS Commercial Cloud Services (C2S).

### AWS encryption with customer-managed CMKs

Starting 9.9.0: EBS data and tiered S3 data both encrypted with customer-managed CMK (previously EBS only). Requires CVO IAM role access to the CMK.

### Support for Azure DoD

Deploy 9.8 in Azure DoD Impact Level 6 (IL6).

### IP address reduction in Google Cloud

Fewer IPs required for 9.8+ (unified intercluster LIF with node management LIF); option to skip SVM management LIF creation via API for further reduction.

### Shared VPC support in Google Cloud

VPC-1/2/3 can now be shared VPCs (previously only VPC-0); supported 9.8+.

## 04 January 2021

(Entry title/content beyond this point was not captured in the fetched excerpt — the source page's changelog appears to continue further back; refer to the live page for entries prior to 04 January 2021.)
