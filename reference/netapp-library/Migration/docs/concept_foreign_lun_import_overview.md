# Foreign LUN Import overview
Source: https://docs.netapp.com/us-en/ontap-fli/san-migration/concept_foreign_lun_import_overview.html
Fetched: 2026-07-07

Foreign LUN Import (FLI) is a feature built into ONTAP that allows users to import data from foreign array LUNs to NetApp LUNs in a simple and efficient manner.

All FLI migrations operate at the LUN level. FLI is a strictly block-based tool; file, record, NFS, and CIFS-based migrations are not supported. For a discussion of other migration methodologies for file-level protocols, such as NFS and CIFS/SMB, review the Data Migration Tools Quick Reference (https://library.netapp.com/ecm/ecm_get_file/ECMP12363719).

Although ONTAP no longer requires a professional-services-run migration, NetApp does strongly recommend professional services involvement in scoping, planning, and training for all but the simplest migrations.

FLI was developed to migrate SAN LUNs to ONTAP. FLI supports a range of migration requirements, including, but not limited to, the following:

- Migrating data between heterogeneous storage arrays from EMC, Hitachi, HP, and other vendors to NetApp.
- Simplifying and accelerating block data migrations during data center relocation, consolidation, and array replacements.
- Consolidating migration and LUN realignments into a single workflow.

In addition, the 7-Mode to ONTAP transition procedure is able to convert from 32-bit to 64-bit aggregates, fix alignment problems, and migrate LUNs as a single operation.

FLI enables the NetApp storage to discover the LUNs to be imported for data migration. The foreign LUNs are shown as disks on the NetApp storage and have no ownership assigned to them automatically so that the user data is not overwritten by mistake. The disks that contain foreign array LUNs must be marked as foreign. The rules for configuring foreign array LUNs must be strictly adhered to in order to use FLI for NetApp storage. See "LUN requirements and limitations" (https://docs.netapp.com/us-en/ontap-fli/san-migration/concept_lun_requirements_and_limitations.html).

FLI requires at least one physical FC port on each controller and to have LUNs migrate directly in Initiator mode. Two ports, one to each fabric, are preferred, but a single port can be used. These ports are used to connect to the source array and need to be zoned and masked in order to be able to see and mount the source LUNs. If you need to change a port from target to initiator, see Configure FC adapters (https://docs.netapp.com/us-en/ontap/san-admin/configure-fc-adapters-task.html).

FLI migrations can be performed either offline, which disrupts operations for the duration of the import, or online, which is mainly non-disruptive.

- Offline data migration: the host is taken offline for the migration. The NetApp array copies the data directly from the third-party array.
- Online data migration: the host is connected to the NetApp controller where the new LUN is now hosted. Host operation can then resume and continue during the import.

(Diagrams referenced in source: foreign_lun_import_overview_1.png [offline], foreign_lun_import_overview_2.png [online] — not reproduced here.)
