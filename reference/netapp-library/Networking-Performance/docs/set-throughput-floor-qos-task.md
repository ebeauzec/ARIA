# Set a throughput floor with ONTAP QoS policy groups
Source: https://docs.netapp.com/us-en/ontap/performance-admin/set-throughput-floor-qos-task.html
Fetched: 2026-07-07

A QoS minimum or throughput floor guarantees that throughput for a workload does not fall below a minimum number of IOPS or MBps, or IOPS and MBps regardless of competing workloads. Set a throughput floor to ensure critical workloads are prioritized and meet minimum performance requirements.

You can use the `min-throughput` field for a policy group to define a throughput floor for storage object workloads (QoS Min). You can apply the policy group when you create or modify the storage object.

## Before you begin

- You must be a cluster administrator to create a policy group.

## About this task

- Beginning with ONTAP 9.13.1, you can enforce throughput floors at the SVM level using an adaptive policy group template (https://docs.netapp.com/us-en/ontap/performance-admin/adaptive-policy-template-task.html). You cannot set an adaptive policy group template on an SVM with a QoS policy group.
- Beginning with ONTAP 9.8, you can specify the throughput floor in IOPS or MBps, or IOPS and MBps.
- Beginning with ONTAP 9.4, you can use a *non-shared* QoS policy group to specify that the defined throughput floor be applied to each member workload individually. This is the only condition in which a policy group for a throughput floor can be applied to multiple workloads.

  Set `-is-shared=false` for the `qos policy-group create` command to specify a non-shared policy group.

- Throughput to a workload might fall below the specified floor if there is insufficient performance capacity (headroom) on the node or aggregate.
- A storage object that is subject to a QoS limit must be contained by the SVM to which the policy group belongs. Multiple policy groups can belong to the same SVM.
- It is a QoS best practice to apply a policy group to the same type of storage objects.
- A policy group that defines a throughput floor cannot be applied to an SVM.

## Steps

1. Check for adequate performance capacity on the node or aggregate, as described in Identifying remaining performance capacity (https://docs.netapp.com/us-en/ontap/performance-admin/identify-remaining-performance-capacity-task.html).

2. Create a policy group:

```
qos policy-group create -policy-group <policy_group> -vserver <SVM> -min-throughput <qos_target> -is-shared <true|false>
```

Learn more about `qos policy-group create` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-policy-group-create.html).

The following example creates the shared policy group `pg-vs2` with a minimum throughput of 1,000 IOPS:

```
cluster1::> qos policy-group create -policy group pg-vs2 -vserver vs2 -min-throughput 1000iops -is-shared true
```

The following example creates the non-shared policy group `pg-vs4` without a throughput limit:

```
cluster1::> qos policy-group create -policy group pg-vs4 -vserver vs4 -is-shared false
```

You can use the `qos policy-group modify` command to adjust throughput floors. Learn more about `qos policy-group modify` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-policy-group-modify.html).

3. Apply a policy group to a volume or LUN:

```
vserver create -vserver <SVM> -qos-policy-group <policy_group>
```

You can use the `vserver modify` command to apply a different policy group to the storage object.

The following example applies policy group `pg-app2` to the volume `app2`:

```
cluster1::> volume create -vserver vs2 -volume app2 -aggregate aggr1 -qos-policy-group pg-app2
```

4. Monitor policy group performance:

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
pg_app2                  7216       28.19MB/s   420.00us
_System-Best-Effort        62       13.36KB/s     4.13ms
_System-Background         30           0KB/s        0ms
```

Learn more about `qos statistics performance show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-performance-show.html).

5. Monitor workload performance:

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
app2-wid7967      7967     7219        28.20MB/s   319.00us
vs1-wid12279     12279     5026        19.63MB/s     2.52ms
_USERSPACE_APPS     14       55        10.92KB/s   236.00us
_Scan_Backgro..   5688       20            0KB/s        0ms
```

Learn more about `qos statistics workload performance show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-performance-show.html).

You can use the `qos statistics workload latency show` command to view detailed latency statistics for QoS workloads. Learn more about `qos statistics workload latency show` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-latency-show.html).
