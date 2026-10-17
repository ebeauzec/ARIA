# Set up disaster recovery for VMFS datastores using BlueXP disaster recovery
Source: https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-disaster-recovery-vmfs.html
Fetched: 2026-07-07

This use case outlines the procedure to set up disaster recovery using BlueXP disaster recovery for on-premises VMware VMs using VMware Virtual Machine File System (VMFS) datastores. Includes setting up the BlueXP account and connector, establishing SnapMirror replication between ONTAP systems, integrating with VMware vCenter, and automating failover and failback operations.

Disaster recovery using block-level replication from production site to disaster recovery site is a resilient and cost-effective way of protecting workloads against site outages and data corruption events (e.g., ransomware attacks). With NetApp SnapMirror replication, VMware workloads running on-premises ONTAP systems using VMFS datastore can be replicated to another ONTAP storage system in a designated recovery datacenter where VMware resides.

## Introduction

This document describes configuring BlueXP DRaaS to set up disaster recovery for on-premises VMware VMs to another designated site: setting up the BlueXP account, BlueXP connector, adding ONTAP arrays within the BlueXP workspace to enable communication from VMware vCenter to ONTAP storage, configuring replication between sites, setting up/testing a recovery plan, and performing full site failover/failback.

Using the BlueXP disaster recovery service (integrated into the NetApp BlueXP console), customers can discover on-premises VMware vCenters along with ONTAP storage, create resource groupings, create a disaster recovery plan, associate it with resource groups, and test or execute failover/failback. SnapMirror provides storage-level block replication with an RPO of up to 5 minutes. DR drills can be simulated without impacting production/replicated datastores or incurring additional storage costs, using ONTAP's FlexClone technology to create a space-efficient copy of the VMFS datastore from the last replicated snapshot on the DR site. When actual failover is needed, the service orchestrates bringing up protected VMs on the DR site and reverses the SnapMirror relationship for failback.

## Getting started

1. Log in to BlueXP.
2. From the BlueXP left navigation, select **Protection > Disaster recovery**.
3. The BlueXP disaster recovery Dashboard appears.

**Prerequisites** before configuring a disaster recovery plan:

- BlueXP Connector is set up in NetApp BlueXP, deployed in an AWS VPC.
- BlueXP connector instance has connectivity to the source and destination vCenter and storage systems.
- On-premises NetApp storage systems hosting VMFS datastores for VMware are added in BlueXP.
- DNS resolution should be in place when using DNS names; otherwise use IP addresses for the vCenter.
- SnapMirror replication is configured for the designated VMFS-based datastore volumes.

Configuration typically takes 3 to 5 minutes once connectivity is established.

> Note: NetApp recommends deploying the BlueXP connector in the disaster recovery site or a third site, so it can communicate with source and destination resources during real outages or natural disasters.

> Note: Support for on-premises to on-premises VMFS datastores was in technology preview at the time of writing. Supported with both FC and iSCSI protocol-based VMFS datastores.

## BlueXP disaster recovery configuration

Discover and add the on-premises vCenter and storage resources to BlueXP disaster recovery. Ensure ONTAP storage systems are added to the working environment within the canvas. Open BlueXP console, select **Protection > Disaster Recovery**, select **Discover vCenter servers** or use the top menu **Sites > Add > Add vCenter**.

Add the following platforms:
- **Source**: On-premises vCenter.
- **Destination**: VMC SDDC vCenter.

Once vCenters are added, automated discovery is triggered.

## Configuring storage replication between source and destination site

SnapMirror uses ONTAP snapshots to manage data transfer. Initially, a full copy based on a source-volume snapshot is copied to the destination (baseline synchronization). As data changes, a new snapshot is created and compared to the baseline; changed blocks are replicated to the destination, and the newer snapshot becomes the new baseline — enabling incremental updates.

Once a SnapMirror relationship is established, the destination volume is online read-only (still accessible) and is an identical physical-block-level replica of the source, including snapshots, volume settings, and any ONTAP compression/deduplication.

Breaking the SnapMirror relationship makes the destination volume writable (used to perform failover). SnapMirror can efficiently resynchronize changed data from the failover site back to the primary system once it comes back online, and re-establish the original relationship.

**How to set it up for VMware Disaster Recovery**

Creating SnapMirror replication is the same process for any application (manual or automated). BlueXP lets you drag & drop the source ONTAP system onto the destination to trigger a wizard. BlueXP DRaaS can automate this if:
- Source and destination clusters have a peer relationship.
- Source SVM and destination SVM have a peer relationship.

> Note: If a SnapMirror relationship is already configured via CLI, BlueXP DRaaS picks it up and continues the workflow.
> Note: SnapMirror replication can also be created via ONTAP CLI or System Manager — BlueXP DRaaS orchestrates the workflow regardless.

## What can BlueXP disaster recovery do for you?

After source and destination sites are added, BlueXP disaster recovery performs automatic deep discovery, displaying VMs and associated metadata, and detects networks/port groups used by VMs.

VMs can be grouped into resource groups (logical groups containing boot orders and boot delays executed upon recovery). Navigate to **Resource Groups** and click **Create New Resource Group** (or create one while creating a replication plan). Boot order can be defined/modified via drag and drop.

## Creating a replication plan

Navigate to the **Replication Plan** tab and click **Add Plan**:

1. Select the source vCenter, then the destination vCenter.
2. Select existing resource groups, or let the wizard group VMs based on recovery objectives (defines the operation sequence for restoring application VMs). Each VM within a resource group starts in sequence based on order; two resource groups start in parallel. You can filter VMs/datastores if resource groups aren't pre-created.
3. Create failover mappings: how source resources map to the destination — compute resources, virtual networks, IP customization, pre-/post-scripts, boot delays, application consistency, etc. (See "Create a replication plan" for details.) By default the same mapping parameters apply to test and failover; uncheck to apply different mappings for test ("Test mapping" option).
4. Select the recurrence type: **Migrate** (one-time migration using failover) or recurring continuous replication (**Replicate**).
5. Review the created mappings and click **Add plan**.

Once created, BlueXP disaster recovery executes the replication process according to the plan every 30 minutes. During failover/test-failover, you can use the most recent SnapMirror snapshot or select a specific point-in-time snapshot (useful for ransomware recovery scenarios where the most recent replicas are compromised). Trigger via **Failover** or **Test failover**.

## What happens during a failover or test failover operation?

**Test failover**: BlueXP disaster recovery creates a FlexClone volume on the destination ONTAP system from the latest (or selected) snapshot. The original target volume is not mapped; instead a new FlexClone volume and a temporary datastore backed by it are mapped to the ESXi hosts. This does not affect SnapMirror replication. Cleanup ("Clean Up failover test") destroys the FlexClone volume afterward.

**Real failover**: BlueXP disaster recovery:
1. Breaks the SnapMirror relationship between the sites.
2. Mounts the VMFS datastore volume after resignature for immediate use.
3. Registers the VMs.
4. Powers on VMs.

Once the primary site is back up, BlueXP disaster recovery enables reverse resync for SnapMirror and enables failback with a click of a button.

If **Migrate** is chosen (a planned failover event), an additional step shuts down VMs at the source site first; the rest is the same as a failover event.

You can monitor replication health status for datastore volumes from BlueXP or the ONTAP CLI, and track failover/test-failover status via Job Monitoring.
