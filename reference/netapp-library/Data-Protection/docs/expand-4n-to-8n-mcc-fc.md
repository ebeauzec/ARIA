# Expanding a four-node MetroCluster FC configuration to an eight-node configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_expand_a_four_node_mcc_fc_configuration_to_an_eight_node_configuration.html
Fetched: 2026-07-07

Expanding a four-node MetroCluster FC configuration to an eight-node MetroCluster FC configuration involves adding two controllers to each cluster to form a second HA pair at each MetroCluster site, and then running the MetroCluster FC configuration operation.

## About this task

- The nodes must be running ONTAP 9 in a MetroCluster FC configuration. This procedure is not supported on earlier versions of ONTAP or in MetroCluster IP configurations.
- The existing MetroCluster FC configuration must be healthy.
- The equipment you are adding must be supported and meet all the requirements described in [Fabric-attached MetroCluster installation and configuration](https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/index.html).
- You must have available FC switch ports to accommodate the new controllers and any new bridges.
- You need the admin password and access to an FTP or SCP server.
- This procedure applies only to MetroCluster FC configurations.
- This procedure is **nondisruptive** and takes approximately one day to complete (excluding rack and stack) when disks are zeroed.

Before performing this procedure, the MetroCluster FC configuration consists of four nodes, with one HA pair at each site. At the conclusion of this procedure, the MetroCluster FC configuration consists of two HA pairs at each site.

Both sites must be expanded equally. A MetroCluster FC configuration cannot consist of an uneven number of nodes.

## Supported platform combinations when adding a second DR group

> **Important:** All nodes in the MetroCluster configuration must be running the same ONTAP version. For example, in an eight-node configuration, all eight nodes must be running the same ONTAP version. The combinations below apply only to regular or permanent eight-node configurations — they do NOT apply if you are using the transition or refresh procedures. All nodes in one DR group must be of the same type and configuration.

**Supported AFF and FAS MetroCluster FC expansion combinations**: Supported platform combinations are documented in a table/diagram in the source (image-based — see source URL for the specific AFF/FAS combination matrix).

**Supported ASA MetroCluster FC expansion combinations**:

| Eight-node DR group 1 | Eight-node DR group 2 | Supported? |
|---|---|---|
| ASA A400 | ASA A400 | Yes |
| ASA A400 | ASA A900 | No |
| ASA A900 | ASA A400 | No |
| ASA A900 | ASA A900 | Yes |
