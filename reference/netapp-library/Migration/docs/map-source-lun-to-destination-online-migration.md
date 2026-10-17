# Map the source LUN to the ONTAP array for an FLI online migration
Source: https://docs.netapp.com/us-en/ontap-fli/san-migration/map-source-lun-to-destination-online-migration.html
Fetched: 2026-07-07

To import data from a foreign array LUN, the LUN must first be unmapped on the foreign array and remapped to your ONTAP storage system. The commands to unmap a LUN on a foreign array vary based upon the array vendor. Follow the steps provided for the overall process and see the documentation for your foreign array for specific commands.

## DISRUPTION NOTE

Disruption begins immediately after the unmap command is executed against the foreign array. Disruption window is generally measured in minutes (time to repoint the host at the new NetApp target and rescan for LUNs).

## Before you begin

Removing the host (initiator) from an igroup affects all LUNs that are mapped to the igroup. To prevent disruption to other LUNs on your foreign array, the LUN you are migrating must be the only LUN mapped to its igroup. If there are other LUNs sharing the igroup, remap them to a different igroup, or create a new igroup specifically for the LUN to be migrated. See the vendor documentation for the appropriate commands.

## Steps

1. On the foreign array, display the storage group to which the source LUN is mapped. (See vendor documentation for the appropriate commands.)
2. If the LUNs being imported are for an ESXi host, review and follow the instructions for ESXi CAW/ATS remediation.
3. Unmap the source LUN from the hosts.

   Note: The disruption begins immediately after the unmap command is executed. Generally, the disruption window can be measured in minutes — the time to repoint the host at the new NetApp target and scan for LUNs.

4. Verify that the host initiators are no longer present.
5. On the ONTAP cluster, bring the destination LUN online, and verify that it is mapped:

```cli
lun online -vserver <SVM_name> -path <volume_path|storage_unit_path>
```

6. Verify that the LUN is online:

```cli
lun show -vserver <SVM_name>
```

7. Rescan the disks on the host, find the LUN on the ONTAP target, and then verify that the DSM has claimed the LUN.

   Note: The disruption window ends here.

8. Verify that you can see all expected paths, and check your event logs to verify that no errors exist.

## Result

The disruptive part of this migration is complete, unless there are outstanding host remediation tasks (identified during your analysis and planning phases) that are disruptive.

The LUNs are online and mapped, and the hosts are now mounting the new ONTAP-hosted LUN. Reads are passed through the ONTAP array to the source LUN, and writes are written to both the new ONTAP-hosted LUN and the original source LUN. The source LUN and destination LUN will stay synchronized until the migration is complete and the LUN relationship has been broken.
