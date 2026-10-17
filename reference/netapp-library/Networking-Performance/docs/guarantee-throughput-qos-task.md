# Learn about ONTAP QoS throughput guarantee
Source: https://docs.netapp.com/us-en/ontap/performance-admin/guarantee-throughput-qos-task.html
Fetched: 2026-07-07

You can use storage quality of service (QoS) to guarantee that performance of critical workloads is not degraded by competing workloads. You can set a throughput *ceiling* on a competing workload to limit its impact on system resources, or set a throughput *floor* for a critical workload, ensuring that it meets minimum throughput targets, regardless of demand by competing workloads. You can set a throughput ceiling and a throughput floor for the same workload.

Adaptive and non-adaptive QoS policy groups are automatically enabled to temporarily increase a workload's throughput ceiling by 50% for a duration of 1 second to respond to short-term demands for higher performance. For example, suppose you are starting up a database or booting multiple virtual machines (VMs). These workloads could create a spike in resource consumption, causing other workloads to be slowed. The automatic, temporary increase in throughput allows ONTAP to allocate the short-term resources needed to initialize the database or boot the virtual machines without your intervention and without you incurring the cost of permanently increasing your system resources to support such tasks. Beginning with ONTAP 9.19.1, you can use the `burst-percent`, `burst-duration` and `burst-iops` options with the `qos-create` command and the `qos-modify` command to change these defaults. In ONTAP 9.18.1 and earlier, the default settings cannot be modified.

## Throughput ceilings (QoS Max)

A throughput ceiling limits throughput for a workload to a maximum number of IOPS or MBps, or IOPS and MBps. The throughput ceiling for a workload ensures that it does not "bully" other workloads.

A *policy group* defines the throughput ceiling for one or more workloads. A workload represents the I/O operations for a *storage object:* a volume, file, qtree or LUN, or all the volumes, files, qtrees, or LUNs in an SVM. You can specify the ceiling when you create the policy group, or you can wait until after you monitor workloads to specify it.

Note: Throughput to workloads might exceed the specified ceiling by up to 10%, especially if a workload experiences rapid changes in throughput. The ceiling might be exceeded by up to 50% to handle bursts. Bursts occur on single nodes when tokens accumulate up to 150%.

## Throughput floors (QoS Min)

A throughput floor guarantees that throughput for a workload does not fall below a minimum number of IOPS or MBps, or IOPS and MBps.

Tip: As the examples suggest, a throughput ceiling throttles throughput directly. A throughput floor throttles throughput indirectly, by giving priority to the workloads for which the floor has been set.

You can specify the floor when you create the policy group, or you can wait until after you monitor workloads to specify it.

Beginning with ONTAP 9.13.1, you can set throughput floors at the SVM scope with Adaptive policy group templates. In releases of ONTAP before 9.13.1, a policy group that defines a throughput floor cannot be applied to an SVM.

Note: In releases before ONTAP 9.7, throughput floors are guaranteed when there is sufficient performance capacity available. In ONTAP 9.7 and later, throughput floors can be guaranteed even when there is insufficient performance capacity available. This new floor behavior is called floors v2. To meet the guarantees, floors v2 can result in higher latency on workloads without a throughput floor or on work that exceeds the floor settings. Floors v2 applies to both QoS and adaptive QoS. The option of enabling/disabling the new behavior of floors v2 is available in ONTAP 9.7P6 and later. A workload might fall below the specified floor during critical operations like `volume move trigger-cutover`. Even when sufficient capacity is available and critical operations are not taking place, throughput to a workload might fall below the specified floor by up to 5%. If floors are overprovisioned and there is no performance capacity, some workloads might fall below the specified floor.

## Shared and non-shared QoS policy groups

Beginning with ONTAP 9.4, you can use a *non-shared* QoS policy group to specify that the defined throughput ceiling or floor applies to each member workload individually. Behavior of *shared* policy groups depends on the policy type:

- For throughput ceilings, the total throughput for the workloads assigned to the shared policy group cannot exceed the specified ceiling.
- For throughput floors, the shared policy group can be applied to a single workload only.

## Adaptive QoS

Ordinarily, the value of the policy group you assign to a storage object is fixed. You need to change the value manually when the size of the storage object changes. An increase in the amount of space used on a volume, for example, usually requires a corresponding increase in the throughput ceiling specified for the volume.

*Adaptive QoS* automatically scales the policy group value to workload size, maintaining the ratio of IOPS to TBs|GBs as the size of the workload changes. That is a significant advantage when you are managing hundreds or thousands of workloads in a large deployment.

You typically use adaptive QoS to adjust throughput ceilings, but you can also use it to manage throughput floors (when workload size increases). Workload size is expressed as either the allocated space for the storage object or the space used by the storage object.

Note: Used space is available for throughput floors in ONTAP 9.5 and later. It is not supported for throughput floors in ONTAP 9.4 and earlier.

- An *allocated space* policy maintains the IOPS/TB|GB ratio according to the nominal size of the storage object. If the ratio is 100 IOPS/GB, a 150 GB volume will have a throughput ceiling of 15,000 IOPS for as long as the volume remains that size. If the volume is resized to 300 GB, adaptive QoS adjusts the throughput ceiling to 30,000 IOPS.
- A *used space* policy (the default) maintains the IOPS/TB|GB ratio according to the amount of actual data stored before storage efficiencies. If the ratio is 100 IOPS/GB, a 150 GB volume that has 100 GB of data stored would have a throughput ceiling of 10,000 IOPS. As the amount of used space changes, adaptive QoS adjusts the throughput ceiling according to the ratio.

Beginning with ONTAP 9.5, you can specify an I/O block size for your application that enables a throughput limit to be expressed in both IOPS and MBps. The MBps limit is calculated from the block size multiplied by the IOPS limit. For example, an I/O block size of 32K for an IOPS limit of 6144IOPS/TB yields an MBps limit of 192MBps.

You can expect the following behavior for both throughput ceilings and floors:

- When a workload is assigned to an adaptive QoS policy group, the ceiling or floor is updated immediately.
- When a workload in an adaptive QoS policy group is resized, the ceiling or floor is updated in approximately five minutes.

Throughput must increase by at least 10 IOPS before updates take place.

Adaptive QoS policy groups are always non-shared: the defined throughput ceiling or floor applies to each member workload individually.

Beginning with ONTAP 9.6, throughput floors are supported on ONTAP Select premium with SSD.

### Adaptive policy group template

Beginning with ONTAP 9.13.1, you can set an adaptive QoS template on an SVM. Adaptive policy group templates enable you to set throughput floors and ceilings for all volumes in an SVM.

Adaptive policy group templates can only be set after the SVM has been created. Use the `vserver modify` command with the `-qos-adaptive-policy-group-template` parameter to set the policy.

When you set an adaptive policy group template, volumes created or migrated after setting the policy automatically inherit the policy. Any volumes existing on the SVM are not impacted when you assign the policy template. If you disable the policy on the SVM, any volume subsequently migrated to or created on the SVM will not receive the policy. Disabling the adaptive policy group template does not impact volumes that inherited the policy template as they retain the policy template.

For more information, see Set an adaptive policy group template (https://docs.netapp.com/us-en/ontap/performance-admin/adaptive-policy-template-task.html).

## General support

The following table shows the differences in support for throughput ceilings, throughput floors, and adaptive QoS.

| Resource or feature    | Throughput ceiling | Throughput floor                                                            | Throughput floor v2                                                         | Adaptive QoS  |
| ---------------------- | ------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------- |
| ONTAP 9 version        | All                | 9.2 and later                                                               | 9.7 and later                                                               | 9.3 and later |
| Platforms              | All                | AFF, C190 (1), ONTAP Select premium with SSD (1)                            | AFF, C190, ONTAP Select premium with SSD                                     | All           |
| Protocols              | All                | All                                                                         | All                                                                         | All           |
| FabricPool             | Yes                | Yes, if the tiering policy is set to "none" and no blocks are in the cloud. | Yes, if the tiering policy is set to "none" and no blocks are in the cloud. | No            |
| SnapMirror Synchronous | Yes                | No                                                                          | No                                                                          | Yes           |

(1) C190 and ONTAP Select support started with the ONTAP 9.6 release.

## Supported workloads for throughput ceilings

Root volumes, load-sharing mirrors, and data protection mirrors are not supported.

| Workload support                    | ONTAP 9.8 and later | ONTAP 9.7 to 9.4 | ONTAP 9.3 and earlier |
| ------------------------------------ | -------------------- | ----------------- | ---------------------- |
| Volume                               | yes                  | yes               | yes                    |
| File                                 | yes                  | yes               | yes                    |
| LUN                                  | yes                  | yes               | yes                    |
| SVM                                  | yes                  | yes               | yes                    |
| FlexGroup volume                     | yes                  | yes               | yes (ONTAP 9.3 only)   |
| qtrees (1)                           | yes                  | no                | no                     |
| Multiple workloads per policy group  | yes                  | yes               | yes                    |
| Non-shared policy groups             | yes                  | yes               | no                     |

(1) Beginning with ONTAP 9.9.1, SMB access is also supported in qtrees in FlexVol and FlexGroup volumes with SMB enabled. Beginning with ONTAP 9.8, NFS access is supported in qtrees in FlexVol and FlexGroup volumes with NFS enabled.

## Supported workloads for throughput floors

Root volumes, load-sharing mirrors, and data protection mirrors are not supported.

| Workload support                    | ONTAP 9.13.1 and later | ONTAP 9.8 to 9.13.0 | ONTAP 9.4 to 9.7 | ONTAP 9.3 |
| ------------------------------------ | ----------------------- | --------------------- | ------------------ | --------- |
| Volume                               | yes                     | yes                   | yes                | yes       |
| File                                 | yes                     | yes                   | yes                | yes       |
| LUN                                  | yes                     | yes                   | yes                | yes       |
| SVM                                  | yes                     | no                    | no                 | no        |
| FlexGroup volume                     | yes                     | yes                   | yes                | no        |
| qtrees (1)                           | yes                     | yes                   | no                 | no        |
| Multiple workloads per policy group  | yes                     | yes                   | yes                | no        |
| Non-shared policy groups             | yes                     | yes                   | yes                | no        |

(1) Beginning with ONTAP 9.8, NFS access is supported in qtrees in FlexVol and FlexGroup volumes with NFS enabled. Beginning with ONTAP 9.9.1, SMB access is also supported in qtrees in FlexVol and FlexGroup volumes with SMB enabled.

## Supported workloads for adaptive QoS

Root volumes, load-sharing mirrors, and data protection mirrors are not supported.

| Workload support                    | ONTAP 9.13.1 and later | ONTAP 9.4 to 9.13.0 | ONTAP 9.3 |
| ------------------------------------ | ----------------------- | --------------------- | --------- |
| Volume                               | yes                     | yes                   | yes       |
| File                                 | yes                     | yes                   | no        |
| LUN                                  | yes                     | yes                   | no        |
| SVM                                  | yes                     | no                    | no        |
| FlexGroup volume                     | yes                     | yes                   | no        |
| Multiple workloads per policy group  | yes                     | yes                   | yes       |
| Non-shared policy groups             | yes                     | yes                   | yes       |

## Maximum number of workloads and policy groups

| Workload support              | ONTAP 9.4 and later | ONTAP 9.3 and earlier |
| ------------------------------ | -------------------- | ---------------------- |
| Maximum workloads per cluster  | 40,000               | 12,000                 |
| Maximum workloads per node     | 40,000               | 12,000                 |
| Maximum policy groups          | 12,000               | 12,000                 |
