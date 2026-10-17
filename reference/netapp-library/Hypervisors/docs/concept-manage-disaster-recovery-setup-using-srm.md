# Configure disaster recovery setup
Source: https://docs.netapp.com/us-en/ontap-tools-vmware-vsphere/concepts/concept_manage_disaster_recovery_setup_using_srm.html
Fetched: 2026-07-07

You can create and manage the disaster recovery setup in your vCenter Server along with VMware's Site Recovery Manager (SRM).

VASA Provider now comes built-in with the capabilities of Storage Replication Adapter (SRA). If you have configured vVols datastores in your datacenter, you do not need to install SRA separately for recovery of vVols datastores. In Site Recovery Manager (SRM), you must pair the protected and recovery sites. After site pairing, the next part of SRM configuration is setting up an array pair, which enables SRM to communicate with the storage system to discover devices and device replication. You must create a site pair in SRM before configuring the array pair.

This release of ONTAP tools provides an option to use synchronous SnapMirror configuration for disaster recovery.

> **Note:** VMware Site Recovery Manager (SRM) does not use SRA for managing disaster recovery of vVols datastores. Instead, the VASA Provider handles replication and failover control of vVols datastores on ONTAP 9.7 and later clusters.

See the "Enable Storage Replication Adapter" section for that procedure.

## Enabling quick_resync

You can enable the `quick_resync` flag to perform Reprotect and Restore operations in SRA. This applies only to datastores backed by volumes with an asynchronous SnapMirror relationship. The `quick_resync` flag enables faster resync of the destination volume because resync doesn't incur storage-efficiency overhead before transferring new data. It is not enabled by default.

**Recommended to enable `quick_resync` when:**
- The resync source does not have volume efficiency enabled.
- Reducing resync time is more important than preserving all possible storage efficiency on the network.

**Steps to enable `quick_resync`:**
1. Log into the control panel at `https://<IP address>:9083` and click the Web-based CLI interface.
2. Run: `vp updateconfig -key=snapmirror.quick.resync.enabled -value=true`
3. Run: `vp reloadconfig`

*(Product: ONTAP tools for VMware vSphere 9.13)*
