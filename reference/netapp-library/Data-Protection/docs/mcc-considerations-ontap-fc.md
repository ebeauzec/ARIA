# Considerations when using ONTAP in a MetroCluster configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/concept_considerations_when_using_ontap_in_a_mcc_configuration.html
Fetched: 2026-07-07

When using ONTAP in a MetroCluster configuration, you should be aware of certain considerations for licensing, peering to clusters outside the MetroCluster configuration, performing volume operations, NVFAIL operations, and other ONTAP operations.

## Licensing considerations
- Both sites should be licensed for the same site-licensed features.
- All nodes should be licensed for the same node-locked features.

## SnapMirror consideration
- SnapMirror SVM disaster recovery is only supported on MetroCluster configurations running ONTAP 9.5 or later.

## FlexCache support in a MetroCluster configuration

Beginning with ONTAP 9.7, FlexCache volumes are supported on MetroCluster configurations. Be aware of requirements for manual repeering after switchover or switchback operations.

### SVM repeering after switchover when FlexCache origin and cache are within the same MetroCluster site

After a negotiated or unplanned switchover, any SVM FlexCache peering relationship within the cluster must be manually configured.

Example: SVMs "vs1" (cache) and "vs2" (origin) are on site_A and peered. After switchover, "vs1-mc" and "vs2-mc" are activated at site_B and must be manually repeered using `vserver peer repeer`.

### SVM repeering after switchover or switchback when a FlexCache destination is on a third cluster and in disconnected mode

For FlexCache relationships to a cluster outside the MetroCluster configuration, peering must always be manually reconfigured after a switchover if the involved clusters are in disconnected mode during switchover.

Example: cache_1 (on vs1) resides on MetroCluster site_A; origin_1 (on vs2) resides on site_C (outside MetroCluster). If switchover is triggered and site_A/site_C are not connected, manually repeer SVMs on site_B (switchover cluster) and site_C via `vserver peer repeer` after switchover. When switchback occurs, repeer SVMs on site_A and site_C again.

Related: [FlexCache volumes management with the CLI](https://docs.netapp.com/us-en/ontap/flexcache/index.html)

## FabricPool support in MetroCluster configurations

Beginning with ONTAP 9.7, MetroCluster configurations support FabricPool storage tiers.

### Considerations when using FabricPools
- Clusters must have FabricPool licenses with matching capacity limits.
- Clusters must have IPspaces with matching names (default or admin-created) used for FabricPool object store configuration.
- For the selected IPspace, each cluster must have an intercluster LIF that can reach the external object store.
- SVM migration isn't supported with FabricPool when the source or destination is a MetroCluster cluster.

### Configuring an aggregate for use in a mirrored FabricPool

Note: object stores must be set up first (see "Set up object stores for FabricPool in a MetroCluster configuration").

1. Create the aggregate or select an existing aggregate.
2. Mirror the aggregate as a typical mirrored aggregate within the MetroCluster configuration.
3. Create the FabricPool mirror with the aggregate:
   a. Attach a primary object store (physically closer to the cluster).
   b. Add a mirror object store (physically further from the cluster than the primary).

Note: maintain at least 20% free space for mirrored aggregates for optimal performance/availability (vs. 10% recommended for non-mirrored aggregates) due to ONTAP's copy-on-write Snapshot-based architecture increasing space utilization for mirrored aggregates.

## FlexGroup support in MetroCluster configurations

Beginning with ONTAP 9.6, MetroCluster configurations support FlexGroup volumes.

## Consistency group support in MetroCluster configurations

Beginning with ONTAP 9.11.1, consistency groups are supported in MetroCluster configurations.

## Job schedules in a MetroCluster configuration

In ONTAP 9.3 and later, user-created job schedules are automatically replicated between clusters via the Configuration Replication Service (CRS). Creating, modifying, or deleting a schedule on one cluster automatically applies the same change to the partner cluster.

Note: System-created schedules are NOT replicated — you must manually replicate them on the partner cluster.

## Cluster peering from the MetroCluster site to a third cluster

Peering configuration is not replicated. If you peer one MetroCluster cluster to a third cluster, you must also configure the same peering on the partner MetroCluster cluster so peering is maintained after a switchover. The non-MetroCluster cluster must run ONTAP 8.3 or later, otherwise peering is lost on switchover even if configured on both partners.

## LDAP client configuration replication in a MetroCluster configuration

An LDAP client configuration created on an SVM on a local cluster is replicated to its partner data SVM on the remote cluster (e.g., admin SVM config replicates to all admin data SVMs on the remote cluster), so the LDAP client configuration remains active on all partner SVMs.

## Networking and LIF creation guidelines for MetroCluster configurations

### IPspace object replication and subnet configuration requirements

**IPspace replication:**
- IPspace names of the two sites must match.
- IPspace objects must be manually replicated to the partner cluster. SVMs created and assigned to an IPspace before it's replicated will NOT be replicated to the partner.

**Subnet configuration:**
- Both clusters must have a subnet in the same IPspace with the same subnet name, subnet, broadcast domain, and gateway.
- The IP ranges of the two clusters must be different, e.g.:
```
cluster_A::> network subnet show
    IPspace: Default
Subnet                     Broadcast                   Avail/
Name      Subnet           Domain    Gateway           Total    Ranges
--------- ---------------- --------- ------------      -------  ---------------
subnet1   192.168.2.0/24   Default   192.168.2.1       10/10    192.168.2.11-192.168.2.20

cluster_B::> network subnet show
 IPspace: Default
Subnet                     Broadcast                   Avail/
Name      Subnet           Domain    Gateway           Total    Ranges
--------- ---------------- --------- ------------     --------  ---------------
subnet1   192.168.2.0/24   Default   192.168.2.1       10/10    192.168.2.21-192.168.2.30
```

**IPv6 configuration:** If IPv6 is configured on one site, it must be configured on the other site as well.

### Requirements for LIF creation in a MetroCluster configuration

- **Fibre Channel:** must use stretched VSAN or stretched fabrics.
- **IP/iSCSI:** must use a layer 2 stretched network.
- **ARP broadcasts:** must be enabled between the two clusters.
- **Duplicate LIFs:** do not create multiple LIFs with the same IP address in an IPspace.
- **NFS and SAN configurations:** use different SVMs for unmirrored and mirrored aggregates.
- Create a subnet object before creating a LIF — enables ONTAP to determine failover targets via associated broadcast domain.

**Verify LIF creation:** use `metrocluster check lif show`; fix issues with `metrocluster check lif repair-placement`.

### LIF replication and placement requirements and issues

When a LIF is created on a cluster in a MetroCluster configuration, it is replicated on the partner cluster (not on a one-to-one name basis — placement verifies ports can host the LIF based on reachability and port attribute checks).

Placement conditions by LIF type:

| Condition | FC | IP/iSCSI |
|---|---|---|
| Node identification | Placed on DR partner of the creating node; DR auxiliary partner used if DR partner unavailable | Same as FC |
| Port identification | ONTAP identifies connected FC target ports on DR cluster | Ports on DR cluster in the same IPspace as source LIF selected for reachability check; if none exist, LIF cannot be placed; ports already hosting a LIF in same IPspace/subnet are auto-marked reachable |
| Reachability check | Checks connectivity of source fabric WWN on DR cluster ports; if fabric absent at DR site, LIF placed on random port on DR partner | Determined by ARP broadcast response from DR cluster ports to source LIF's IP; requires ARP broadcasts allowed between clusters |
| Port selection | Categorized by adapter type/speed; matching-attribute ports selected, else random connected port | Prefers ports in broadcast domain associated with the LIF's subnet; falls back to reachable ports, then broadcast-domain ports, then random; further filtered by adapter type/interface type/speed |
| LIF placement | Least loaded reachable port selected | Least loaded selected port chosen |

**Placement when DR partner node is down:** replicated LIF placed on DR auxiliary partner node; after giveback, LIFs are NOT automatically moved back to the DR partner, potentially concentrating LIFs on a single node — this can cause LUN mapping failures for the SVM during a subsequent MetroCluster switchover. Run `metrocluster check lif show` after takeover/giveback to verify placement; use `metrocluster check lif repair-placement` to fix.

**LIF placement errors:** retained after switchover; cleared automatically if `network interface modify/rename/delete` is run against the affected LIF.

**LIF replication failure:** check via `metrocluster check lif show` (an EMS message is generated on failure); fix with `metrocluster check lif repair-placement`. Resolve promptly to ensure LIF availability during switchover. Note: even if the source SVM is down, LIF placement might proceed normally if a LIF belonging to a different SVM exists on a port with the same IPspace/network in the destination SVM.

**LIFs inaccessible after a switchover:** changes to the FC switch fabric connecting source/DR target ports can make DR-placed FC LIFs inaccessible to hosts post-switchover. Run `metrocluster check lif repair-placement` on both source and DR nodes after fabric changes to verify host connectivity.

### Volume creation on a root aggregate

New volumes cannot be created on the root aggregate (HA policy of CFO) of a MetroCluster node; root aggregates cannot be added to an SVM via `vserver add-aggregates`.

## SVM disaster recovery in a MetroCluster configuration

Beginning with ONTAP 9.5, active SVMs in a MetroCluster configuration can be sources for the SnapMirror SVM disaster recovery feature (destination SVM must be on a third cluster outside the MetroCluster configuration). Beginning with ONTAP 9.11.1, both sites within a MetroCluster configuration can be the source for an SVM DR relationship with a FAS or AFF destination cluster.

Requirements/limitations:
- Only an active SVM within the MetroCluster configuration can be the source of an SVM DR relationship (sync-source before switchover, or sync-destination after switchover).
- In steady state, the MetroCluster sync-destination SVM cannot be the source of an SVM DR relationship (volumes not online).
- When the sync-source SVM is the source of an SVM DR relationship, that relationship info is replicated to the MetroCluster partner, allowing SVM DR updates to continue after switchover.
- During switchover/switchback, replication to the SVM DR destination might fail temporarily, but the next scheduled SVM DR update after completion will succeed.

See "Replicating the SVM configuration" in Data Protection with the CLI for configuring SVM DR relationships.

### SVM resynchronization at a disaster recovery site

During resynchronization, the SVM DR source on the MetroCluster configuration is restored from the destination SVM on the non-MetroCluster site; the source SVM (cluster_A) temporarily acts as a destination SVM.

**If an unplanned switchover occurs during resynchronization:**
- Resynchronization transfer halts.
- The destination SVM on the MetroCluster site (previously the source SVM) remains a destination SVM; the partner-cluster SVM retains its subtype and stays inactive.
- The SnapMirror relationship must be re-created manually with the sync-destination SVM as the destination.
- The relationship does not appear in SnapMirror show output after switchover at the survivor site unless a SnapMirror create operation is executed.

**Performing switchback after an unplanned switchover during resynchronization:** the resynchronization relationship must be broken and deleted first. Switchback is not permitted if any SnapMirror DR destination SVMs exist in the MetroCluster configuration, or if the cluster has an SVM of subtype "dp-destination".

## Output for "storage aggregate plex show" is indeterminate after a MetroCluster switchover

After a switchover, plex0 of the switched-over root aggregate shows status "failed" (indeterminate) until the MetroCluster healing phase determines the actual status.

## Modifying volumes to set the NVFAIL flag in case of switchover

You can set the NVFAIL flag on a volume so it is fenced off from modification if a MetroCluster switchover occurs — used for volumes where committed writes must be treated as lost after switchover.

Note: ONTAP versions before 9.0 use the NVFAIL flag for every switchover; ONTAP 9.0+ uses unplanned switchover (USO) instead.

Command: `vol modify -vserver vserver-name -volume volume-name -dr-force-nvfail on`
