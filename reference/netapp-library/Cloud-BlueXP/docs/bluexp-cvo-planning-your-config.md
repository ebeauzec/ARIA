# Plan your Cloud Volumes ONTAP configuration in AWS
Source: https://docs.netapp.com/us-en/bluexp-cloud-volumes-ontap/task-planning-your-config.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-planning-your-config.html

Last updated: 01/09/2026

When you deploy Cloud Volumes ONTAP in AWS, you can choose a preconfigured system that matches your workload requirements, or you can create your own configuration. If you choose your own configuration, you should understand the options available to you.

## Choose a Cloud Volumes ONTAP license

Several licensing options are available for Cloud Volumes ONTAP. Each option enables you to choose a consumption model that meets your needs.

- [Learn about licensing options for Cloud Volumes ONTAP](https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/concept-licensing.html)
- [Learn how to set up licensing](https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-set-up-licensing-aws.html)

## Choose a supported region

Cloud Volumes ONTAP is supported in most AWS regions. View the full list of supported regions (https://bluexp.netapp.com/cloud-volumes-global-regions). Newer AWS regions must be enabled before you can create and manage resources in those regions.

### Choose a supported Local Zone

Selecting a Local Zone is optional. Cloud Volumes ONTAP is supported in some AWS Local Zones including Singapore. Cloud Volumes ONTAP in AWS supports only high availability (HA) mode in a single availability zone. Single node deployments are not supported.

> Note: Cloud Volumes ONTAP does not have support for data tiering and cloud tiering in AWS Local Zones. Additionally, Local Zones with instances that have not been qualified for Cloud Volumes ONTAP are not supported. An example of this is Miami, that is not available as a Local Zone, because it has only Gen6 instances that are unsupported and unqualified.

Local Zones must be enabled before you can create and manage resources in those zones.

## Choose a supported instance

Cloud Volumes ONTAP supports several instance types, depending on the license type that you choose. See [Supported configurations for Cloud Volumes ONTAP in AWS](https://docs.netapp.com/us-en/cloud-volumes-ontap-relnotes/reference-configs-aws.html).

## Understand storage limits

The raw capacity limit for a Cloud Volumes ONTAP system is tied to the license. Additional limits impact the size of aggregates and volumes. See [Storage limits for Cloud Volumes ONTAP in AWS](https://docs.netapp.com/us-en/cloud-volumes-ontap-relnotes/reference-limits-aws.html).

## Size your system in AWS

Key points when choosing an instance type, disk type, and disk size:

**Instance type**
- Match your workload requirements to the maximum throughput and IOPS for each EC2 instance type.
- If several users write to the system at the same time, choose an instance type that has enough CPUs to manage the requests.
- If you have an application that is mostly reads, then choose a system with enough RAM.

**EBS disk type**
- *General Purpose SSD (gp3)* — lowest-cost SSDs balancing cost and performance for a broad range of workloads; performance defined by IOPS and throughput. Supported with Cloud Volumes ONTAP 9.7 and later. The NetApp Console fills in default IOPS/throughput values equivalent to gp2 based on disk size; you can increase but not lower these values (lowering results in inferior performance). Supports the Amazon EBS Elastic Volumes feature.
- *General Purpose SSD (gp2)* — balances cost and performance; performance defined by IOPS.
- *Provisioned IOPS SSD (io1)* — for critical applications requiring highest performance at a higher cost; supports Elastic Volumes.
- *Throughput Optimized HDD (st1)* — for frequently accessed workloads requiring fast, consistent throughput at a lower price.

> Note: Data tiering to Amazon S3 is not supported if your Cloud Volumes ONTAP system is in an AWS Local Zone, because accessing S3 buckets outside the Local Zone involves higher latency.

**EBS disk size**
If your configuration doesn't support Elastic Volumes, you must choose an initial disk size at launch. Key considerations:
- All disks in an aggregate must be the same size.
- EBS disk performance is tied to disk size (baseline IOPS/burst duration for SSD; baseline/burst throughput for HDD).
- Choose the disk size that gives you the sustained performance you need.
- Even with larger disks, you might not get all IOPS because the EC2 instance can reach its bandwidth limit.

## View default system disks

In addition to storage for user data, the Console also purchases cloud storage for Cloud Volumes ONTAP system data (boot, root, core, and NVRAM data). See [default disks for Cloud Volumes ONTAP system data in AWS](https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/reference-default-configs.html#aws). The Console agent also requires a system disk.

## Prepare to deploy Cloud Volumes ONTAP in an AWS Outpost

Deploy Cloud Volumes ONTAP in an AWS Outpost by selecting the Outpost VPC during deployment (requires a Console agent already deployed in the Outpost). Limitations:

- Only single node Cloud Volumes ONTAP systems are supported at this time
- EC2 instances are limited to what's available in your Outpost
- Only General Purpose SSDs (gp2) are supported at this time

## Collect networking information

**Single node or HA pair in a single AZ**: Region, VPC, Subnet, Security group (if using your own).

**HA pair in multiple AZs**: Region, VPC, Security group (if using your own), Node 1 AZ/subnet, Node 2 AZ/subnet, Mediator AZ/subnet, Key pair for mediator, Floating IP for cluster management port, Floating IP for data on node 1/node 2, Route tables for floating IP addresses.

## Choose a write speed

The Console enables you to choose a write speed setting (normal or high). Understand the risks/recommendations for high write speed before choosing. See [write speed concept](https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/concept-write-speed.html).

## Choose a volume usage profile

ONTAP storage efficiency features that can be enabled or disabled per volume profile:

- **Thin provisioning** — presents more logical storage than physically available; space allocated dynamically as data is written.
- **Deduplication** — locates identical data blocks and replaces them with references to a single shared block, reducing capacity requirements within a volume.
- **Compression** — reduces physical capacity required by compressing data within a volume on primary, secondary, and archive storage.
