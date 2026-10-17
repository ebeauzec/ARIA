# Using Foreign LUN Import to import LUNs into AFF
Source: https://docs.netapp.com/us-en/ontap-fli/san-migration/concept_using_fli_to_import_luns_into_all_flash.html
Fetched: 2026-07-07

Beginning with ONTAP 9.1, AFF supports FLI. You can use FLI to import LUNs from other arrays directly into ONTAP clusters.

Beginning with ONTAP 8.3.2, AFF can support FLI with an approved Process Variance Request (PVR). Contact your NetApp account team to get the PVR submitted for approval. On approval, the submitter, usually a NetApp System Engineer, will receive an approval letter with instructions for enabling FLI functionality.

For versions of ONTAP software previous to 8.3.2, you will need to stage FLI imports to a non-AFF HA pair on the same cluster with the AFF. After the migration has been completed, you can then use non-disruptive operations (NDO) such as vol or LUN move to move the migrated LUNs to AFF. If your AFF cluster doesn't have any non-AFF nodes, talk to your account team about the possibility of borrowing swing gear to facilitate this.
