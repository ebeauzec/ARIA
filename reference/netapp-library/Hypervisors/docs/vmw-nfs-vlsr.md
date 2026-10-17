# Configure disaster recovery for NFS datastores using VMware Site Recovery Manager
Source: https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-nfs-vlsr.html
Fetched: 2026-07-07

Implement disaster recovery for NFS datastores using VMware Site Recovery Manager (SRM) and ONTAP tools for VMware vSphere 10. This procedure covers configuring SRM with vCenter servers at primary/secondary sites, installing the ONTAP Storage Replication Adapter (SRA), establishing SnapMirror relationships between ONTAP storage systems, and setting up SRM site recovery.

ONTAP tools 10 with SRA and VMware SRM deliver robust storage capabilities including native HA/scalability for the VASA Provider, supporting iSCSI and NFS vVols, simplifying management of multiple vCenter servers and ONTAP clusters, and enabling seamless VM/data replication and failover between sites.

The SRA works with SRM to manage replication of VM data between production and DR sites for traditional VMFS/NFS datastores, and supports nondisruptive testing of DR replicas, automating discovery, recovery, and reprotection tasks.

## Scenario overview

High-level steps:
1. Configure SRM with vCenter servers at primary and secondary sites.
2. Install the SRA adapter for ONTAP tools 10 and register with vCenters.
3. Create SnapMirror relationships between source and destination ONTAP storage systems.
4. Configure Site Recovery for SRM.
5. Conduct test and final failover.
6. Reprotection and failback.

## Architecture

Typical VMware Site Recovery architecture uses ONTAP tools for VMware vSphere 10 configured in a 3-node high-availability configuration.

## Prerequisites

- vSphere 8 clusters at both primary and secondary locations with suitable inter-environment networking.
- ONTAP storage systems at both locations, with physical data ports on Ethernet switches dedicated to NFS storage traffic.
- ONTAP tools for VMware vSphere 10 installed, with both vCenter servers registered.
- VMware Site Replication Manager appliances installed at primary and secondary sites, with inventory mappings (network, folder, resource, storage policy) configured for SRM.

NetApp recommends redundant network designs for NFS providing fault tolerance for storage systems, switches, network adapters, and hosts. NFS can be deployed with a single subnet or multiple subnets depending on architectural requirements. See VMware's "Best Practices For Running NFS with VMware vSphere" and the NetApp "Network configuration - NFS" section of the enterprise applications docs.

## Deployment steps

### Create SnapMirror relationship between ONTAP storage systems

A SnapMirror relationship must exist between source and destination ONTAP systems for datastore volumes to be protected. See ONTAP SnapMirror replication workflow documentation for cluster peer, SVM peer, and per-volume SnapMirror relationship setup (via System Manager or CLI).

### Configure the SRM appliance

**Connect the SRM appliance for primary and secondary sites** (complete for both sites):
1. Browse to `https://<SRM_appliance_IP>:5480`, log in, click **Configure Appliance**.
2. On the Platform Services Controller page, enter the vCenter server credentials to register SRM against. Click Next.
3. On the vCenter Server page, verify the connected vCenter and click Next.
4. On the Name and extension page, provide an SRM site name, admin email, and local host used by SRM. Click Next.
5. Review and complete on the Ready to complete page.

**Configure SRA on the SRM appliance:**
1. Download the SRA for ONTAP tools 10 from the NetApp Support Site (otv10 downloads).
2. In the SRM management appliance, click **Storage Replication Adapters** > **New Adapter**.
3. Follow the steps in "Configure SRA on the SRM appliance" (ONTAP tools 10 docs). Once complete, SRA can communicate using the provided vCenter IP address and credentials.

### Configure Site Recovery for SRM

**Configure Site Pairing** (in the vSphere client of the primary site):
1. Click **Site Recovery** in the left menu (opens SRM management UI for the primary site).
2. Click **NEW SITE PAIR**.
3. On Pair type, verify the local vCenter server and select the pair type. Click Next.
4. On Peer vCenter, enter secondary-site vCenter credentials, click **Find vCenter Instances**, verify discovery, click Next.
5. On Services, check the proposed site pairing box, click Next.
6. Review and click **Finish** to create the Site Pairing.

**Add an Array Pair** (Site Recovery interface, primary site):
1. Navigate to **Configure > Array Based Replication > Array Pairs**, click **ADD**.
2. On Storage replication adapter, verify the SRA adapter for the primary site, click Next.
3. On Local array manager, enter a name, the storage system FQDN, the SVM IP addresses serving NFS, and optionally specific volume names to discover. Click Next.
4. On Remote array manager, repeat for the secondary-site ONTAP system.
5. On Array pairs, select array pairs to enable, click Next.
6. Review and click **Finish**.

**Configure Protection Groups** (Site Recovery interface, primary site):
1. Click **Protection Groups** tab > **New Protection Group**.
2. Name and direction: name the group, choose protection direction.
3. Type: select protection group type (datastore, VM, or vVol) and the array pair. Click Next.
4. Datastore groups: select datastores to include (VMs on each datastore are shown). Click Next.
5. Recovery plan: optionally add to an existing recovery plan, or select "Do not add to recovery plan." Click Next.
6. Review and click **Finish**.

**Configure Recovery Plan** (Site Recovery interface, primary site):
1. Click **Recovery plan** tab > **New Recovery Plan**.
2. Name and direction: name the plan, choose source/destination direction. Click Next.
3. Protection groups: select previously created protection groups. Click Next.
4. Test Networks: configure networks used during plan testing (an isolated test network is auto-created if none selected). Click Next.
5. Review and click **Finish**.

## Disaster recovery operations with SRM

See "Operational best practices" (docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-srm-operational_best_practices.html) for more on ONTAP + SRM DR operations.

**Testing failover:**
1. In Site Recovery, select a recovery plan, click **Test**.
2. Monitor progress in the Site Recovery and vCenter task panes.
3. SRM sends commands via SRA to the secondary ONTAP system — a FlexClone of the most recent snapshot is created and mounted at the secondary vSphere cluster (visible in storage inventory).
4. After the test completes, click **Cleanup** to unmount the datastore and revert to the original environment.

**Running the recovery plan (full failover):**
1. Select a recovery plan, click **Run**.
2. After failover, the datastore is mounted and VMs are registered at the secondary site.

**Reprotection:** After recovery, the former recovery site becomes the new production site, but SnapMirror replication is disrupted during recovery, leaving the new production site unprotected. Establish new protection by replicating to another site. If the original production site is still functional, it can be repurposed as the new recovery site (reversing protection direction). Reprotection is only feasible for non-catastrophic failures — the original vCenter Servers, ESXi servers, SRM servers, and databases must be eventually recoverable. Otherwise, a new protection group and recovery plan are required.

**Failback:** A reverse failover returning operations to the original site. Ensure the original site has regained functionality first. Recommended: run a test failover after reprotection and before the final failback, to verify the original site can handle the workload before committing.

## Additional information

- "VMware Site Recovery Manager with ONTAP" — docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-srm-overview.html
- ONTAP 9 Documentation center
- VMware Cloud Foundation Documentation (Broadcom techdocs)

*Page last updated: 07/30/2025*
