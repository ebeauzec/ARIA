# Set throughput with ONTAP adaptive QoS policy groups
Source: https://docs.netapp.com/us-en/ontap/performance-admin/adaptive-qos-policy-groups-task.html
Fetched: 2026-07-07

You can use an *adaptive QoS* policy group to automatically scale a throughput ceiling or floor to volume size, maintaining the ratio of IOPS to TBs/GBs as the size of the volume changes. That is a significant advantage when you are managing hundreds or thousands of workloads in a large deployment.

## Before you begin

- You must be a cluster administrator to create a policy group.
- The storage object you want to add to the policy group must be a member of a non-adaptive policy group. A storage object can be a member of an adaptive policy group or a non-adaptive policy group, but not both.
- The SVM of the storage object and the policy must be the same.
- The storage object must be online.

## About this task

- Adaptive QoS policy groups are always non-shared: the defined throughput ceiling or floor applies to each member workload individually.
- Adaptive and non-adaptive QoS policy groups are automatically enabled to temporarily increase a workload's throughput ceiling by 50% for a duration of 1 second to respond to short-term demands for higher performance by default. Beginning with ONTAP 9.19.1, you can modify these default settings. In ONTAP 9.18.1 and earlier these settings cannot be changed.

  Options to modify the default settings:

  | Option | Description | Default setting |
  | --- | --- | --- |
  | `burst-percent` | Throughput increase in percentage | 50% |
  | `burst-duration` | Duration for the throughput increase in seconds | 1 second |
  | `burst-iops` | Maximum number of IOPs above the throughput ceiling for the specified burst duration | 0 |

- The ratio of throughput limits to storage object size is determined by the interaction of the following fields:
  - `expected-iops` is the minimum expected IOPS per allocated TB/GB.
  - `peak-iops` is the maximum possible IOPS per allocated or used TB/GB.
  - `expected-iops-allocation` specifies whether allocated space (the default) or used space is used for expected-iops.
  - `peak-iops-allocation` specifies whether allocated space or used space (the default) is used for `peak-iops`.
  - `absolute-min-iops` is the absolute minimum number of IOPS. You can use this field with very small storage objects. It overrides both `peak-iops` and/or `expected-iops` when `absolute-min-iops` is greater than the calculated `expected-iops`. For example, if you set `expected-iops` to 1,000 IOPS/TB, and the volume size is less than 1 GB, the calculated `expected-iops` will be a fractional IOP. The calculated `peak-iops` will be an even smaller fraction. You can avoid this by setting `absolute-min-iops` to a realistic value.
  - `block-size` specifies the application I/O block size. The default is 32K. Valid values are 8K, 16K, 32K, 64K, ANY. ANY means that the block size is not enforced.

## Steps

1. Create an adaptive QoS policy group:

```
qos adaptive-policy-group create -policy group <policy_group> -vserver <SVM> -expected-iops <number_of_iops>/TB|GB -peak-iops <number_of_iops>/TB|GB -expected-iops-allocation-space|used-space -peak-iops-allocation allocated-space|used-space -absolute-min-iops <number_of_iops> -block-size 8K|16K|32K|64K|ANY
```

Learn more about `qos adaptive-policy-group create` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/qos-adaptive-policy-group-create.html).

Note: `-expected-iops-allocation` and `-block-size` is available in ONTAP 9.5 and later. These options are not supported in ONTAP 9.4 and earlier.

The following command creates adaptive QoS policy group `adpg-app1` with `-expected-iops` set to 300 IOPS/TB, `-peak-iops` set to 1,000 IOPS/TB, `-peak-iops-allocation` set to `used-space`, and `-absolute-min-iops` set to 50 IOPS:

```
cluster1::> qos adaptive-policy-group create -policy group adpg-app1 -vserver vs2 -expected-iops 300iops/tb -peak-iops 1000iops/TB -peak-iops-allocation used-space -absolute-min-iops 50iops
```

2. Apply an adaptive QoS policy group to a volume:

```
volume create -vserver SVM -volume <volume_name> -aggregate <aggregate> -size <number_of_ TB|GB> -qos-adaptive-policy-group <policy_group>
```

Learn more about `volume create` in the ONTAP command reference (https://docs.netapp.com/us-en/ontap-cli/volume-create.html).

The following command applies adaptive QoS policy group `adpg-app1` to volume `app1`:

```
cluster1::> volume create -vserver vs1 -volume app1 -aggregate aggr1 -size 2TB -qos-adaptive-policy-group adpg-app1
```

The following commands apply the default adaptive QoS policy group `extreme` to the new volume `app4` and to the existing volume `app5`. The throughput ceiling defined for the policy group applies to volumes `app4` and `app5` individually:

```
cluster1::> volume create -vserver vs4 -volume app4 -aggregate aggr4 -size 2TB -qos-adaptive-policy-group extreme
cluster1::> volume modify -vserver vs5 -volume app5 -qos-adaptive-policy-group extreme
```

## Default adaptive QoS policy groups

Three default adaptive QoS policy groups are available. You can apply these policy groups directly to a volume.

| Default policy group | Expected IOPS/TB | Peak IOPS/TB | Absolute Min IOPS |
| --- | --- | --- | --- |
| `extreme` | 6,144 | 12,288 | 1000 |
| `performance` | 2,048 | 4,096 | 500 |
| `value` | 128 | 512 | 75 |
