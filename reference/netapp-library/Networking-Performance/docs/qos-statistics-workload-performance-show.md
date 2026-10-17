# qos statistics workload performance show
Source: https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-performance-show.html
Fetched: 2026-07-07

Display system performance data per QoS workload

**Availability:** This command is available to *cluster* administrators at the *admin* privilege level.

## Description

The `qos statistics workload performance show` command shows the current system performance that each QoS workload is achieving.

The command displays the following data:

- The QoS workload name (Workload)
- The QoS workload ID (ID)
- Input/output operations performed per second (IOPS)
- Throughput in kilobytes per second (KB/s) or megabytes per second (MB/s) as appropriate (Throughput)
- Latency observed per request in microseconds (us) or milliseconds (ms) as appropriate (Latency)

The results displayed per iteration are sorted by IOPS. Each iteration starts with a row that displays the total IOPS used across all QoS workloads. Other columns in this row are either totals or averages.

## Parameters

- `[-node {<nodename>|local}]` - Node. Selects the QOS workloads that match this parameter value. If you do not specify this parameter, the command displays data for the entire cluster.
- `[-iterations <integer>]` - Number of Iterations. Specifies the number of times the display is refreshed before terminating. If you do not specify this parameter, the command iterates until interrupted by Ctrl-C.
- `[-refresh-display {true|false}]` - Toggle Screen Refresh Between Each Iteration. Specifies the display style. If true, the command clears the display after each data iteration. If false, the command displays each data iteration below the previous one. The default is false.
- `[-rows <integer>]` - Number of Rows in the Output. Specifies the number of busiest QoS policy groups to display. Valid values are from 1 to 20. The default value is 10.
- `[-policy-group <text>]` - QoS Policy Group Name. Selects the QoS workloads that belong to the QoS policy group specified by this parameter value. If you do not specify this parameter, the command displays data for all QoS workloads.
- `[-adaptive-policy-group <text>]` - Adaptive QoS Policy Group Name. Selects the QoS workloads that belong to the QoS adaptive policy group specified by this parameter value. If you do not specify this parameter, the command displays data for all QoS workloads.
- `[-workload <text>]` - QoS Workload Name. Selects the QoS workload that matches this parameter value. If you do not specify this parameter, the command displays data for all QoS workloads.
- `[-workload-id <integer>]` - QoS Workload ID. Selects the QoS workload that matches the QoS workload ID specified by this parameter value.
- `[-show-flexgroup-as-constituents {true|false}]` - Display Flexgroups as Constituents. If the parameter is specified and if the value is true, it will display data for FlexVol volumes and FlexGroup constituents. Otherwise it will display data for FlexVol volumes and FlexGroup volumes.

## Examples

```
cluster1::> qos statistics workload performance show -iterations 100 -rows 4
Workload            ID     IOPS       Throughput    Latency
--------------- ------ -------- ---------------- ----------
-total-              -       97         1.90MB/s   216.87ms
_Scan_Besteff..    101       31            0KB/s        0ms
vol_2-wid104       104       28         1.75MB/s   412.78ms
vol_1-wid103       103       25       100.00KB/s   169.16ms
vs1vol0-wid102     102       13        52.00KB/s   403.78ms
-total-              -       98      1276.00KB/s    89.98ms
_Scan_Besteff..    101       34            0KB/s        0ms
vs1vol0-wid102     102       28       112.00KB/s    80.70ms
vol_1-wid103       103       19        76.00KB/s   114.72ms
vol_2-wid104       104       17      1088.00KB/s   257.60ms
-total-              -       78      1152.00KB/s   225.22ms
_Scan_Besteff..    101       30            0KB/s        0ms
vol_1-wid103       103       17        68.00KB/s   452.27ms
vol_2-wid104       104       16      1024.00KB/s   419.93ms
vs1vol0-wid102     102       15        60.00KB/s   210.63ms
```

The example above displays the system performance for the 4 QoS workloads with the highest IOPS and it refreshes the display 100 times before terminating.

```
cluster1::> qos statistics workload performance show -iterations 100 -rows 2 -policy-group pg1
Workload          ID       IOPS       Throughput    Latency
--------------- ------ -------- ---------------- ----------
-total-              -     2598         9.96MB/s  1223.00us
file-testfile..   4228      650         2.54MB/s  1322.00us
file-testfile..  11201      635         2.48MB/s  1128.00us
-total-              -     2825        10.89MB/s   714.00us
file-testfile..   4228      707         2.76MB/s   759.00us
file-testfile..  11201      697         2.72MB/s   693.00us
-total-              -     2696        10.13MB/s  1149.00us
file-testfile..   4228      645         2.52MB/s   945.00us
file-testfile..   6827      634         2.48MB/s  1115.00us
```

The example above displays the system performance for the 2 QoS workloads belonging to QoS policy group `pg1` with the highest IOPS and it refreshes the display 100 times before terminating.

```
cluster1::> qos statistics workload performance show -iterations 100 -workload-id 11201
Workload            ID     IOPS       Throughput    Latency
--------------- ------ -------- ---------------- ----------
-total-              -     2866        10.92MB/s   905.00us
file-testfile..  11201      674         2.63MB/s   889.00us
-total-              -     2761        10.55MB/s  1054.00us
file-testfile..  11201      638         2.49MB/s  1055.00us
-total-              -     2810        10.58MB/s   832.00us
file-testfile..  11201      685         2.68MB/s   909.00us
-total-              -     2593         9.86MB/s  1092.00us
file-testfile..  11201      632         2.47MB/s   964.00us
```

The example above displays the system performance for the QoS workload with QoS workload ID `11201` and it refreshes the display 100 times before terminating.
