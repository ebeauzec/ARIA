# Understanding MetroCluster data protection and disaster recovery
Source: https://docs.netapp.com/us-en/ontap-metrocluster/manage/concept_understanding_mcc_data_protection_and_disaster_recovery.html
Fetched: 2026-07-07

It is helpful to understand how MetroCluster protects data and provides transparent recovery from failures so that you can manage your switchover and switchback activities easily and efficiently.

MetroCluster uses mirroring to protect the data in a cluster. It provides disaster recovery through a single MetroCluster command that activates a secondary on the survivor site to serve the mirrored data originally owned by a primary site affected by disaster.

## How eight- and four-node MetroCluster configurations provide local failover and switchover

Eight- and four-node MetroCluster configurations protect data on both a local level and cluster level.

MetroCluster configurations protect data by using two physically separated, mirrored clusters. Each cluster synchronously mirrors the data and storage virtual machine (SVM) configuration of the other. When a disaster occurs at one site, an administrator can activate the mirrored SVM and begin serving the mirrored data from the surviving site. Additionally, the nodes in each cluster are configured as an HA pair, providing a level of local failover.

### How local HA data protection works in a MetroCluster configuration

The two clusters in the peered network provide bidirectional disaster recovery, where each cluster can be the source and backup of the other cluster. Each cluster includes two nodes, configured as an HA pair. In the case of a failure or required maintenance within a single node's configuration, storage failover can transfer that node's operations to its local HA partner.

The HA functionality is the same in MetroCluster IP configurations as MetroCluster FC, except that the HA interconnect is provided by the cluster switches.

Related: [High-availability configuration](https://docs.netapp.com/us-en/ontap/high-availability/index.html)

## How MetroCluster configurations provide data and configuration replication

MetroCluster configurations use a variety of ONTAP features to provide synchronous replication of data and configuration between the two MetroCluster sites.

### Configuration protection with the configuration replication service

The ONTAP configuration replication service (CRS) protects the MetroCluster configuration by automatically replicating the information to the DR partner. The CRS synchronously replicates local node configuration to the DR partner in the partner cluster over the cluster peering network. The information replicated includes the cluster configuration and the SVM configuration.

### Replication of SVMs during MetroCluster operations

The CRS provides redundant data server configuration and mirroring of data volumes belonging to the SVM. If a switchover occurs, the source SVM is brought down and the destination SVM, located on the surviving cluster, becomes active.

Note: Destination SVMs in the MetroCluster configuration have the suffix "-mc" automatically appended to their name. If the SVM name contains a period, the suffix "-mc" is applied prior to the first period (e.g., SVM.DNS.NAME becomes SVM-MC.DNS.NAME).

Example: SVM_cluster_A serves data on cluster A (sync-source, replicated to SVM_cluster_A-mc, a sync-destination SVM on cluster B). SVM_cluster_B serves data on cluster B (sync-source, replicated to SVM_cluster_B-mc on cluster A). SVM_cluster_B-mc and SVM_cluster_A-mc are stopped during normal healthy operation and activated only after a successful switchover from their respective source cluster.

If a switchover occurs, the remote plex on the surviving cluster comes online and the secondary SVM begins serving the data.

The availability of remote plexes after switchover depends on the MetroCluster configuration type:
- **MetroCluster FC configurations**: after switchover, both local and remote plexes remain online if the disaster site storage is accessible via the ISLs. If the ISLs have failed and disaster site storage is unavailable, the sync-destination SVM begins serving data from the surviving site.
- **MetroCluster IP configurations**: availability depends on ONTAP version. Beginning with ONTAP 9.5, both local and remote plexes remain online if the disaster site nodes remain booted up. Prior to ONTAP 9.5, storage is available only from the local plex on the surviving site, and the sync-destination SVM begins serving data from the surviving site.

### How MetroCluster configurations use SyncMirror to provide data redundancy

Mirrored aggregates using SyncMirror functionality provide data redundancy and contain the volumes owned by the source and destination SVM. Data is replicated into disk pools on the partner cluster. Unmirrored aggregates are also supported.

State of an unmirrored aggregate after a switchover:

| Type of switchover | MetroCluster FC state | MetroCluster IP state |
|---|---|---|
| Negotiated switchover (NSO) | Online | Offline (manual bring-online required) |
| Automatic unplanned switchover (AUSO) | Online | Offline (manual bring-online required) |
| Unplanned switchover (USO) | Online if storage available, else Offline | Offline (manual bring-online required) |

Note: In MetroCluster IP configurations, after switchover completes, you can manually bring unmirrored aggregates online.

Important: After a switchover, if the unmirrored aggregate is at the DR partner node and there is an ISL failure, that local node might fail. Also, if hybrid aggregates are used, performance degradation can occur after a SyncMirror plex has failed due to the SSD layer filling up.

### How NVRAM or NVMEM cache mirroring and dynamic mirroring work in MetroCluster configurations

Nonvolatile memory (NVRAM/NVMEM) in storage controllers is mirrored both locally to a local HA partner and remotely to a remote DR partner. This preserves nonvolatile cache data during local failover or switchover.

- In a non-MetroCluster HA pair: two cache partitions (self + HA partner).
- In a four-node MetroCluster configuration: cache divided into four partitions (local, HA partner, DR partner, DR auxiliary partner).
- In a two-node MetroCluster configuration: HA partner and DR auxiliary partitions are unused (controllers not configured as HA pair).

Partition contents:
- Local partition: data not yet written to disk.
- HA partner partition: copy of local cache of the storage controller's HA partner.
- DR partner partition: copy of local cache of the storage controller's DR partner (a node in the partner cluster paired with the local node).
- DR auxiliary partner partition: copy of local cache of the HA partner of the local node's DR partner (needed for HA takeover during normal operation or after a switchover).

#### Dynamic mirroring in event of a local HA takeover

If a local HA takeover occurs in a four-node configuration, the taken-over node can no longer mirror for its DR partner, so mirroring automatically switches to the DR auxiliary partner. After a successful giveback, mirroring automatically returns to the DR partner.

## Types of disasters and recovery methods

- **Single-node failure**: a single component in the local HA pair fails. In four-node configs, this may lead to automatic/negotiated takeover of the impaired node. In two-node configs, this leads to an automatic unplanned switchover (AUSO).
- **Site-wide controller failure**: all controller modules fail at a site (power loss, equipment replacement, disaster). Witness software (e.g., MetroCluster Tiebreaker) can differentiate failures from disasters. Can lead to automatic switchover if ISL links/switches are up and storage is accessible.
- **ISL failure**: links between sites fail. No MetroCluster action is taken; each node continues serving data normally, but mirrors are not written to respective DR sites.
- **Multiple sequential failures**: e.g., controller module, switch fabric, and shelf fail in sequence, resulting in storage failover, fabric redundancy, and SyncMirror sequentially protecting against downtime/data loss.

Note: AUSO is not supported on MetroCluster IP configurations.

Failure type / DR mechanism / recovery method summary:

| Failure type | Four-node DR mechanism | Two-node DR mechanism | Recovery method |
|---|---|---|---|
| Single-node failure | Local HA failover | AUSO | Four-node: not required if auto failover/giveback enabled. Two-node: after node restored, manual healing and switchback via `metrocluster heal -phase aggregates`, `metrocluster heal -phase root-aggregates`, `metrocluster switchback` (heal commands not required on MetroCluster IP 9.5+). |
| Site failure | MetroCluster switchover | MetroCluster switchover | After node restored, manual healing (`metrocluster healing`) and `metrocluster switchback` required (not required on MetroCluster IP 9.5+). |
| Site-wide controller failure | AUSO (only if disaster-site storage accessible) | AUSO (same as single-node failure) | — |
| Multiple sequential failures | Local HA failover, then MetroCluster forced switchover (`metrocluster switchover -forced-on-disaster`); forced switchover may not always be required | MetroCluster forced switchover (`metrocluster switchover -forced-on-disaster`) | — |
| ISL failure | No MetroCluster switchover; clusters serve data independently | Same | Not required; storage resynchronizes automatically once connectivity restored. |

## How an eight-node or four-node MetroCluster configuration provides nondisruptive operations

A single-node issue is handled by local HA failover/giveback without requiring switchover to the remote site. Each site can withstand local failures without a switchover, same as HA pairs in non-MetroCluster configurations. Node failures due to panic or power loss can cause an automatic switchover in four/eight-node configs.

If a second failure occurs after a local failover, MetroCluster switchover provides continued nondisruptive operations. Similarly, after a switchover, a second failure in a surviving node triggers a local failover, with the single surviving node serving data for all four nodes in the DR group.

### Switchover and switchback during MetroCluster transition

MetroCluster FC-to-IP transition involves adding MetroCluster IP nodes/switches to an existing FC configuration, then retiring the FC nodes. Switchover, healing, and switchback workflows differ depending on transition stage. See "Switchover, healing, and switchback operations during transition" in the ONTAP docs.

### Consequences of local failover after switchover

If a local failover occurs after a switchover, a single controller serves data for all storage systems in the MetroCluster configuration, risking resource issues and vulnerability to additional failures.

## How a two-node MetroCluster configuration provides nondisruptive operations

If one site has an issue due to panic, MetroCluster switchover provides continued nondisruptive operation. If power loss impacts both node and storage, switchover is not automatic — disruption occurs until `metrocluster switchover` is issued manually. Because all storage is mirrored, switchover provides nondisruptive resiliency similar to HA-pair storage failover. The same events that trigger automatic storage failover in an HA pair trigger AUSO in a two-node MetroCluster configuration — same level of protection as an HA pair.

## Overview of the switchover process

The MetroCluster switchover operation enables immediate resumption of services following a disaster by moving storage and client access from the source cluster to the remote site.

During switchover:
- Ownership of disks belonging to the disaster site changes to the DR partner (similar to local HA failover).
- Surviving plexes on the surviving site (belonging to disaster-cluster nodes) are brought online on the surviving cluster.
- The sync-source SVM belonging to the disaster site is brought down (negotiated switchover only).
- The sync-destination SVM belonging to the disaster site is brought up.
- Root aggregates of the DR partner are NOT brought online during switchover.

The `metrocluster switchover` command switches over nodes in all DR groups (e.g., both DR groups in an eight-node configuration).

Guidance: for a services-only switchover to the remote site, perform a negotiated switchover without fencing. If storage/equipment is unreliable, fence the disaster site first, then perform an unplanned switchover (fencing prevents RAID reconstructions from disks powering up in a staggered manner). This fencing procedure should only be used if the other site is stable and not intended to go offline.

### Availability of commands during switchover

| Command | Availability during switchover |
|---|---|
| `storage aggregate create` | Only for aggregates owned by a node in the surviving cluster |
| `storage aggregate delete` | Can delete a data aggregate |
| `storage aggregate mirror` | Can create a plex for a non-mirrored aggregate |
| `storage aggregate plex delete` | Can delete a plex for a mirrored aggregate |
| `vserver create` | Only if root volume resides in a data aggregate owned by the surviving cluster |
| `vserver delete` | Can delete both sync-source and sync-destination SVMs |
| `network interface create -lif` | Can create a data SVM LIF for both sync-source and sync-destination SVMs |
| `network interface delete -lif` | Can delete a data SVM LIF for both sync-source and sync-destination SVMs |
| `volume create` | Sync-source SVM: volume must reside in aggregate owned by surviving cluster. Sync-destination SVM: volume must reside in aggregate owned by disaster-site cluster |
| `volume delete` | Can delete a volume for both sync-source and sync-destination SVMs |
| `volume move` | Sync-source SVM: surviving cluster must own destination aggregate. Sync-destination SVM: disaster-site cluster must own destination aggregate |
| `snapmirror break` | Can break a SnapMirror relationship between source/destination endpoint of a data protection mirror |

### Differences in switchover between MetroCluster FC and IP configurations

In MetroCluster IP configurations, remote disks are accessed through remote DR partner nodes acting as iSCSI targets, so remote disks are not accessible once remote nodes are taken down during switchover. As a result:
- Mirrored aggregates owned by the local cluster become degraded.
- Mirrored aggregates switched over from the remote cluster become degraded.
- Note: when unmirrored aggregates are supported on MetroCluster IP, unmirrored aggregates not switched over from the remote cluster are not accessible.

### Disk ownership changes during HA takeover and MetroCluster switchover in a four-node configuration

A controller module's unique system ID (from NVRAM/NVMEM) identifies which node owns a specific disk. Ownership may temporarily change during HA/DR operations; the system tracks this via three fields: **Owner**, **Home owner**, **DR Home owner**.

A cluster-foreign aggregate (one taken over from the partner cluster during switchover) is identified by the DR Home owner field being populated, whereas a traditional foreign aggregate within an HA pair has differing Owner/Home owner values.

| Field | Normal operation | Local HA takeover | MetroCluster switchover | Takeover during switchover |
|---|---|---|---|---|
| Owner | ID of node with access | ID of HA partner (temporary) | ID of DR partner (temporary) | ID of DR auxiliary partner (temporary) |
| Home owner | Original owner within HA pair | Original owner within HA pair | ID of DR partner (Home owner in HA pair during switchover) | ID of DR partner (Home owner in HA pair during switchover) |
| DR Home owner | Empty | Empty | ID of original owner within MetroCluster configuration | ID of original owner within MetroCluster configuration |

Example progression for a disk in node_A_1's pool1 (physically located in cluster_B):

| MetroCluster state | Owner | Home owner | DR Home owner |
|---|---|---|---|
| Normal, all nodes operational | node_A_1 | node_A_1 | n/a |
| Local HA takeover (node_A_2 takes over node_A_1) | node_A_2 | node_A_1 | n/a |
| DR switchover (node_B_1 takes over from node_A_1) | node_B_1 | node_B_1 | node_A_1 |
| DR switchover + local HA takeover (node_B_2 takes over from node_B_1) | node_B_2 | node_B_1 | node_A_1 |
| After HA giveback and DR switchback | node_A_1 | node_A_1 | n/a |

### Considerations when using unmirrored aggregates

- **Maintenance requiring power shutdown**: manually take offline any unmirrored aggregates owned by the disaster site before negotiated switchover for site-wide power shutdown maintenance. Otherwise, nodes at the surviving site might go down due to multi-disk panics.
- **Hierarchical namespaces**: configure the junction path so volumes are either all on mirrored aggregates or all on unmirrored aggregates — mixing can prevent access to unmirrored aggregates after switchover.
- **CRS metadata volume and data SVM root volumes**: must be on a mirrored aggregate. If on an unmirrored aggregate, negotiated switchover/switchback are vetoed (`metrocluster check` warns of this).
- **SVMs**: configure on mirrored-only or unmirrored-only aggregates. Mixing can cause switchover to exceed 120 seconds and result in a data outage if unmirrored aggregates don't come online.
- **SAN**: a LUN should not be located on an unmirrored aggregate — doing so can cause switchover to exceed 120 seconds and a data outage.

### Automatic unplanned switchover (AUSO) in MetroCluster FC configurations

AUSO can be triggered in a site-wide controller failure to provide nondisruptive operations (not supported in MetroCluster IP). Triggered if all nodes at a site fail due to power down, power loss, or panic. In an eight-node MetroCluster FC configuration, you can set an option to trigger AUSO if both nodes in an HA pair fail.

For two-node MetroCluster configurations (no local HA failover available), AUSO provides continued operation after: node power down, power loss, panic, or reboot. Disk ownership for the impaired node's pool0/pool1 disks changes to the DR partner, preventing aggregates from going degraded. After AUSO, you must manually proceed through healing and switchback.

**Hardware-assisted AUSO**: in two-node configs, the controller module's service processor (SP) monitors the configuration and can detect failure faster than ONTAP software, triggering AUSO. Automatically enabled; SP sends/receives SNMP traffic to/from its DR partner.

**Changing the AUSO setting (MetroCluster FC only)**: default is `auso-on-cluster-disaster` (view via `metrocluster show`). Disable with `metrocluster modify -auto-switchover-failure-domain auto-disabled` (run on both sites to disable everywhere). Re-enable with `metrocluster modify -auto-switchover-failure-domain auso-on-cluster-disaster`. Advanced setting `auso-on-dr-group-disaster` triggers AUSO on HA failover at one site (run on both sites).

During switchover, the AUSO setting is internally disabled (a site already in switchover cannot auto-switch over again).

Recovering from AUSO uses the same steps as a planned switchover.

**Mediator-assisted AUSO in MetroCluster IP**: see "How the ONTAP Mediator supports automatic unplanned switchover in MetroCluster IP configurations."

## What happens during healing (MetroCluster FC configurations)

Healing resynchronizes mirrored aggregates in a phased process preparing repaired disaster-site nodes for switchback. It's planned, giving full control to minimize downtime. Two-step process: storage and controller.

**Data aggregate healing**: checks all nodes up at surviving site; changes ownership of all pool 0 disks at the disaster site (including root aggregates). RAID subsystem resynchronizes mirrored aggregates; WAFL replays nvsave files for mirrored aggregates with a failed pool 1 plex at switchover time. Errors reported at Storage, Sanown, or RAID levels if source storage components failed. Can take hours to complete.

**Root aggregate healing**: after aggregates sync, give back CFO aggregates and root aggregates to their respective DR partners.

## What happens during healing (MetroCluster IP configurations)

Same phased, two-step healing process as FC, with one key difference: **you must boot the nodes in the disaster site cluster before the healing operation**, since remote iSCSI disks must be accessible for aggregate resynchronization. If disaster-site nodes aren't running, healing fails (disk ownership changes can't be performed).

Data aggregate healing and root aggregate healing steps are otherwise the same as MetroCluster FC.

## Automatic healing of aggregates on MetroCluster IP configurations after switchover

Beginning with ONTAP 9.5, healing is automated during negotiated switchover on MetroCluster IP. Beginning with ONTAP 9.6, automated healing after unscheduled switchover is also supported, removing the need to issue `metrocluster heal` commands manually.

**Automatic healing after negotiated switchover (ONTAP 9.5+)**: disaster-site nodes remain up (not serving data, in switchover state) and move to "Waiting for switchback" state (confirm via `metrocluster operation show`). You can switch back without issuing healing commands. Applies to MetroCluster IP only, not FC. Manual healing still required on MetroCluster IP 9.4 and earlier.

**Automatic healing after unscheduled switchover (ONTAP 9.6+)**: an unscheduled switchover uses `switchover -forced-on-disaster true`. Not supported on MetroCluster FC; manual healing still required on MetroCluster IP 9.5 and earlier for unscheduled switchover. On ONTAP 9.6+: disaster-site nodes may be down; once booted (or if they remained up), they move to "Waiting for switchback" state; healing operations are performed automatically. Confirm status via `metrocluster operation show`.

**If automatic healing fails**: issue `metrocluster heal` commands manually (as in pre-9.6 versions). Use `metrocluster operation show` and `metrocluster operation history show -instance` to monitor healing status and diagnose failure causes.

## Creating SVMs for a MetroCluster configuration

Requirements:
- Both clusters must be in a MetroCluster configuration.
- Aggregates must be available and online in both clusters.
- IPspaces with matching names must exist on both clusters if required.
- If a cluster is rebooted without a switchover, sync-source SVMs might come online as "stopped" instead of "started".

When you create an SVM on one cluster, it's created as the source SVM, and a partner SVM is automatically created with the same name plus "-mc" suffix on the partner cluster (applied before the first period if the name contains one). A MetroCluster configuration supports up to 64 SVMs per cluster, 128 total.

Example:
```
cluster_A::>vserver create -vserver vs4 -rootvolume vs4_root -aggregate aggr1 -rootvolume-security-style mixed
[Job 196] Job succeeded: Vserver creation completed
```
This creates SVM "vs4" locally and "vs4-mc" on the partner site.

Verify with `metrocluster vserver show`:
```
cluster_A::> metrocluster vserver show

        Partner    Configuration
Cluster     Vserver   Vserver    State
---------  --------  --------- -----------------
cluster_A   vs4       vs4-mc     healthy
cluster_B   vs1       vs1-mc     healthy
```

Verify SVM state with `vserver show`:
```
cluster_A::> vserver show

        Admin   Operational Root
Vserver Type  Subtype        State   State       Volume     Aggregate
------- ----- -------       ------- --------    ----------- ----------
vs4     data  sync-source   running   running    vs4_root   aggr1

cluster_B::> vserver show

        Admin   Operational  Root
Vserver Type  Subtype          State   State        Volume      Aggregate
------- ----- -------          ------  ---------    ----------- ----------
vs4-mc  data  sync-destination running stopped      vs4_root    aggr1
```

SVM creation might fail if intermediate operations (e.g., root volume creation) fail, leaving the SVM in "initializing" state — you must delete and re-create it. MetroCluster SVMs are created with a 1 GB root volume; sync-source SVM is "running", sync-destination SVM is "stopped".

## What happens during a switchback

After the disaster site has recovered and aggregates have healed, the MetroCluster switchback process returns storage and client access from the DR site to the home cluster.

The `metrocluster switchback` command returns the primary site to full, normal MetroCluster operation. Configuration changes are propagated to the original SVMs. Data server operation returns to the sync-source SVMs on the disaster site, and the sync-destination SVMs that had been operating on the surviving site are deactivated.

If SVMs were deleted on the surviving site while in switchover state, switchback also:
- Deletes the corresponding SVMs on the partner site (former disaster site).
- Deletes any peering relationships of the deleted SVMs.
