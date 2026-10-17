# Set a throughput ceiling with ONTAP QoS policy groups
Source: https://docs.netapp.com/us-en/ontap/performance-admin/set-throughput-ceiling-qos-task.html
Fetched: 2026-07-07

A QoS maximum or throughput ceiling guarantees that throughput for a workload does not exceed a maximum number of IOPS or MBps, or IOPS and MBps regardless of competing workloads. Set a throughput ceiling to prevent less critical workloads from consuming excessive performance resources and degrading the performance of more critical workloads.

You can use the `max-throughput` field for a policy group to define a throughput ceiling for storage object workloads (QoS Max). You can apply the policy group when you create or modify the storage object.

## Before you begin

- You must be a cluster administrator to create a policy group and to apply a policy group to an SVM.

## About this task

- Beginning with ONTAP 9.4, you can use a *non-shared* QoS policy group to specify that the defined throughput ceiling applies to each member workload individually. Otherwise, the policy group is *shared:* the total throughput for the workloads assigned to the policy group cannot exceed the specified ceiling.

  Set `-is-shared=false` for the `qos policy-group create` command to specify a non-shared policy group.

- You can specify the throughput limit for the ceiling in IOPS, MB/s, or IOPS, MB/s. If you specify both IOPS and MB/s, whichever limit is reached first is enforced.

  Note: If you set a ceiling and a floor for the same workload, you can specify the throughput limit for the ceiling in IOPS only.

- A storage object that is subject to a QoS limit must be contained by the SVM to which the policy group belongs. Multiple policy groups can belong to the same SVM.

- You cannot assign a storage object to a policy group if its containing object or its child objects belong to the policy group.

- It is a QoS best practice to apply a policy group to the same type of storage objects.

## Steps

1. Create a policy group:

```
qos policy-group create -policy-group <policy_group> -vserver <SVM> -max-throughput <number_of_iops_|Mb/S|iops,Mb/S> -is-shared <true|false>
```

Learn more about `qos policy-group create` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-policy-group-create.html).

You can use the `qos policy-group modify` command to adjust throughput ceilings. Learn more about `qos policy-group modify` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-policy-group-modify.html).

The following example creates the shared policy group `pg-vs1` with a maximum throughput of 5,000 IOPS:

```
cluster1::> qos policy-group create -policy-group pg-vs1 -vserver vs1 -max-throughput 5000iops -is-shared true
```

The following example creates the non-shared policy group `pg-vs3` with a maximum throughput of 100 IOPS and 400 Kb/S:

```
cluster1::> qos policy-group create -policy-group pg-vs3 -vserver vs3 -max-throughput 100iops,400KB/s -is-shared false
```

The following example creates the non-shared policy group `pg-vs4` without a throughput limit:

```
cluster1::> qos policy-group create -policy-group pg-vs4 -vserver vs4 -is-shared false
```

2. Apply a policy group to an SVM, file, volume, or LUN:

```
vserver create -vserver <SVM> -qos-policy-group <policy_group>
```

You can use the `vserver modify` command to apply a different policy group to the storage object.

The following example applies policy group `pg-vs1` to SVM `vs1`:

```
cluster1::> vserver create -vserver vs1 -qos-policy-group pg-vs1
```

The following examples apply policy group `pg-app` to the volumes `app1` and `app2`:

```
cluster1::> volume create -vserver vs2 -volume app1 -aggregate aggr1 -qos-policy-group pg-app
cluster1::> volume create -vserver vs2 -volume app2 -aggregate aggr1 -qos-policy-group pg-app
```

3. Monitor policy group performance:

```
qos statistics performance show
```

Note: Monitor performance from the cluster. Do not use a tool on the host to monitor performance.

Example output:

```
cluster1::> qos statistics performance show
Policy Group           IOPS      Throughput   Latency
-------------------- -------- --------------- ----------
-total-                 12316       47.76MB/s  1264.00us
pg_vs1                   5008       19.56MB/s     2.45ms
_System-Best-Effort        62       13.36KB/s     4.13ms
_System-Background         30           0KB/s        0ms
```

Learn more about `qos statistics performance show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-performance-show.html).

4. Monitor workload performance:

```
qos statistics workload performance show
```

Note: Monitor performance from the cluster. Do not use a tool on the host to monitor performance.

Example output:

```
cluster1::> qos statistics workload performance show
Workload          ID     IOPS      Throughput    Latency
--------------- ------ -------- ---------------- ----------
-total-              -    12320        47.84MB/s  1215.00us
app1-wid7967      7967     7219        28.20MB/s   319.00us
vs1-wid12279     12279     5026        19.63MB/s     2.52ms
_USERSPACE_APPS     14       55        10.92KB/s   236.00us
_Scan_Backgro..   5688       20            0KB/s        0ms
```

Learn more about `qos statistics workload performance show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-performance-show.html).

You can use the `qos statistics workload latency show` command to view detailed latency statistics for QoS workloads. Learn more about `qos statistics workload latency show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-latency-show.html).
