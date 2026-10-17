# Prepare storage systems for SnapMirror and SnapVault replication for MySQL
Source: https://docs.netapp.com/us-en/snapcenter-60/protect-mysql/prepare-storage-systems-for-snapmirror-and-snapvault-replication-for-plugin-for-mysql.html
Fetched: 2026-07-07

You can use a SnapCenter plug-in with ONTAP SnapMirror technology to create mirror copies of backup sets on another volume, and with ONTAP SnapVault technology to perform disk-to-disk backup replication for standards compliance and other governance-related purposes. Before you perform these tasks, you must configure a data-protection relationship between the source and destination volumes and initialize the relationship.

SnapCenter performs the updates to SnapMirror and SnapVault after it completes the Snapshot operation. SnapMirror and SnapVault updates are performed as part of the SnapCenter job; do not create a separate ONTAP schedule.

Note: If you are coming to SnapCenter from a NetApp SnapManager product and are satisfied with the data protection relationships you have configured, you can skip this section.

A data protection relationship replicates data on primary storage (the source volume) to secondary storage (the destination volume). When you initialize the relationship, ONTAP transfers the data blocks referenced on the source volume to the destination volume.

Note: SnapCenter does not support cascade relationships between SnapMirror and SnapVault volumes (Primary > Mirror > Vault). You should use fanout relationships.

SnapCenter supports the management of version-flexible SnapMirror relationships. For details about version-flexible SnapMirror relationships and how to set them up, see the ONTAP documentation.

(Note: this is the SnapCenter 6.0 version of the page; a newer release 6.2 is available at the equivalent protect-mysql path under /us-en/snapcenter/.)
