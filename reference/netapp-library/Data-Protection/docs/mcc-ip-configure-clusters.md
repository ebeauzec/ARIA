# Configure ONTAP clusters in a MetroCluster IP configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/task_sw_config_configure_clusters.html
Fetched: 2026-07-07

You must peer the clusters, mirror the root aggregates, create a mirrored data aggregate, and then issue the command to implement the MetroCluster operations.

**About this task:** Before you run `metrocluster configure`, HA mode and DR mirroring are not enabled and you might see an error message related to this expected behavior. You enable HA mode and DR mirroring later when you run `metrocluster configure` to implement the configuration.

## Disabling automatic drive assignment (if doing manual assignment in ONTAP 9.4)

In ONTAP 9.4, if your MetroCluster IP configuration has fewer than four external storage shelves per site, you must disable automatic drive assignment on all nodes and manually assign drives.

Not required in ONTAP 9.5 and later. Does not apply to an AFF A800 system with an internal shelf and no external shelves. See "Considerations for automatic drive assignment and ADP systems in ONTAP 9.4 and later."

Steps:
1. Disable automatic drive assignment: `storage disk option modify -node <node_name> -autoassign off`
2. Issue this command on all nodes in the MetroCluster IP configuration.

## Verifying drive assignment of pool 0 drives

Verify that the remote drives are visible to the nodes and have been assigned correctly. Automatic assignment depends on the storage system platform model and drive shelf arrangement.

Steps:
1. Verify pool 0 drives are assigned automatically: `disk show`

Example (`cluster_A`, AFF A800, no external shelves): drive autoassignment gives one quarter (8 drives) to node_A_1 and one quarter to node_A_2; remaining drives become remote (pool 1) drives for node_B_1 and node_B_2:
```
cluster_A::*> disk show
                 Usable     Disk      Container           Container
Disk             Size       Shelf Bay Type    Type        Name      Owner
---------------- ---------- ----- --- ------- ----------- --------- --------
node_A_1:0n.12   1.75TB     0     12  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.13   1.75TB     0     13  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.14   1.75TB     0     14  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.15   1.75TB     0     15  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.16   1.75TB     0     16  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.17   1.75TB     0     17  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.18   1.75TB     0     18  SSD-NVM shared      aggr0     node_A_1
node_A_1:0n.19   1.75TB     0     19  SSD-NVM shared      -         node_A_1
node_A_2:0n.0    1.75TB     0     0   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.1    1.75TB     0     1   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.2    1.75TB     0     2   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.3    1.75TB     0     3   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.4    1.75TB     0     4   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.5    1.75TB     0     5   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.6    1.75TB     0     6   SSD-NVM shared      aggr0_node_A_2_0 node_A_2
node_A_2:0n.7    1.75TB     0     7   SSD-NVM shared      -         node_A_2
node_A_2:0n.24   -          0     24  SSD-NVM unassigned  -         -
[... additional unassigned bays 25-31, 36-43 ...]
32 entries were displayed.
```
(cluster_B shows the mirror-image assignment for node_B_1 / node_B_2.)

## Peering the clusters

The clusters must be in a peer relationship to communicate and perform the data mirroring essential to MetroCluster disaster recovery. See "Cluster and SVM peering express configuration," "Considerations when using dedicated ports," and "Considerations when sharing data ports."

## Configuring intercluster LIFs for cluster peering

Create intercluster LIFs on ports used for communication between MetroCluster partner clusters — either dedicated ports or ports that also carry data traffic.

### Configuring intercluster LIFs on dedicated ports

Increases available bandwidth for replication traffic.

1. List ports: `network port show`
2. Determine available ports for intercluster communication: `network interface show -fields home-port,curr-port`
3. Create a failover group for dedicated ports:
   `network interface failover-groups create -vserver <system_svm> -failover-group <failover_group> -targets <physical_or_logical_ports>`
   Example: `network interface failover-groups create -vserver cluster01 -failover-group intercluster01 -targets cluster01-01:e0e,cluster01-01:e0f,cluster01-02:e0e,cluster01-02:e0f`
4. Verify: `network interface failover-groups show`
5. Create intercluster LIFs on the system SVM, assigned to the failover group:
   - ONTAP 9.6+: `network interface create -vserver <system_svm> -lif <lif_name> -service-policy default-intercluster -home-node <node_name> -home-port <port_name> -address <port_ip_address> -netmask <netmask_address> -failover-group <failover_group>`
   - ONTAP 9.5 and earlier: same but `-role intercluster` instead of `-service-policy default-intercluster`
   Example:
   ```
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl01 -service-policy default-intercluster -home-node cluster01-01 -home-port e0e -address 192.168.1.201 -netmask 255.255.255.0 -failover-group intercluster01
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl02 -service-policy default-intercluster -home-node cluster01-02 -home-port e0e -address 192.168.1.202 -netmask 255.255.255.0 -failover-group intercluster01
   ```
6. Verify LIFs created: `network interface show -service-policy default-intercluster` (9.6+) or `-role intercluster` (9.5 and earlier)
7. Verify LIFs are redundant: `network interface show -service-policy default-intercluster -failover` (9.6+) or `-role intercluster -failover` (9.5 and earlier) — confirms failover targets (e.g., e0e fails over to e0f).

### Configuring intercluster LIFs on shared data ports

Reduces the number of ports needed for intercluster networking.

1. List ports: `network port show`
2. Create intercluster LIFs on the system SVM:
   - ONTAP 9.6+: `network interface create -vserver <system_svm> -lif <lif_name> -service-policy default-intercluster -home-node <node_name> -home-port <port_name> -address <port_ip_address> -netmask <netmask>`
   - ONTAP 9.5 and earlier: `-role intercluster` instead
   Example: creates `cluster01_icl01` on e0c (192.168.1.201) and `cluster01_icl02` on e0c (192.168.1.202).
3. Verify: `network interface show -service-policy default-intercluster` (or `-role intercluster`)
4. Verify redundancy: `network interface show -service-policy default-intercluster -failover` — shows failover from e0c to e0d.

## Creating a cluster peer relationship

Use `cluster peer create` to create a peer relationship between local and remote clusters, then authenticate on the remote cluster.

Requirements: intercluster LIFs created on every node in both clusters; clusters running ONTAP 9.3 or later.

1. On the destination cluster: `cluster peer create -generate-passphrase -offer-expiration <MM/DD/YYYY HH:MM:SS|1…7days|1…168hours> -peer-addrs <peer_lif_ip_addresses> -ipspace <ipspace>` (omit `-ipspace` if not using a custom IPspace). Note the generated passphrase — it cannot be displayed again.
2. On the source cluster: `cluster peer create -peer-addrs <peer_lif_ip_addresses> -ipspace <ipspace>`, then enter/confirm the passphrase when prompted.
3. Verify: `cluster peer show -instance`
4. Check connectivity/status: `cluster peer health show`

## Creating the DR group

Create the disaster recovery (DR) group relationships between the clusters. Performed once, on one cluster. **DR relationships cannot be changed after DR groups are created.**

1. Verify nodes are ready: `metrocluster configuration-settings show-status` (should show "ready for DR group create" for each node).
2. Create the DR group: `metrocluster configuration-settings dr-group create -partner-cluster <partner_cluster_name> -local-node <local_node_name> -remote-node <remote_node_name>`
   Issued once (not repeated on the partner cluster). Example creates DR pairs node_A_1↔node_B_1 and (implicitly) node_A_2↔node_B_2:
   ```
   Cluster_A::> metrocluster configuration-settings dr-group create -partner-cluster cluster_B -local-node node_A_1 -remote-node node_B_1
   [Job 27] Job succeeded: DR Group Create is successful.
   ```

## Configuring and connecting the MetroCluster IP interfaces

Configure MetroCluster IP interfaces used for replication of each node's storage and nonvolatile cache, then establish iSCSI connections for storage replication.

Note: MetroCluster IP and connected switch ports do not come online until after interfaces are created.

Requirements:
- Two interfaces per node, associated with VLANs defined in the MetroCluster RCF file.
- All "A" ports in one VLAN, all "B" ports in the other VLAN.
- Beginning with ONTAP 9.9.1, layer 3 configurations require the `-gateway` parameter.
- Default VLANs are 10 (A) and 20 (B) on platforms supporting `-vlan-id`; you may specify VLAN 101-4095 instead via `-vlan-id`.
- Platforms that do NOT support `-vlan-id`: FAS8200, AFF A300, AFF A320, FAS9000, AFF A700, AFF C800, ASA C800, AFF A800, ASA A800. All other platforms support it.
- Physical ports depend on platform model — see "Cable the MetroCluster IP switches."

Caution: do not use 169.254.17.x or 169.254.18.x IP addresses for MetroCluster IP interfaces (conflicts with system auto-generated interface IPs).

Example IP plan:
| Node | Interface | IP address | Subnet |
|---|---|---|---|
| node_A_1 | MetroCluster IP interface 1 | 10.1.1.1 | 10.1.1/24 |
| node_A_1 | MetroCluster IP interface 2 | 10.1.2.1 | 10.1.2/24 |
| node_A_2 | MetroCluster IP interface 1 | 10.1.1.2 | 10.1.1/24 |
| node_A_2 | MetroCluster IP interface 2 | 10.1.2.2 | 10.1.2/24 |
| node_B_1 | MetroCluster IP interface 1 | 10.1.1.3 | 10.1.1/24 |
| node_B_1 | MetroCluster IP interface 2 | 10.1.2.3 | 10.1.2/24 |
| node_B_2 | MetroCluster IP interface 1 | 10.1.1.4 | 10.1.1/24 |
| node_B_2 | MetroCluster IP interface 2 | 10.1.2.4 | 10.1.2/24 |

Steps:
1. Confirm disk automatic assignment is enabled on each node: `storage disk option show` (check "Auto Assign" column).
2. Verify nodes are ready to create MetroCluster IP interfaces: `metrocluster configuration-settings show-status` (should show "ready for interface create").
3. Create interfaces on node_A_1 (ports e5a and e5b for an AFF A700/FAS9000 example):
   `metrocluster configuration-settings interface create -cluster-name <cluster_name> -home-node <node_name> -home-port e5a -address <ip_address> -netmask <netmask>`
   Example: `metrocluster configuration-settings interface create -cluster-name cluster_A -home-node node_A_1 -home-port e5a -address 10.1.1.1 -netmask 255.255.255.0`
   For platforms supporting VLANs (e.g., AFF A220), add `-vlan-id <id>`, e.g., `-vlan-id 120`.
   Repeat for e5b (10.1.2.1).
4. Repeat for node_A_2 (e5a: 10.1.1.2, e5b: 10.1.2.2; VLAN example uses `-vlan-id 220`).
5. Repeat for node_B_1 (e5a: 10.1.1.3, e5b: 10.1.2.3).
6. Repeat for node_B_2 (e5a: 10.1.1.4, e5b: 10.1.2.4).
7. Verify interfaces configured: `metrocluster configuration-settings interface show` (Config State should show "completed" for all 8 entries in a four-node config).
8. Verify nodes ready to connect: `metrocluster configuration-settings show-status` (should show "ready for connection connect").
9. Establish connections: `metrocluster configuration-settings connection connect`
   Note: on ONTAP versions earlier than 9.10.1, IP addresses cannot be changed after issuing this command.
10. Verify connections established: `metrocluster configuration-settings show-status` (status "completed" for all nodes).
11. Verify iSCSI connections:
    a. `set -privilege advanced` (confirm with `y`)
    b. `storage iscsi-initiator show` — ONTAP 9.5 shows eight MetroCluster IP initiators per cluster (dr_auxiliary and dr_partner types); ONTAP 9.4 and earlier show four.
    c. `set -privilege admin`
12. Verify nodes ready for final implementation: `metrocluster node show` (Configuration State should show "ready to configure").

## Verifying or manually performing pool 1 drives assignment

Procedure depends on configuration and ONTAP version:

| Configuration type | Procedure |
|---|---|
| Meets automatic drive assignment requirements, or ONTAP 9.3 factory-shipped | Verify disk assignment for pool 1 disks |
| Three shelves, or uneven multiple of four shelves (e.g., seven), running ONTAP 9.5 | Manually assign drives for pool 1 (ONTAP 9.4+) |
| Fewer than four storage shelves per site, running ONTAP 9.4 | Manually assign drives for pool 1 (ONTAP 9.4+) |
| Not factory-shipped, running ONTAP 9.3 | Manually assign disks for pool 1 (ONTAP 9.3) |

### Verifying disk assignment for pool 1 disks

Wait at least 10 minutes for disk auto-assignment to complete after `metrocluster configuration-settings connection connect`. Disk names appear as `node-name:0m.i1.0L1`. Use `disk show` (optionally with `-host-adapter 0m -owner <node>`) to confirm remote pool 1 disks were correctly auto-assigned to each node — cross-site ownership should be visible (e.g., node_B_1's disk show output lists disks owned by node_A_1 and node_A_2 as remote pool 1 members, and vice versa).

### Manually assigning drives for pool 1 (ONTAP 9.4 or later)

Applies when the system was not factory pre-configured and doesn't meet automatic assignment requirements. See "Considerations for automatic drive assignment and ADP systems in ONTAP 9.4 and later." With only two external shelves per site, pool 1 drives per node should share the same remote shelf (e.g., node_A_1 gets bays 0-11 on site_B-shelf_2; node_A_2 gets bays 12-23 on the same shelf).

Steps (repeat on each node in the MetroCluster IP configuration):
1. Display unassigned drives: `disk show -host-adapter 0m -container-type unassigned`
2. Assign remote drives (0m) to pool 1 of the node: `disk assign -disk <disk-id> -pool 1 -owner <owner_node_name>` (disk-id must identify a drive on a remote shelf of owner_node_name)
3. Confirm assignment: re-run `disk show -host-adapter 0m -container-type unassigned` — assigned drives no longer appear. (iSCSI connection to remote drives shows as device 0m.)
4. Repeat for the second node on site A.
5. Repeat on site B.

### Manually assigning disks for pool 1 (ONTAP 9.3)

With at least two disk shelves per node, ONTAP auto-assigns remaining disks on a shelf once you "seed" one disk per shelf. Example: all disks on site_B-shelf_2 auto-assign to pool1 of node_A_1; site_B-shelf_4 to node_A_2; site_A-shelf_2 to node_B_1; site_A-shelf_4 to node_B_2.

Steps (repeat on each node):
1. Display unassigned disks: `disk show -host-adapter 0m -container-type unassigned`
2. Assign one remote disk (0m) to pool 1 of the node: `disk assign -disk <disk_id> -pool 1 -owner <owner_node_name>` — auto-assignment then applies to the rest of that shelf.
3. Wait at least 60 seconds, then verify: `disk show -host-adapter 0m -container-type unassigned` (assigned shelf's disks no longer listed; iSCSI connection shows as device 0m).
4. Repeat for the second node on site A.
5. Repeat on site B.

## Enabling automatic drive assignment in ONTAP 9.4

If you disabled automatic drive assignment earlier in this procedure, re-enable it on all nodes:
`storage disk option modify -node <node_name> -autoassign on`

## Mirroring the root aggregates

Mirror root aggregates to provide data protection. By default the root aggregate is RAID-DP; you can change it to RAID4:
`storage aggregate modify –aggregate <aggr_name> -raidtype raid4`
(On non-ADP systems, RAID type can be changed before or after mirroring.)

Steps:
1. Mirror the root aggregate: `storage aggregate mirror <aggr_name>`
   Example: `controller_A_1::> storage aggregate mirror aggr0_controller_A_1` — creates a local plex and a remote plex at the MetroCluster partner site.
2. Repeat for each node in the MetroCluster configuration.

## Creating a mirrored data aggregate on each node

Create a mirrored data aggregate on each node in the DR group.

Considerations:
- Know which drives will be used; for heterogeneous storage, ensure correct drive type selection.
- All drives in an aggregate must be owned by the same node (the home node). ADP systems partition each drive into P1/P2/P3.
- Aggregate names must follow your planned naming scheme and must be unique across MetroCluster sites (cannot reuse a name between site A and site B).

Steps:
1. List available spares: `storage disk show -spare -owner <node_name>`
2. Create the aggregate: `storage aggregate create -mirror true`
   - Can be created on any node from the cluster management interface; use `-node` or specify owned drives to target a specific node.
   - Options include: home node, specific drive list, drive count, checksum style, drive type/size/speed, RAID type, max drives per RAID group, mixed-RPM allowance.
   - Note: in minimum supported configurations with limited drives, use `-force-small-aggregate` to allow a three-disk RAID-DP aggregate.
   Example: `cluster_A::> storage aggregate create aggr1_node_A_1 -diskcount 10 -node node_A_1 -mirror true`
3. Verify RAID group/drives: `storage aggregate show-status -aggregate <aggregate-name>`

## Implementing the MetroCluster configuration

Run `metrocluster configure` to start data protection.

Requirements:
- At least two non-root mirrored data aggregates per cluster (verify with `storage aggregate show`); if using a single mirrored data aggregate, use the alternate step below.
- The ha-config state of controllers/chassis must be "mccip".
- Issue the command once, on any node — not needed on each site/node.
- `metrocluster configure` automatically pairs the two lowest-system-ID nodes in each cluster as DR partners; in a four-node config, the second DR pair forms from the two higher-system-ID nodes.
- **Do not** configure Onboard Key Manager (OKM) or external key management before running `metrocluster configure`.

Steps:
1. Configure MetroCluster:
   - Multiple data aggregates: `metrocluster configure <node_name>`
   - Single mirrored data aggregate: `set -privilege advanced` (confirm `y`) → `metrocluster configure -allow-with-one-aggregate true <node_name>` → `set -privilege admin`
   Best practice: use multiple data aggregates. If the first DR group has only one aggregate and you want to add a DR group with one aggregate, you must move the metadata volume off the single data aggregate (see "Moving a metadata volume in MetroCluster configurations").
   Example: `cluster_A::*> metrocluster configure -node-name controller_A_1` → `[Job 121] Job succeeded: Configure is successful.`
2. Verify networking status on site A: `network port show` (MTU 9000 shown on cluster ports in the four-node example).
3. Verify MetroCluster configuration from both sites: `metrocluster show` on cluster_A and cluster_B — both should show Configuration state "configured" and Mode "normal" for local and remote.
4. To avoid nonvolatile memory mirroring issues, reboot each of the four nodes: `node reboot -node <node_name> -inhibit-takeover true`
5. Re-verify configuration with `metrocluster show` on both clusters.

## Configuring the second DR group in an eight-node configuration

Repeat the previous tasks (DR group creation, IP interface configuration, aggregate mirroring, MetroCluster configure) for the nodes in the second DR group.

## Creating unmirrored data aggregates

Optional, for data not requiring MetroCluster's redundant mirroring.

Important: in MetroCluster IP configurations, remote unmirrored aggregates are NOT accessible after a switchover. Unmirrored aggregates must be local to the node owning them.

Steps:
1. Enable unmirrored aggregate deployment: `metrocluster modify -enable-unmirrored-aggr-deployment true`
2. Verify disk autoassignment is disabled: `disk option show`
3. Install and cable the disk shelves for the unmirrored aggregates (per platform Installation and Setup docs).
4. Manually assign all disks on the new shelf: `disk assign -disk <disk_id> -owner <owner_node_name>`
5. Create the aggregate: `storage aggregate create` — ensure only unmirrored-shelf drives are included. Same option set as mirrored aggregate creation.
   Example: `controller_A_1::> storage aggregate create aggr1_controller_A_1 -diskcount 10 -node controller_A_1`
6. Verify: `storage aggregate show-status -aggregate <aggregate_name>`
7. Disable unmirrored aggregate deployment: `metrocluster modify -enable-unmirrored-aggr-deployment false`
8. Verify disk autoassignment is re-enabled: `disk option show`

## Checking the MetroCluster configuration

Check that components/relationships are working correctly — after initial configuration, after any configuration change, and before a negotiated switchover or switchback.

Caution: running `metrocluster check run` twice within a short time on either/both clusters can cause a conflict, and the command might not collect all data (subsequent `metrocluster check show` output won't be as expected).

Steps:
1. `metrocluster check run` (runs as a background job; use `metrocluster operation history show -job-id <id>` to check status).
2. `metrocluster check show` — shows results table: nodes, lifs, config-replication, aggregates, clusters, connections, volumes (all should show "ok").
3. Detailed results: `metrocluster check aggregate show`, `metrocluster check cluster show`, `metrocluster check config-replication show`, `metrocluster check lif show`, `metrocluster check node show`.
   Note: always run `metrocluster check run` before using the `show` commands so displayed information is current.
   - `metrocluster check aggregate show` example: for each aggregate, mirroring-status / disk-pool-allocation / ownership-state all show "ok".
   - `metrocluster check cluster show` example: negotiated-switchover-ready and switchback-ready show "not-applicable" (normal state); job-schedules, licenses, periodic-check-enabled show "ok" — indicates clusters are ready to perform a negotiated switchover if necessary.

## Completing ONTAP configuration

After configuring, enabling, and checking the MetroCluster configuration, proceed to complete cluster configuration by adding additional SVMs, network interfaces, and other ONTAP functionality as needed.
