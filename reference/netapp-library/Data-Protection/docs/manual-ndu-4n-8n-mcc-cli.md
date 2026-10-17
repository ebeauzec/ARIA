# Manual nondisruptive ONTAP upgrade of a four- or eight-node MetroCluster configuration using the CLI
Source: https://docs.netapp.com/us-en/ontap/upgrade/task_updating_a_four_or_eight_node_mcc.html
Fetched: 2026-07-07

A manual upgrade of a four- or eight-node MetroCluster configuration involves preparing for the update, updating the DR pairs in each of the one or two DR groups simultaneously, and performing post-upgrade tasks.

- This task applies to: four-node MetroCluster FC or IP configurations running ONTAP 9.2 or earlier; eight-node MetroCluster FC configurations, regardless of ONTAP version.
- If you have a two-node MetroCluster configuration, do not use this procedure.
- Terminology: when upgrading, the "old" version has a lower version number than the "new" version. When downgrading, the "old" version has a higher version number than the "new" version.

## Differences when updating ONTAP software on an eight-node or four-node MetroCluster configuration

A MetroCluster configuration consists of one or two DR groups. Each DR group consists of two HA pairs, one HA pair at each MetroCluster cluster. An eight-node MetroCluster includes two DR groups. You upgrade one DR group at a time.

For four-node MetroCluster configurations:
1. Upgrade DR Group One:
   1. Upgrade node_A_1 and node_B_1.
   2. Upgrade node_A_2 and node_B_2.

For eight-node MetroCluster configurations, you perform the DR group upgrade procedure twice:
1. Upgrade DR Group One: node_A_1/node_B_1, then node_A_2/node_B_2.
2. Upgrade DR Group Two: node_A_3/node_B_3, then node_A_4/node_B_4.

## Preparing to upgrade a MetroCluster DR group

Before upgrading ONTAP software on the nodes, identify the DR relationships among the nodes, send an AutoSupport message that you are initiating an upgrade, and confirm the ONTAP version running on each node. You must have downloaded and installed the software images beforehand. This task must be repeated on each DR group.

1. Identify the DR pairs: `metrocluster node show -fields dr-partner`
   ```
   cluster_A::> metrocluster node show -fields dr-partner
      (metrocluster node show)
    dr-group-id cluster     node       dr-partner
    ----------- -------     --------   ----------
    1           cluster_A   node_A_1   node_B_1
    1           cluster_A   node_A_2   node_B_2
    1           cluster_B   node_B_1   node_A_1
    1           cluster_B   node_B_2   node_A_2
    4 entries were displayed.
   ```
2. Set the privilege level to advanced (enter `y` when prompted): `set -privilege advanced` (advanced prompt `*>` appears)
3. Confirm the ONTAP version on cluster_A: `system image show`
4. Confirm the version on cluster_B: `system image show`
5. Trigger an AutoSupport notification: `autosupport invoke -node * -type all -message "Starting_NDU"`. This records system status before the upgrade for troubleshooting. If AutoSupport is not configured to send messages, a copy is saved locally.
6. For each node in the first set, set the target ONTAP software image as the default image: `system image modify {-node nodename -iscurrent false} -isdefault true`
7. Verify the target image is set as default on cluster_A and cluster_B: `system image show`
8. Determine whether the nodes to be upgraded are currently serving clients (run twice per node to check for increasing operation counts): `system node run -node target-node -command uptime`

   > **Note:** Note each protocol with increasing client operations so you can verify traffic resumed after the upgrade.

   Example:
   ```
   cluster_x::> system node run -node node0 -command uptime
      2:58pm up  7 days, 19:16 800000260 NFS ops, 1017333 CIFS ops, 0 HTTP ops, 40395 FCP ops, 32810 iSCSI ops

      cluster_x::> system node run -node node0 -command uptime
      2:58pm up  7 days, 19:17 800001573 NFS ops, 1017333 CIFS ops, 0 HTTP ops, 40395 FCP ops, 32815 iSCSI ops
   ```

## Updating the first DR pair in a MetroCluster DR group

You must perform a takeover and giveback of the nodes in the correct order to make the new version of ONTAP current. All nodes must be running the old version of ONTAP. This task upgrades node_A_1 and node_B_1 (or node_A_3/node_B_3 for the second DR group in an eight-node configuration).

1. Migrate all data LIFs away from the node:
   ```
   network interface migrate-all -node node_A_1
   network interface migrate-all -node node_B_1
   ```
2. If MetroCluster Tiebreaker software is enabled, disable it.
3. For each node in the HA pair, disable automatic giveback: `storage failover modify -node target-node -auto-giveback false` (repeat for each node).
4. Verify automatic giveback is disabled: `storage failover show -fields auto-giveback`
5. Ensure I/O is not exceeding ~50% and CPU utilization is not exceeding ~50% per controller.
6. Initiate a takeover of the target node on cluster_A (do NOT use `-option immediate` — a normal takeover is required so the node boots onto the new software image):
   a. `storage failover takeover -ofnode node_A_1` — node boots to "Waiting for giveback" state.
      > **Note:** If AutoSupport is enabled, an AutoSupport message indicating the nodes are out of cluster quorum is expected — you can ignore it and proceed.
   b. Verify success: `storage failover show`
7. Take over the DR partner on cluster_B (node_B_1) the same way — do NOT use `-option immediate`:
   a. `storage failover takeover -ofnode node_B_1`
   b. Verify success: `storage failover show`
8. Wait at least eight minutes for client multipathing to stabilize and clients to recover from the I/O pause (recovery time is client-specific and may take longer).
9. Return the aggregates to the target nodes (note: after upgrading MetroCluster IP configurations to ONTAP 9.5 or later, aggregates will be in a degraded state briefly before resynchronizing to mirrored state):
   a. `storage failover giveback -ofnode node_A_1`
   b. `storage failover giveback -ofnode node_B_1`
   (Root aggregate is returned first, then non-root aggregates after the node finishes booting.)
10. Verify all aggregates have been returned on both clusters: `storage failover show-giveback`. If the Giveback Status field shows no aggregates to give back, all have been returned. If giveback is vetoed, the command shows progress and which subsystem vetoed it.
11. If any aggregates have not been returned:
    a. Review the veto workaround to decide whether to address the condition or override the veto.
    b. If necessary, address the "veto" condition, ensuring identified operations terminate gracefully.
    c. Reenter `storage failover giveback` (add `-override-vetoes true` if overriding).
12. Wait at least eight minutes again for client stabilization/recovery.
13. Set privilege to advanced: `set -privilege advanced`
14. Confirm the version on cluster_A: `system image show` (image2/target version should now show true/true for Default/Current on node_A_1).
15. Confirm the version on cluster_B: `system image show` (same check for node_B_1).

## Updating the second DR pair in a MetroCluster DR group

You must perform a takeover and giveback of the node in the correct order. You should have already upgraded the first DR pair (node_A_1 and node_B_1). This task upgrades node_A_2 and node_B_2 (or node_A_4/node_B_4 for the second DR group in an eight-node configuration).

1. Migrate all data LIFs away from the node:
   ```
   network interface migrate-all -node node_A_2
   network interface migrate-all -node node_B_2
   ```
2. Initiate a takeover of the target node on cluster_A (do NOT use `-option immediate`):
   a. `storage failover takeover -ofnode node_A_2 -option allow-version-mismatch`
      > **Note:** The `allow-version-mismatch` option is not required for upgrades from ONTAP 9.0 to ONTAP 9.1 or for any patch upgrades.
      Node boots to "Waiting for giveback" state; ignore any AutoSupport cluster-quorum message and proceed.
   b. Verify success: `storage failover show`
3. Initiate a takeover of the target node on cluster_B (node_B_2) — do NOT use `-option immediate`:

   | If you are upgrading from… | Enter this command… |
   |---|---|
   | ONTAP 9.2 or ONTAP 9.1 | `storage failover takeover -ofnode node_B_2` |
   | ONTAP 9.0 or Data ONTAP 8.3.x | `storage failover takeover -ofnode node_B_2 -option allow-version-mismatch` |

   > **Note:** The `allow-version-mismatch` option is not required for upgrades from ONTAP 9.0 to ONTAP 9.1 or for any patch upgrades. If AutoSupport is enabled, an AutoSupport message indicating out-of-quorum nodes is expected — safely ignore it.

   Verify success: `storage failover show`
4. Wait at least eight minutes for client multipathing stabilization/recovery.
5. Return the aggregates to the target nodes (aggregates degraded briefly after upgrading MetroCluster IP to ONTAP 9.5):
   a. `storage failover giveback -ofnode node_A_2`
   b. `storage failover giveback -ofnode node_B_2`
6. Verify all aggregates returned on both clusters: `storage failover show-giveback`
7. If any aggregates have not been returned: review the veto workaround, address the condition if needed, and reenter `storage failover giveback` (with `-override-vetoes true` if overriding).
8. Wait at least eight minutes again for stabilization/recovery.
9. Set privilege to advanced: `set -privilege advanced`
10. Confirm the version on cluster_A: `system image show` (node_A_2 should show target version as default/current).
11. Confirm the version on cluster_B: `system image show` (node_B_2 should show target version as default/current).
12. For each node in the HA pair, enable automatic giveback: `storage failover modify -node target-node -auto-giveback true` (repeat for each node).
13. Verify automatic giveback is enabled: `storage failover show -fields auto-giveback`

## Related information

- [storage failover giveback](https://docs.netapp.com/us-en/ontap-cli/storage-failover-giveback.html)
- [storage failover modify](https://docs.netapp.com/us-en/ontap-cli/storage-failover-modify.html)
- [storage failover show-giveback](https://docs.netapp.com/us-en/ontap-cli/storage-failover-show-giveback.html)
- [storage failover takeover](https://docs.netapp.com/us-en/ontap-cli/storage-failover-takeover.html)
