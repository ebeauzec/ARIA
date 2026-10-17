# Expanding a two-node MetroCluster FC configuration to a four-node configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_expand_a_two_node_mcc_fc_configuration_to_a_four_node_fc_configuration_supertask.html
Fetched: 2026-07-07

Expanding a two-node MetroCluster FC configuration to a four-node MetroCluster FC configuration involves adding a controller to each cluster to form an HA pair at each MetroCluster site, and then refreshing the MetroCluster FC configuration.

## Before you begin

- The nodes must be running ONTAP 9 or later in a MetroCluster FC configuration. This procedure is not supported on earlier versions of ONTAP or in MetroCluster IP configurations.
- If the platforms in your two-node configuration are not supported in ONTAP 9.2 and you plan to upgrade to platforms supported in ONTAP 9.2 *and* expand to a four-node cluster, you must upgrade the platforms in the two-node configuration *before* expanding the MetroCluster FC configuration.
- The existing MetroCluster FC configuration must be healthy.
- The equipment you are adding must be supported and meet all of the requirements described in [Fabric-attached MetroCluster installation and configuration](https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/index.html) and [Stretch MetroCluster installation and configuration](https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/concept_considerations_differences.html).
- You must have available FC switch ports to accommodate the new controllers and any new bridges.
- Verify that you have a default broadcast domain created on the old nodes. When you add new nodes to an existing cluster without a default broadcast domain, node management LIFs are created for the new nodes using UUIDs instead of expected names. See KB [Node management LIFs on newly-added nodes generated with UUID names](https://kb.netapp.com/onprem/ontap/os/Node_management_LIFs_on_newly-added_nodes_generated_with_UUID_names).
- You need the admin password and access to an FTP or SCP server.

## About this task

- This procedure applies only to MetroCluster FC configurations.
- This procedure is **disruptive** and takes approximately four hours to complete.
- Before performing this procedure, the MetroCluster FC configuration consists of two single-node clusters. After completing this procedure, the MetroCluster FC configuration consists of two HA pairs, one at each site.
- Both sites must be expanded equally — a MetroCluster configuration cannot consist of an uneven number of nodes.
- This procedure can take over an hour per site, with additional time for tasks such as initializing the disks and netbooting the new nodes. The time to initialize the disks depends on the size of the disks.

(This page is the workflow landing/overview page for the supertask; it links out to the detailed sub-procedure pages for adding controllers, cabling, and refreshing the configuration.)
