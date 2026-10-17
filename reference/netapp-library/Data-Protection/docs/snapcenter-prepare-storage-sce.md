# Prepare storage systems for SnapMirror and SnapVault replication
Source: https://docs.netapp.com/us-en/snapcenter/protect-sce/reference_prepare_storage_system_for_snapmirror_and_snapvault.html
Fetched: 2026-07-07

You can use a SnapCenter plug-in with ONTAP SnapMirror technology to create mirror copies of backup sets on another volume, and with ONTAP SnapVault technology to perform disk-to-disk backup replication for standards compliance and other governance-related purposes. Before you perform these tasks, you must configure a data-protection relationship between the source and destination volumes and initialize the relationship.

SnapCenter performs the updates to SnapMirror and SnapVault after it completes the Snapshot operation. SnapMirror and SnapVault updates are performed as part of the SnapCenter job. If you are using SnapMirror active sync, then go with default SnapMirror or SnapVault schedules for both SnapMirror active sync and asynchronous relationships.

Note: If you are coming to SnapCenter from a NetApp SnapManager product and are satisfied with the data protection relationships you have configured, you can skip this section.

A data protection relationship replicates data on primary storage (the source volume) to secondary storage (the destination volume). When you initialize the relationship, ONTAP transfers the data blocks referenced on the source volume to the destination volume.

Note: SnapCenter does not support cascade relationships between SnapMirror and SnapVault volumes (Primary > Mirror > Vault). You should use fanout relationships.

SnapCenter supports the management of version-flexible SnapMirror relationships. For details about version-flexible SnapMirror relationships and how to set them up, see the ONTAP documentation.
