# What is Quality of Service (QoS) in ONTAP?
Source: https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Quality_of_Service_QoS_in_ONTAP
Fetched: 2026-07-07

## Applies to

- ONTAP 9

## Answer

Quality-of-Service (QoS) is a way to throttle storage objects, but also includes performance monitoring of volumes with the QoS statistics commands (https://docs.netapp.com/ontap-9/topic/com.netapp.doc.dot-cm-cmpr-960/TOC__qos__statistics.html).

Note: Adaptive QoS is slightly different and is covered in the article What is Adaptive QoS and how does it work? (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Adaptive_QoS_and_how_does_it_work)

### What is a storage object?

- A Vserver with FlexVol volumes
- A FlexVol volume QoS workload
- A LUN
- A file (typically represents a virtual machine)
- Can include system processes internal to ONTAP, called a System-defined workload

Note: Beginning with ONTAP 9.2, Adaptive QoS was introduced for SAN workloads and expanded to NAS in ONTAP 9.3. For more information, refer to the Adaptive QoS page (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Adaptive_QoS_and_how_does_it_work).

### When to use QoS?

1. Prevent workloads from impacting performance
2. Enable critical applications to achieve consistent performance
3. Monitor and manage application workloads

### What are the components of a QoS policy?

1. Workload types include:
   1. User-defined workload
      1. Beginning with Clustered Data ONTAP 8.3, all created FlexVols are automatically assigned a workload ID
      2. I/O to storage objects that are not assigned to policy groups belong to the "User-Default" workload
   2. System-defined workload (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_are_some_internal_ONTAP_workloads_in_qos_statistics_commands)
   3. User-defined policy group - Enforces a maximum throughput limit on the storage objects that belong to the policy group by throttling input/output (I/O) requests
   4. System-defined policy group - Manages internal work that the cluster performs
2. QoS policy: The maximum IOPs and/or throughput allowed

### What are the rules for assigning storage objects to policy groups?

- Storage objects and policy groups must belong to the same Vserver
- Specify the Vserver to which the policy group belongs when you create the policy group
- Multiple policy groups can belong to the same Vserver
- Multiple storage objects can be put in a single policy group
- A single storage object can be put in a single policy group
- A storage object cannot have two different policy groups assigned
- Nested storage objects cannot belong to policy groups:

| If you assign a... | Then you cannot assign... |
| --- | --- |
| Vserver to a policy group | Any storage objects contained by the Vserver to a policy group |
| Volume to a policy group | The volume's containing Vserver or any child LUNs or files to a policy group |
| LUN to a policy group | The LUN's containing volume or Vserver to a policy group |
| File to a policy group | The file's containing volume or Vserver to a policy group |

### What is not supported with QoS?

- Aggregates
- Entire nodes
- Load-sharing mirrors
- Node root volumes
- Data ONTAP 7-mode FlexCache volumes

Note: The 7-mode FlexCache uses a different technology than the ONTAP 9 version. For more information see the FlexCache Technical Report (https://www.netapp.com/us/media/tr-4571.pdf).

### What are the configuration limits in QoS in ONTAP 9?

| Workload Support | 9.3 and earlier | 9.4 and later |
| --- | --- | --- |
| Maximum workloads per cluster | 12,000 | 40,000 |
| Maximum workloads per node | 12,000 | 40,000 |
| Maximum policy group | 12,000 | 12,000 |

### What should the QoS Limit be set to?

1. Using Active IQ (https://aiq.netapp.com) (AIQ) or Active IQ Unified Manager (AIQUM), determine the Input/Output Operations Per Second (IOPs) and throughput of the volume.
   - To identify volume throughput or IOPs, review How to monitor volume latency from Active IQ Unified Manager (https://kb.netapp.com/data-mgmt/AIQUM/AIQUM_Kbs/How_to_monitor_volume_latency_and_IOPS_from_Active_IQ_Unified_Manager).
   - AIQ is not updated in real-time, so it is recommended to download AIQUM (https://mysupport.netapp.com/site/products/all/details/activeiq-unified-manager/downloads-tab) or monitor with `qos statistics` commands (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/How_to_use_qos_statistics_commands_monitor_volume_latency_real_time).
2. Once the top value is seen, set a value incrementally smaller than the peaks.
3. Incrementally set the throttle value lower until latency is at desired levels.

Notes:
- ONTAP will adjust QoS throttles almost instantly, so you can monitor live with `qos statistics` commands so users will not be impacted more than a few seconds.
- See the article Can I increase IOPS on a QoS policy or will it cause performance problems? (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/Can_I_increase_IOPS_on_a_QoS_policy_or_will_it_cause_performance_problems) for additional guidance.

### What happens if the QoS limit is too high?

See QoS Limits causing high volume latency (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/QoS_Limits_causing_high_volume_latency) and Can I increase IOPS on a QoS policy or will it cause performance problems? (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/Can_I_increase_IOPS_on_a_QoS_policy_or_will_it_cause_performance_problems).

Should the built-in Value, Performance, and Fixed policies be used, or should custom ones be made?
- The default ones can provide a starting point, but realistically custom ones should be made after monitoring performance.

## Additional Information

- Adaptive QoS Information (https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Adaptive_QoS_and_how_does_it_work)
- QoS commands documentation (https://docs.netapp.com/ontap-9/index.jsp?topic=%2Fcom.netapp.doc.dot-cm-cmpr-960%2FTOC__qos.html&cp=5_2_17)
- How to avoid bullying application performance issues in ONTAP Select Clusters (https://kb.netapp.com/on-prem/ontap/ontap-select/Select-KBs/How_to_avoid_bullying_application_performance_issues_in_ONTAP_Select_Clusters)
- qos statistics commands documentation (https://docs.netapp.com/ontap-9/topic/com.netapp.doc.dot-cm-cmpr-960/TOC__qos__statistics.html)

Example of creating a QoS policy:

```
Cluster::> qos policy-group create -policy-group vol1-qos -vserver svm0 -max-throughput 50iops,10MB/s -min-throughput 0

Cluster::> vol modify -volume vol1 -qos-policy-group vol1-qos
Volume modify successful on volume test_cifs_homedir of Vserver svm0.

Cluster::> qos policy-group show
Name             Vserver     Class        Wklds Throughput   Is Shared
---------------- ----------- ------------ ----- ------------ ---------
vol3-qos         svm0        user-defined 0     0-3000IOPS,200MB/s
                                                             true
vol1-qos         svm0        user-defined 1     0-50IOPS,10MB/s
                                                             true
2 entries were displayed.

Cluster::> vol show -fields volume,qos-policy-group,qos-adaptive-policy-group
vserver         volume qos-policy-group qos-adaptive-policy-group
--------------- ------ ---------------- -------------------------
Cluster-node1   vol0   -                -
svm0            svm_root
                       -                -
svm0            vol1
                       vol1-qos         -
svm0            vol3
                       vol3-qos         -
3 entries were displayed.

Cluster::>
```

NetApp provides no representations or warranties regarding the accuracy or reliability or serviceability of any information or recommendations provided in this publication or with respect to any results that may be obtained by the use of the information or observance of any recommendations provided herein. The information in this document is distributed AS IS and the use of this information or the implementation of any recommendations or techniques herein is a customer's responsibility and depends on the customer's ability to evaluate and integrate them into the customer's operational environment.
