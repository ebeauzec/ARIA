# Move an ONTAP volume
Source: https://docs.netapp.com/us-en/ontap-sm-classic/online-help-96-97/task_moving_flexvol_volumes_between_aggregates_or_nodes.html
Fetched: 2026-07-07

Note: This URL redirects to the current ONTAP docs page (`https://docs.netapp.com/us-en/ontap/volumes/move-volume-task.html`); the classic System Manager 9.6/9.7 help page has been retired/merged into current documentation.

You can move a FlexVol volume to a different aggregate, node, or both within the same storage virtual machine (SVM) to balance storage capacity after determining that there is a storage capacity imbalance.

## About this task

By default, if the cutover operation fails to complete within 30 seconds, it will retry. You can adjust the default behavior by using the `-cutover-window` and `-cutover-action` parameters, both of which require advanced privilege level access.

You must be a cluster administrator to perform this task.

## Before you begin

- If you are moving a volume that uses 8K adaptive compression to one of the following platforms, you should increase the size of the volume's active file system before moving the volume. Data is compressed differently on these platforms so that space is saved at the aggregate level instead of the volume level. Because of this difference, the size of the volume's active file system should be increased by the amount of 8k compression savings to prevent the volume from running out of space during the volume move.
  - AFF and FAS platforms that support dedicated offload processor storage efficiency
  - AFF C-Series platforms (see Hardware Universe for a full list of C-series platforms)
- If you are moving a data protection mirror and you have not initialized the mirror relationship, use the `snapmirror initialize` command to initialize the mirror relationship. Data protection mirror relationships must be initialized before you can move one of the volumes.

## Steps

1. Determine an aggregate to which you can move the volume:

```cli
volume move target-aggr show
```

   The aggregate that you select must have enough space for the volume; that is, the available size is bigger than the volume that you are moving.

   Example output:

```
cluster1::> volume move target-aggr show -vserver vs2 -volume user_max
Aggregate Name   Available Size   Storage Type
--------------   --------------   ------------
aggr2            467.9GB          hdd
node12a_aggr3    10.34GB          hdd
node12a_aggr2    10.36GB          hdd
node12a_aggr1    10.36GB          hdd
node12a_aggr4    10.36GB          hdd
5 entries were displayed.
```

2. Perform a validation check to verify that the volume can be moved to the intended aggregate:

```cli
volume move start -perform-validation-only
```

3. Move the volume:

```cli
volume move start
```

   Example: moves the `user_max` volume on the `vs2` SVM to the `node12a_aggr3` aggregate. The move runs as a background process.

```
cluster1::> volume move start -vserver vs2 -volume user_max
-destination-aggregate node12a_aggr3
```

4. Determine the status of the volume move operation:

```cli
volume move show
```

   Example output showing a move that completed the replication phase and is in the cutover phase:

```
cluster1::> volume move show
Vserver   Volume     State    Move Phase  Percent-Complete Time-To-Complete
--------- ---------- -------- ----------  ---------------- ----------------
vs2       user_max   healthy  cutover     -                -
```

   The volume move is complete when it no longer appears in the `volume move show` command output.

5. Optionally, view compression savings:

```cli
volume show-footprint -vserver <SVM> -volume <volume_name>
```

   Note: Additional aggregate-level savings might be realized through a post-process conversion scan that runs automatically and shortly after the volume move is completed.

## Related information

- Considerations and recommendations when moving volumes: https://docs.netapp.com/us-en/ontap/volumes/recommendations-moving-concept.html
