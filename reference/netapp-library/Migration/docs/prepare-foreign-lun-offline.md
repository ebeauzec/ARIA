# Prepare foreign storage array LUNs for an ONTAP FLI offline migration
Source: https://docs.netapp.com/us-en/ontap-fli/san-migration/prepare-foreign-lun-offline.html
Fetched: 2026-07-07

In a Foreign LUN Import (FLI) offline migration, you must take manual steps from your foreign storage array to present the foreign source LUN to your ONTAP storage system; then you must take steps from your ONTAP storage system to discover the foreign LUN.

## Step 1: Present foreign array source LUNs to ONTAP storage

Before you can begin importing data from a foreign storage array LUN using an FLI offline migration, you must present the source LUNs on your foreign storage array to your ONTAP storage system.

Steps:

1. Log in to the source array.
2. Add the NetApp initiators to the host group created during the plan phase.
3. Select the host LUNs that need to be migrated from available logical LUNs. Use LUN names for each host mentioned in the source LUNs section of your Site Survey and Planning worksheet (https://docs.netapp.com/us-en/ontap-fli/san-migration/reference_site_survey_and_planning_worksheet_source_luns_tab.html).

## Step 2: Discover foreign array source LUNs in ONTAP

After you have presented your foreign array source LUNs to your ONTAP storage system, the LUNs must be discovered in ONTAP before you can create the LUN import relationship.

Steps:

1. Verify the source LUNs and mapping from the source storage to the destination storage.
2. Log in to the ONTAP storage system through SSH using admin user.
3. Change the mode to advanced:

```cli
set -privilege advanced
```

4. Enter `y` when asked if you want to continue.
5. Discover the source array on ONTAP. Wait for a few minutes and retry to detect the source array.

```cli
storage array show
```

   Example output showing discovery of a Hitachi DF600F array:

```
DataMig-ontap::*> storage array show
Prefix                         Name   Vendor            Model Options
-------- ---------------------------- -------- ---------------- ----------
HIT-1                HITACHI_DF600F_1  HITACHI           DF600F
```

   Note: When the storage array is discovered for the first time, ONTAP might not show the array by discovering automatically. Reset the switch port where ONTAP initiator ports are connected in that case.

6. Verify the source array is discovered through all the initiator ports:

```cli
storage array config show -array-name <array_name>
```

   Example output showing the Hitachi DF600F array discovered through all the initiator ports:

```
DataMig-ontap::*> storage array config show -array-name HITACHI_DF600F_1
             LUN   LUN
Node         Group Count     Array Name       Array Target Port Initiator
------------ ----- ----- ---------------------------- -----------------------
DataMig-ontap-01 0     1    HITACHI_DF600F_1     50060e801046b960        0a
                                                 50060e801046b964        0b
                                                 50060e801046b968        0a
                                                 50060e801046b96c        0b
DataMig-ontap-02 0     1    HITACHI_DF600F_1     50060e801046b960        0a
                                                 50060e801046b964        0b
                                                 50060e801046b968        0a
                                                 50060e801046b96c        0b
```

## What's next?

Create the LUN import relationship: https://docs.netapp.com/us-en/ontap-fli/san-migration/create-lun-import-relationship-offline.html
