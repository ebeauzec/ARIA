# Quality of service (QoS)
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vsphere-qos.html
Fetched: 2026-07-07

Throughput limits are useful in controlling service levels, managing unknown workloads, or testing applications before deployment to ensure they don't affect other production workloads. They can also constrain a "bully" workload after it's identified.

## ONTAP QoS policy support

ONTAP's storage QoS feature limits throughput in MBps and/or IOPS for storage objects such as files, LUNs, volumes, or entire SVMs. Minimum service levels based on IOPS are also supported — for SAN objects since ONTAP 9.2, and for NAS objects since ONTAP 9.3.

The QoS maximum throughput limit on an object can be set in MBps and/or IOPS — if both are set, the first limit reached is enforced. A workload can contain multiple objects, and a policy can apply to one or more workloads; when a policy applies to multiple workloads, they share the policy's total limit. Nested objects are not supported (e.g., individual files within a volume can't each have their own policy). QoS minimums can only be set in IOPS.

Tools for managing ONTAP QoS policies:
- ONTAP CLI
- ONTAP System Manager
- OnCommand Workflow Automation
- Active IQ Unified Manager
- NetApp PowerShell Toolkit for ONTAP
- ONTAP tools for VMware vSphere VASA Provider

To assign a QoS policy to a LUN (including VMFS and RDM), get the SVM (Vserver), LUN path, and serial number from the Storage Systems menu on the ONTAP tools for VMware vSphere home page (select storage system > Related Objects > SAN).

## Non-vVols NFS datastores

A QoS policy can be applied to an entire NFS datastore or to individual VMDK files within it. Important: all VMs on a traditional (non-vVols) NFS datastore share a common I/O queue from a given host — if one VM is throttled by a QoS policy, all I/O for that datastore will appear throttled for that host.

**Example:** A QoS limit is set on vm1.vmdk on a volume mounted as an NFS datastore by host esxi-01. The same host also runs vm2.vmdk on the same volume. If vm1.vmdk is throttled, vm2.vmdk will also appear throttled since they share the same I/O queue. This does not apply to vVols.

Since vSphere 6.5, file-granular limits on non-vVols datastores can be managed via Storage Policy-Based Management (SPBM) with Storage I/O Control (SIOC) v2.

To assign a QoS policy to a VMDK on NFS:
- Apply the policy to the `vmname-flat.vmdk` (the actual virtual disk image), not `vmname.vmdk` (descriptor file) or `vmname.vmx` (VM descriptor file).
- Do not apply policies to other VM files such as virtual swap files (`vmname.vswp`).
- The vSphere web client (Datastore > Files) combines `-flat.vmdk` and `.vmdk` info under one displayed name — add `-flat` to the filename to get the correct path.

FlexGroup datastores offer enhanced QoS with ONTAP tools for VMware vSphere 9.8+ — QoS can be set on all VMs in a datastore or on specific VMs, though the shared-I/O-queue limitation for traditional NFS datastores still applies.

## VMFS datastores

QoS policies can be applied to the FlexVol volume containing the LUNs, or to individual LUNs, but not to individual VMDK files — ONTAP has no awareness of the VMFS file system.

## vVols datastores

Minimum and/or maximum QoS can be set on individual VMs or VMDKs without impacting any other VM/VMDK, via Storage Policy-Based Management and vVols. When creating the storage capability profile (SCP) for the vVol container, specify max and/or min IOPS under the performance capability, then reference the SCP in the VM's storage policy.

> **Note:** vVols requires ONTAP tools for VMware vSphere, which functions as the VASA Provider for ONTAP.

## ONTAP QoS and VMware SIOC

ONTAP QoS and VMware Storage I/O Control (SIOC) are complementary technologies:

| Property | ONTAP QoS | VMware SIOC |
| --- | --- | --- |
| When active | Always active | Active only when contention exists (datastore latency over threshold) |
| Type of units | IOPS, MBps | IOPS, shares |
| vCenter/application scope | Multiple vCenter environments, other hypervisors and applications | Single vCenter server |
| Set QoS on VM (VMDK on NFS)? | Yes | Yes (NFS or VMFS) |
| Set QoS on LUN (RDM)? | Yes | No |
| Set QoS on LUN (VMFS)? | Yes | Yes (datastore can be throttled) |
| Set QoS on volume (NFS datastore)? | Yes | Yes (datastore can be throttled) |
| Set QoS on SVM (tenant)? | Yes | No |
| Policy-based approach? | Yes — shared by all workloads in a policy or applied in full to each | Yes, with vSphere 6.5+ |
| License required | Included with ONTAP | Enterprise Plus |

## VMware Storage Distributed Resource Scheduler (SDRS)

SDRS places VMs on storage based on current I/O latency and space usage, moving VMs/VMDKs nondisruptively between datastores in a datastore cluster (pod). With ONTAP tools, first create a datastore with the plug-in, use vCenter to create the datastore cluster, then add the datastore to it. Additional datastores can be added directly from the provisioning wizard.

Other ONTAP best practices for SDRS:
- All datastores in the cluster should use the same storage type (SAS/SATA/SSD), be all-VMFS or all-NFS, and share the same replication/protection settings.
- Consider default (manual) SDRS mode so recommendations can be reviewed before applying. Effects of VMDK migration:
  - Moving VMDKs between datastores loses space savings from ONTAP cloning/dedup — rerun dedup to regain savings.
  - After SDRS moves VMDKs, recreate snapshots at the source datastore (space is otherwise locked by the moved VM).
  - Moving VMDKs between datastores on the same aggregate has little benefit; SDRS has no visibility into other workloads sharing that aggregate.

## Storage policy based management and vVols

VMware vSphere APIs for Storage Awareness (VASA) let storage admins configure datastores with well-defined capabilities that VM admins can consume without direct interaction. Prior to VASA, VM admins had to identify appropriate datastores manually (documentation/naming conventions). With VASA, the storage admin defines a range of capabilities (performance, tiering, encryption, replication) grouped into a storage capability profile (SCP).

The SCP supports minimum and/or maximum QoS for a VM's data vVols. Minimum QoS is supported only on AFF systems. ONTAP tools for VMware vSphere includes a dashboard showing VM-granular performance and logical capacity for vVols on ONTAP.

After defining an SCP, it's referenced by a VM storage policy, letting vCenter display a list of compatible datastores for VM provisioning — this is storage policy based management.

VASA translates between storage system APIs/constructs and VMware APIs understood by vCenter. NetApp's VASA Provider for ONTAP ships as part of the ONTAP tools for VMware vSphere appliance VM.

ONTAP supports both VMFS and NFS vVols datastores. Best practices (see also TR-4400):
- A vVols datastore can consist of multiple FlexVol volumes across multiple cluster nodes. Simplest approach: a single datastore even with volumes of differing capabilities — SPBM ensures a compatible volume is used. All volumes must belong to a single ONTAP SVM and use a single protocol; one LIF per node per protocol is sufficient. Avoid mixing ONTAP releases within a single vVols datastore since capabilities can vary by release.
- Use ONTAP tools for VMware vSphere to create/manage vVols datastores — it auto-creates protocol endpoints as needed. LUN PEs are mapped using LUN IDs 300+; verify the ESXi host's `Disk.MaxLUN` advanced setting allows LUN IDs above 300 (default 1024) — check via vCenter > host > Configure tab > Disk.MaxLUN.
- Do not install or migrate VASA Provider, vCenter Server, or ONTAP tools itself onto a vVols datastore — this creates mutual dependency that limits management ability during a power outage or other disruption.
- Back up the VASA Provider VM regularly — at minimum, hourly snapshots of the traditional datastore containing it.
