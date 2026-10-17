# Refresh a four-node or an eight-node MetroCluster IP configuration (ONTAP 9.8 and later)
Source: https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_refresh_4n_mcc_ip.html
Fetched: 2026-07-07

You can use this procedure to upgrade controllers and storage in four-node or eight-node configurations.

Beginning with ONTAP 9.13.1, you can upgrade the controllers and storage in an eight-node MetroCluster IP configuration by expanding the configuration to become a temporary twelve-node configuration and then removing the old disaster recovery (DR) groups.

Beginning with ONTAP 9.8, you can upgrade the controllers and storage in a four-node MetroCluster IP configuration by expanding the configuration to become a temporary eight-node configuration and then removing the old DR group.

## Important information if you are adding an older platform model

This guidance is for an uncommon scenario where you need to add an older platform model (platforms released before ONTAP 9.15.1) to an existing MetroCluster configuration that contains a newer platform model (platforms released in ONTAP 9.15.1 or later).

If your existing MetroCluster configuration contains a platform that uses **shared cluster/HA ports** (platforms released in ONTAP 9.15.1 or later), you cannot add a platform that uses **shared MetroCluster/HA ports** (platforms released before ONTAP 9.15.1) without upgrading all nodes in the configuration to ONTAP 9.15.1P11 or ONTAP 9.16.1P4 or later.

> **Caution:** Adding an older platform model that uses shared/MetroCluster HA ports to a MetroCluster containing a newer platform model that uses shared cluster/HA ports is an uncommon scenario and most combinations are not affected.

| If your existing MetroCluster contains… | And the platform you're adding is… | Then… |
|---|---|---|
| An AFF system using shared cluster/HA ports: AFF A20, AFF A30, AFF C30, AFF A50, AFF C60, AFF C80, AFF A70, AFF A90, AFF A1K. A FAS system using shared cluster/HA ports: FAS50, FAS70, FAS90 | An AFF system using shared MetroCluster/HA ports: AFF A150/ASA A150, AFF A220, AFF C250/ASA C250, AFF A250/ASA A250, AFF A300, AFF A320, AFF C400/ASA C400, AFF A400/ASA A400, AFF A700, AFF C800/ASA C800, AFF A800/ASA A800, AFF A900/ASA A900. A FAS system using shared MetroCluster/HA ports: FAS2750, FAS500f, FAS8200, FAS8300, FAS8700, FAS9000, FAS9500 | Before you add the new platform to your existing MetroCluster configuration, upgrade all nodes in the existing and new configuration to ONTAP 9.15.1P11 or ONTAP 9.16.1P4 or later. |

## About this task

- If you have an eight-node configuration, your system must be running ONTAP 9.13.1 or later.
- If you have a four-node configuration, your system must be running ONTAP 9.8 or later.
- If you are also upgrading the IP switches, you must upgrade them before performing this refresh procedure.
- This procedure describes the steps required to refresh one four-node DR group. If you have an eight-node configuration (two DR groups) you can refresh one or both DR groups. Refresh DR groups one at a time. References to "old nodes" mean the nodes you intend to replace. For eight-node configurations, the source and target eight-node MetroCluster platform combination must be supported.

  > **Note:** If you refresh both DR groups, the platform combination might not be supported after you refresh the first DR group. You must refresh both DR groups to achieve a supported eight-node configuration.

- You can only refresh specific platform models using this procedure in a MetroCluster IP configuration. For supported platform upgrade combinations, review the MetroCluster IP refresh table in [Choosing a system refresh method](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/concept_choosing_tech_refresh_mcc.html#supported-metrocluster-ip-tech-refresh-combinations).
- The lower limits of the source and target platforms apply. If you transition to a higher platform, the limits of the new platform apply only after the tech refresh of all DR groups completes.
- If you perform a tech refresh to a platform with lower limits than the source platform, you must adjust and reduce the limits to be at or below the target platform limits before performing this procedure.

## Enable console logging

NetApp strongly recommends that you enable console logging on the devices you are using and take the following actions when performing this procedure:

- Leave AutoSupport enabled during maintenance.
- Trigger a maintenance AutoSupport message before and after maintenance to disable case creation for the duration of the maintenance activity. See KB [How to suppress automatic case creation during scheduled maintenance windows](https://kb.netapp.com/removed-link).
- Enable session logging for any CLI session. See the "Logging Session Output" section in KB [How to configure PuTTY for optimal connectivity to ONTAP systems](https://kb.netapp.com/on-prem/ontap/Ontap_OS/OS-KBs/How_to_configure_PuTTY_for_optimal_connectivity_to_ONTAP_systems).

## Perform the refresh procedure

Steps:
1. Verify that you have a default broadcast domain created on the old nodes. When you add new nodes to an existing cluster without a default broadcast domain, node management LIFs are created for the new nodes using UUIDs instead of expected names. See KB [Node management LIFs on newly-added nodes generated with UUID names](https://kb.netapp.com/onprem/ontap/os/Node_management_LIFs_on_newly-added_nodes_generated_with_UUID_names).
2. Gather information from the old nodes (four-node configuration before expansion / eight-node after expansion — see illustrations in source).
3. To prevent automatic support case generation, send an AutoSupport message indicating the upgrade is underway:
   a. `system node autosupport invoke -node * -type all -message "MAINT=10h Upgrading old-model to new-model"` (10-hour example window; allow additional time per your plan). To end early: `system node autosupport invoke -node * -type all -message MAINT=end`
   b. Repeat the command on the partner cluster.
4. If end-to-end encryption is enabled, follow the steps to [disable end-to-end encryption](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/task-configure-encryption.html#disable-end-to-end-encryption).
5. Remove the existing MetroCluster configuration from Tiebreaker, Mediator, or other software that can initiate switchover:

   | If you are using… | Use this procedure… |
   |---|---|
   | Tiebreaker | Use the Tiebreaker CLI `monitor remove` command: `NetApp MetroCluster Tiebreaker :> monitor remove -monitor-name cluster_A`. Confirm removal with `monitor show -status`. |
   | Mediator | From the ONTAP prompt: `metrocluster configuration-settings mediator remove` |
   | Third-party applications | Refer to the product documentation. |

6. Perform all of the steps in [Expanding a MetroCluster IP configuration](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_expand_a_four_node_mcc_ip_configuration.html) to add the new nodes and storage to the configuration. (Results in a temporary eight-node or temporary twelve-node configuration, depending on starting size.)
7. Confirm that takeover is possible and the nodes are connected on both clusters: `storage failover show`
   ```
   cluster_A::> storage failover show
                                       Takeover
   Node           Partner              Possible    State Description
   -------------- -------------------- ---------   ------------------
   Node_FC_1      Node_FC_2              true      Connected to Node_FC_2
   Node_FC_2      Node_FC_1              true      Connected to Node_FC_1
   Node_IP_1      Node_IP_2              true      Connected to Node_IP_2
   Node_IP_2      Node_IP_1              true      Connected to Node_IP_1
   ```
8. Move the CRS volumes — see [Moving a metadata volume in MetroCluster configurations](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/task_move_a_metadata_volume_in_mcc_configurations.html).
9. Move the data from the old nodes to the new nodes:
   a. Perform all steps in [Create an aggregate and move volumes to the new nodes](https://docs.netapp.com/us-en/ontap-systems-upgrade/upgrade/upgrade-create-aggregate-move-volumes.html). (Note: you might choose to mirror the aggregate when or after it is created.)
   b. Perform all steps in [Move non-SAN data LIFs and cluster-management LIFs to the new nodes](https://docs.netapp.com/us-en/ontap-systems-upgrade/upgrade/upgrade-move-lifs-to-new-nodes.html).
10. Modify the IP address for the cluster peer of the transitioned nodes for each cluster:
    a. Identify the cluster_A peer: `cluster peer show`
       ```
       cluster_A::> cluster peer show
       Peer Cluster Name         Cluster Serial Number Availability   Authentication
       ------------------------- --------------------- -------------- --------------
       cluster_B         1-80-000011           Unavailable    absent
       ```
       Modify: `cluster peer modify -cluster cluster_A -peer-addrs node_A_3_IP -address-family ipv4`
    b. Identify the cluster_B peer: `cluster peer show` (similarly), then modify: `cluster peer modify -cluster cluster_B -peer-addrs node_B_3_IP -address-family ipv4`
    c. Verify the updated IP address on each cluster with `cluster peer show -instance` (check the "Remote Intercluster Addresses" field).
11. Follow the steps in [Removing a Disaster Recovery group](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/concept_removing_a_disaster_recovery_group.html) to remove the old DR group.
12. If you need to refresh both DR groups in an eight-node configuration, repeat the entire procedure for each DR group.
13. Confirm the operational mode of the MetroCluster configuration and perform a MetroCluster check:
    a. `metrocluster show`
    b. `metrocluster node show`
    c. `metrocluster check run`
    d. `metrocluster check show`
14. If you disabled end-to-end encryption before adding the new nodes, re-enable it — see [Enable end-to-end encryption](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/task-configure-encryption.html#enable-end-to-end-encryption).
15. Restore monitoring if necessary:

    | If you are using… | Use this procedure |
    |---|---|
    | Tiebreaker | [Adding MetroCluster configurations](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_configuring_the_tiebreaker_software.html#add-mcc-config-tb) |
    | Mediator | [Configure ONTAP Mediator from a MetroCluster IP configuration](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_mediator_requirements.html) |
    | Third-party applications | Refer to the product documentation. |

16. To resume automatic support case generation, send an AutoSupport message indicating maintenance is complete:
    a. `system node autosupport invoke -node * -type all -message MAINT=end`
    b. Repeat the command on the partner cluster.
