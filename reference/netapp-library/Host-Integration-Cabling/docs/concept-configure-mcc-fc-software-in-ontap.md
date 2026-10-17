# Configure the MetroCluster FC software in ONTAP
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/concept_configure_the_mcc_software_in_ontap.html
Fetched: 2026-07-07

You must set up each node in the MetroCluster FC configuration in ONTAP, including the node-level configurations and the configuration of the nodes into two sites. You must also implement the MetroCluster relationship between the two sites.

## Gathering required information

You need to gather the required IP addresses for the controller modules before you begin the configuration process.

### IP network information worksheet for site A

You must obtain IP addresses and other network information for the first MetroCluster site (site A) from your network administrator before you configure the system.

#### Site A switch information (switched clusters)

When you cable the system, you need a host name and management IP address for each cluster switch. This information is not needed if you are using a two-node switchless cluster or have a two-node MetroCluster configuration (one node at each site).

Fields to record per cluster switch (Interconnect 1, Interconnect 2, Management 1, Management 2): host name, IP address, network mask, default gateway.

#### Site A cluster creation information

When you first create the cluster, you need: cluster name (example: site_A), DNS domain, DNS name servers, location, administrator password.

#### Site A node information

For each node in the cluster, you need a management IP address, a network mask, and a default gateway (Node 1 example: controller_A_1; Node 2 not required for two-node MetroCluster configurations, example: controller_A_2).

#### Site A LIFs and ports for cluster peering

For each node in the cluster, you need the IP addresses of two intercluster LIFs, including a network mask and a default gateway, for Node 1 IC LIF 1/2 and Node 2 IC LIF 1/2 (Node 2 not required for two-node configurations).

#### Site A time server information

You must synchronize the time, which requires one or more NTP time servers (host name, IP address, network mask, default gateway).

#### Site A AutoSupport information

You must configure AutoSupport on each node: from email address, mail hosts (IP/names), transport protocol (HTTP/HTTPS/SMTP), proxy server, recipient email addresses/distribution lists (full-length, concise, partners).

#### Site A SP information

You must enable access to the Service Processor (SP) of each node: IP address, network mask, default gateway (Node 2 not required for two-node configurations).

### IP network information worksheet for Site B

You must obtain the same categories of information (switch info, cluster creation info, node info, LIFs/ports, time server info, AutoSupport info, SP info) for the second MetroCluster site (site B) — mirroring the Site A worksheet, using controller_B_1/controller_B_2 and site_B naming examples.

## Similarities and differences between standard cluster and MetroCluster configurations

The configuration of the nodes in each cluster in a MetroCluster configuration is similar to that of nodes in a standard cluster. The MetroCluster configuration is built on two standard clusters. Physically, the configuration must be symmetrical, with each node having the same hardware configuration, and all MetroCluster components must be cabled and configured. However, the basic software configuration for nodes in a MetroCluster configuration is the same as for nodes in a standard cluster.

| Configuration step | Standard cluster | MetroCluster |
| --- | --- | --- |
| Configure management, cluster, and data LIFs on each node | Same | Same |
| Configure the root aggregate | Same | Same |
| Configure nodes in the cluster as HA pairs | Same | Same |
| Set up the cluster on one node | Same | Same |
| Join the other node to the cluster | Same | Same |
| Create a mirrored root aggregate | Optional | Required |
| Peer the clusters | Optional | Required |
| Enable the MetroCluster configuration | Does not apply | Required |

## Verifying and configuring the HA state of components in Maintenance mode

When configuring a storage system in a MetroCluster FC configuration, you must make sure that the high-availability (HA) state of the controller module and chassis components is `mcc` or `mcc-2n` so that these components boot properly. Although this value should be preconfigured on systems received from the factory, you should still verify the setting before proceeding.

> Caution: If the HA state of the controller module and chassis is incorrect, you cannot configure the MetroCluster without re-initializing the node. You must correct the setting using this procedure, then initialize the system using the appropriate restore-defaults procedure for MetroCluster IP or MetroCluster FC.

Before you begin: verify that the system is in Maintenance mode.

Steps:
1. In Maintenance mode, display the HA state of the controller module and chassis: `ha-config show`. The correct HA state depends on your MetroCluster configuration:
   - Eight or four node MetroCluster FC configuration: `mcc`
   - Two-node MetroCluster FC configuration: `mcc-2n`
   - Eight or four node MetroCluster IP configuration: `mccip`
2. If the displayed system state of the controller is not correct, set it: `ha-config modify controller mcc` (or `mcc-2n` / `mccip` as appropriate).
3. If the displayed system state of the chassis is not correct, set it: `ha-config modify chassis mcc` (or `mcc-2n` / `mccip` as appropriate).
4. Boot the node to ONTAP: `boot_ontap`.
5. Repeat this entire procedure to verify the HA state on each node in the MetroCluster configuration.

## Restoring system defaults and configuring the HBA type on a controller module

About this task: To ensure a successful MetroCluster installation, reset and restore defaults on the controller modules. This task is only required for stretch configurations using FC-to-SAS bridges.

Steps:
1. At the LOADER prompt, return the environmental variables to their default setting: `set-defaults`.
2. Boot the node into Maintenance mode (`boot_ontap maint`), check current HBA port settings (`ucadmin show`), and update port settings as needed:
   - CNA FC: `ucadmin modify -m fc -t initiator adapter_name`
   - CNA Ethernet: `ucadmin modify -mode cna adapter_name`
   - FC target: `fcadmin config -t target adapter_name`
   - FC initiator: `fcadmin config -t initiator adapter_name`
3. Exit Maintenance mode: `halt` (wait until the node stops at the LOADER prompt).
4. Boot the node back into Maintenance mode to enable the configuration changes: `boot_ontap maint`.
5. Verify the changes: `ucadmin show` (CNA) or `fcadmin show` (FC).
6. Exit Maintenance mode: `halt`.
7. Boot the node to the boot menu: `boot_ontap menu`.
8. Clear the node configuration by typing `wipeconfig` at the boot menu prompt (deletes critical system configuration, including cluster membership — do not run on an HA node that has been taken over).

## Configuring FC-VI ports on a X1132A-R6 quad-port card on FAS8020 systems

If using the X1132A-R6 quad-port card on a FAS8020 system, you can enter Maintenance mode to configure the 1a and 1b ports for FC-VI and initiator usage (not required on factory-configured MetroCluster systems). Converting an FC port to an FC-VI port with `ucadmin` is only supported on FAS8020/AFF 8020 systems.

Steps:
1. Disable the ports: `storage disable adapter 1a`, `storage disable adapter 1b`.
2. Verify ports are disabled: `ucadmin show`.
3. Set the a and b ports to FC-VI mode: `ucadmin modify -adapter 1a -type fcvi` (sets both 1a and 1b).
4. Confirm the change is pending: `ucadmin show`.
5. Shut down the controller and reboot into Maintenance mode.
6. Confirm the configuration change: `ucadmin show local`.

## Verifying disk assignment in Maintenance mode in an eight-node or four-node configuration

Before fully booting the system to ONTAP, you can optionally boot to Maintenance mode and verify disk assignment. Disks should be assigned to create a fully symmetric active-active configuration, with each pool having an equal number of assigned disks. New MetroCluster systems have disk assignment completed prior to shipment. Disks are assigned to pools on a per-shelf basis (Pool 0 = same site as owning system; Pool 1 = remote site).

Steps:
1. Confirm shelf assignments: `disk show -v`.
2. If necessary, explicitly assign disks: `disk assign` (wildcards can assign all disks on a shelf with one command; identify shelf IDs/bays with `storage show disk -x`).

### Assigning disk ownership in non-AFF systems

If disks are not correctly assigned, or you're using DS460C shelves, assign disks per node/pool on a shelf-by-shelf basis so each node has equal disks in local/remote pools. For DS460C 12-disk drawers: disks 0-2 → local node's pool 0; 3-5 → HA partner's pool 0; 6-8 → DR partner of local node's pool 1; 9-11 → DR partner of HA partner's pool 1.

Steps: boot each system into Maintenance mode; on the first node assign local shelves to pool 0 and remote shelves to pool 1 (`disk assign -shelf local-switch-name:shelf-name.port -p pool`); repeat for the second node at the local site; then repeat for both nodes at the second site; confirm with `storage show shelf`; exit Maintenance mode (`halt`); display the boot menu (`boot_ontap menu`); on each node select option 4 to initialize all disks.

### Assigning disk ownership in AFF systems

If using AFF systems with mirrored aggregates and disks (SSDs) not correctly assigned, assign half the disks on each shelf to the local node and half to its HA partner, so each node has equal disks in local/remote pools. Does not apply to unmirrored aggregates, active/passive configurations, or unequal disk counts.

Steps: boot each system into Maintenance mode; assign disks per node using `disk assign -shelf <shelf-name> -p <pool> -n <number-of-disks>`; repeat for site B; confirm with `storage show disk`; exit Maintenance mode (`halt`); display boot menu (`boot_ontap menu`); on each node select option 4 to initialize all disks.

## Verifying disk assignment in Maintenance mode in a two-node configuration

Verify disk assignment creates a fully symmetric configuration with both sites owning their own shelves and serving data, with equal mirrored disks per node/pool. For DS460C 12-disk drawers: disks 1-6 → local node's pool 0; 7-12 → DR partner's pool 1.

Steps: confirm shelf assignments (`disk show -v`); if necessary, assign disks per site using `disk assign -shelf disk_shelf_name -p pool`; show disk shelf IDs and bays (`disk show -v`).

## Setting up ONTAP

You must set up ONTAP on each controller module. If you need to netboot new controllers, see "Netbooting the new controller modules" in the MetroCluster Upgrade, Transition, and Expansion Guide.

### Setting up ONTAP in a two-node MetroCluster configuration

On each cluster, boot up the node, exit the Cluster Setup wizard, and use `cluster setup` to configure the node into a single-node cluster. This applies to two-node MetroCluster configurations using native NetApp storage and must be performed on both clusters.

Steps:
1. Power on the first node (repeat on the DR-site node). The Cluster Setup wizard starts, informing you AutoSupport will be enabled automatically; confirm with `yes` and provide node management interface port/IP/netmask/gateway.
2. Create a new cluster: `create`.
3. Choose whether the node is used as a single node cluster (default `yes`).
4. Accept defaults or provide your own values through the wizard prompts.
5. After the wizard completes, verify the cluster is active and the node is healthy: `cluster show`. Use `cluster setup` again later if you need to change any settings.

### Setting up ONTAP in an eight-node or four-node MetroCluster configuration

After booting each node, you are prompted to run the System Setup tool for basic node/cluster configuration, then return to the ONTAP CLI to create aggregates and configure MetroCluster. Applies to eight/four-node configurations using native NetApp storage; new MetroCluster systems are preconfigured, but you should still configure AutoSupport. Must be performed on both clusters. You can alternatively use the CLI cluster setup wizard.

Steps:
1. Power up each node and let it boot completely (if in Maintenance mode, `halt` then `boot_ontap` from LOADER).
2. Enable AutoSupport following on-screen directions.
3. Respond to prompts to configure the node management interface (port, IP, netmask, gateway).
4. Confirm nodes are configured in HA mode: `storage failover show -fields mode`; if not, run `storage failover modify -mode ha -node localhost` on each node and reboot (this configures HA mode but does not enable storage failover, which is auto-enabled during MetroCluster configuration).
5. Confirm four ports are configured as cluster interconnects: `network port show`.
6. If creating a two-node switchless cluster, enable switchless-cluster networking mode: `set -privilege advanced`, then `network options switchless-cluster modify -enabled true`, then `set -privilege admin`.
7. Launch the System Setup tool as directed on the console.
8. Use System Setup to configure each node and create the cluster, but do not create aggregates yet (mirrored aggregates are created in later tasks).

## Configuring the clusters into a MetroCluster configuration

You must peer the clusters, mirror the root aggregates, create a mirrored data aggregate, and then issue the command to implement the MetroCluster operations. Before running `metrocluster configure`, HA mode and DR mirroring are not enabled (an expected related error message may appear) — these are enabled by the `metrocluster configure` command itself.

### Peering the clusters

The clusters must be in a peer relationship to communicate and perform data mirroring for MetroCluster disaster recovery.

### Configuring intercluster LIFs

Create intercluster LIFs on ports used for communication between the MetroCluster partner clusters, using dedicated ports or shared data ports.

#### Configuring intercluster LIFs on dedicated ports

Dedicated ports typically increase available bandwidth for replication traffic.

Steps:
1. List the ports in the cluster: `network port show`.
2. Determine available ports for intercluster communication: `network interface show -fields home-port,curr-port`.
3. Create a failover group for the dedicated ports: `network interface failover-groups create -vserver system_SVM -failover-group failover_group -targets physical_or_logical_ports`.
4. Verify the failover group was created: `network interface failover-groups show`.
5. Create intercluster LIFs and assign to the failover group:
   - ONTAP 9.6+: `network interface create -vserver system_SVM -lif LIF_name -service-policy default-intercluster -home-node node -home-port port -address port_IP -netmask netmask -failover-group failover_group`
   - ONTAP 9.5 and earlier: same command using `-role intercluster` instead of `-service-policy default-intercluster`.
6. Verify LIF creation: `network interface show -service-policy default-intercluster` (9.6+) or `-role intercluster` (9.5-).
7. Verify LIF redundancy/failover targets with the `-failover` flag on the same show command.

#### Configuring intercluster LIFs on shared data ports

Shared data ports reduce the number of ports needed for intercluster networking.

Steps: list ports (`network port show`); create intercluster LIFs on the system SVM using the same `network interface create` syntax without a failover group; verify creation and redundancy the same way as for dedicated ports.

### Creating a cluster peer relationship

Use `cluster peer create` to create a peer relationship between a local and remote cluster; after creation, run `cluster peer create` on the remote cluster to authenticate it.

Before you begin: intercluster LIFs must exist on every node in the clusters being peered; clusters must run ONTAP 9.3 or later.

Steps:
1. On the destination cluster: `cluster peer create -generate-passphrase -offer-expiration <MM/DD/YYYY HH:MM:SS|1...7days|1...168hours> -peer-addrs peer_LIF_IPs -ipspace ipspace` (ignore `-ipspace` if not using a custom IPspace; note the generated passphrase — it cannot be displayed again).
2. On the source cluster, authenticate: `cluster peer create -peer-addrs peer_LIF_IPs -ipspace ipspace`, then enter/confirm the passphrase.
3. Verify: `cluster peer show -instance`.
4. Check connectivity/status: `cluster peer health show`.

#### Creating a cluster peer relationship (ONTAP 9.2 and earlier)

Use `cluster peer create -peer-addrs peer_LIF_IPs -ipspace ipspace` on the destination cluster first (requires cluster administrators to agree on a shared passphrase in advance), then authenticate from the source cluster with the same command and matching passphrase. Verify with `cluster peer show -instance` and `cluster peer health show`.

### Mirroring the root aggregates

Mirror the root aggregates for data protection. By default the root aggregate is RAID-DP; you can change it to RAID4 with `storage aggregate modify -aggregate aggr_name -raidtype raid4` (can be done before or after mirroring on non-ADP systems).

Steps:
1. Mirror the root aggregate: `storage aggregate mirror aggr_name` (creates a local plex and a remote plex at the remote MetroCluster site).
2. Repeat for each node in the MetroCluster configuration.

### Creating a mirrored data aggregate on each node

Create a mirrored data aggregate on each node in the DR group. Know which drives will be used; understand drive-type selection for heterogeneous storage; drives are owned by a specific node and all drives in an aggregate must be owned by the same node (the home node); aggregate names must follow your naming scheme and be unique across MetroCluster sites.

Steps:
1. Display available spares: `storage disk show -spare -owner node_name`.
2. Create the aggregate: `storage aggregate create -mirror true`, specifying home node, drives/drive count, checksum style, drive type/size/speed, RAID type, max drives per RAID group, and whether mixed RPM is allowed (in minimum-supported configs with limited drives, use `-force-small-aggregate` to allow a three-disk RAID-DP aggregate). Example: `storage aggregate create aggr1_node_A_1 -diskcount 10 -node node_A_1 -mirror true`.
3. Verify the RAID group and drives: `storage aggregate show-status -aggregate aggregate-name`.

### Creating unmirrored data aggregates

Optionally create unmirrored data aggregates for data not requiring MetroCluster mirroring redundancy.

> Important: In MetroCluster FC configurations, unmirrored aggregates only stay online after a switchover if the remote disks remain accessible; if ISLs fail, the local node may lose access to unmirrored remote disk data, potentially causing a local node reboot.

Unmirrored aggregates must be local to the owning node.

Steps:
1. Display available spares: `storage disk show -spare -owner node_name`.
2. Create the aggregate: `storage aggregate create` (same option set as mirrored, without `-mirror true`). Example: `storage aggregate create aggr1_controller_A_1 -diskcount 10 -node controller_A_1`.
3. Verify: `storage aggregate show-status -aggregate aggregate-name`.

### Implementing the MetroCluster configuration

Run `metrocluster configure` to start data protection. Before running it, there should be at least two non-root mirrored data aggregates per cluster (verify with `storage aggregate show`), and the ha-config state of controllers/chassis must be `mcc`. You issue the command once, on any node — it automatically pairs the two nodes with the lowest system IDs at each site as DR partners (in four-node configs, a second DR pair forms from the higher-system-ID nodes).

> Note: Do not configure Onboard Key Manager (OKM) or external key management before running `metrocluster configure`.

Steps:
1. Configure MetroCluster:
   - Multiple data aggregates: `metrocluster configure node-name`.
   - Single mirrored data aggregate: enter advanced privilege (`set -privilege advanced`), run `metrocluster configure -allow-with-one-aggregate true node-name`, then return to admin privilege (`set -privilege admin`). Best practice is multiple data aggregates; if adding a DR group with one aggregate to an existing single-aggregate DR group, you must move the metadata volume off the single data aggregate first.
2. Verify networking status on site A: `network port show`.
3. Verify the MetroCluster configuration from both sites: `metrocluster show` (shows local/remote cluster configuration state, mode, and AUSO failure domain).

### Configuring in-order delivery or out-of-order delivery of frames on ONTAP software

Configure in-order delivery (IOD) or out-of-order delivery (OOD) of frames to match the FC switch configuration. Rebooting the controller is required to change this setting.

Step: By default IOD is enabled. Check with `set advanced` then `metrocluster interconnect adapter show`. To configure OOD on each node: enter advanced mode, verify current settings, run `metrocluster interconnect adapter modify -node node_name -is-ood-enabled true` on each node, reboot the controller via an HA takeover in both directions, then verify settings again.

### Configuring SNMPv3 in a MetroCluster configuration

Before you begin: authentication and privacy protocols on the switches and ONTAP system must match. ONTAP currently supports AES-128 encryption.

Steps:
1. Create an SNMP user for each switch: `security login create -user-or-group-name snmpv3user -application snmp -authentication-method usm -role none -remote-switch-ipaddress <ip>`.
2. Respond to prompts for EngineID (press Enter for default), authentication protocol (none/md5/sha/sha2-256), auth password, privacy protocol (none/des/aes128), and privacy password. The same username can be reused across switches with different IPs.
3. Repeat for remaining switches.
4. Verify one login entry exists per switch: `security login show -user-or-group-name snmpv3user -fields remote-switch-ipaddress`.
5. Configure SNMPv3 on the switches from the switch prompt:
   - Brocade FOS 9.0+: `snmpconfig --add snmpv3 -index <index> -user <user_name> -groupname <rw/ro> -auth_proto <auth_protocol> -auth_passwd <auth_password> -priv_proto <priv_protocol> -priv_passwd <priv_password>`
   - Brocade FOS 8.x and earlier: `snmpconfig --set snmpv3` (interactive prompts for RW/RO users, auth/privacy protocols)
   - Cisco: `snmp-server user <user_name> auth [md5/sha/sha-256] <auth_password> priv (aes-128) <priv_password>`
   - Also set passwords on unused accounts and use the strongest encryption available in your ONTAP release.
6. Configure encryption/passwords on remaining switch users as needed.

### Configuring MetroCluster components for health monitoring

Special configuration is needed before monitoring MetroCluster components. NetApp recommends SNMPv2 or SNMPv3 for switch health monitoring (applies only to systems with FC-to-SAS bridges). Beginning with Fabric OS 9.0.1, SNMPv2 is not supported for Brocade switch health monitoring — use SNMPv3 (configure it in ONTAP first per the section above). Place bridges and a node management LIF in a dedicated network to avoid interference; if used, every node needs a node management LIF in that dedicated network.

Supported monitoring tools: Brocade Network Advisor (BNA), Brocade SANnav, Active IQ Config Advisor, NetApp Health Monitoring (ONTAP), MetroCluster data collector (MC_DC).

#### Configuring the MetroCluster FC switches for health monitoring

In a fabric-attached MetroCluster configuration, additional steps are needed to monitor FC switches. Beginning with ONTAP 9.8, `storage switch` is replaced by `system switch fibre-channel` (preferred for 9.8+).

Steps:
1. Add a switch with an IP address to each MetroCluster node:
   - SNMPv3: `storage switch add -address <ip_address> -snmp-version SNMPv3 -snmp-community-or-username <SNMP_user_configured_on_the_switch>`
   - SNMPv2: `storage switch add -address ipaddress`
   Repeat on all four switches. Brocade 7840 FC switches support all health-monitoring alerts except NoISLPresent_Alert.
2. Verify all switches are properly configured: `storage switch show` (may take up to 15 minutes due to polling interval). If the switch WWN is shown, ONTAP's health monitor can contact/monitor the FC switch.

#### Configuring FC-to-SAS bridges for health monitoring

For ONTAP versions prior to 9.8, special steps are needed to monitor FC-to-SAS bridges (third-party SNMP tools are not supported for FibreBridge bridges). Beginning with ONTAP 9.8, FC-to-SAS bridges are monitored via in-band connections by default with no extra configuration needed. Beginning with ONTAP 9.8, `storage bridge` is replaced by `system bridge` (preferred for 9.8+).

Steps:
1. Add the bridge to health monitoring:
   - ONTAP 9.5+: `storage bridge add -address 0.0.0.0 -managed-by in-band -name bridge-name`
   - ONTAP 9.4 and earlier: `storage bridge add -address bridge-ip-address -name bridge-name`
2. Verify: `storage bridge show` (may take up to 15 minutes). A "Status" of "ok" plus WWN display indicates the bridge is monitored correctly.

### Checking the MetroCluster configuration

Check that MetroCluster components/relationships work correctly after initial configuration, after any config changes, and before a negotiated switchover/switchback. Running `metrocluster check run` twice within a short time on either/both clusters can cause a conflict where not all data is collected, and subsequent `metrocluster check show` output won't reflect the expected results.

Steps:
1. Run the check: `metrocluster check run` (runs as a background job; monitor via `metrocluster operation history show -job-id <id>`).
2. View summarized results: `metrocluster check show` (reports on nodes, lifs, config-replication, aggregates, clusters, connections, volumes).
3. View detailed results from the most recent run: `metrocluster check aggregate show`, `metrocluster check cluster show`, `metrocluster check config-replication show`, `metrocluster check lif show`, `metrocluster check node show`. Always run `metrocluster check run` before these show commands so results are current.

## Checking for MetroCluster configuration errors with Config Advisor

Config Advisor is a configuration validation and health check tool you can download from the NetApp Support Site and deploy at secure or non-secure sites for data collection/system analysis. Support for Config Advisor is limited and available only online.

Steps: download Config Advisor from the NetApp Downloads page; run it, review the output, and follow its recommendations to address any discovered issues.

## Verifying local HA operation

For a four-node MetroCluster configuration, verify local HA pair operation (not required for two-node configurations, which do not consist of local HA pairs).

Steps (performed on cluster_A, then repeated on cluster_B):
1. Confirm storage failover is enabled: `storage failover show` (should show takeover possible for both nodes).
2. Take over one node from its partner: `storage failover takeover <partner-node>` (monitor with `storage failover show-takeover`).
3. Confirm takeover is complete: `storage failover show` (shows the takeover node "In takeover", partner status "Unknown").
4. Give back the node: `storage failover giveback <partner-node>` (monitor with `storage failover show-giveback`).
5. Confirm storage failover returned to normal: `storage failover show` (both nodes show takeover possible again).
6. Repeat, taking over in the opposite direction.

## Verifying switchover, healing, and switchback

Use the procedures for negotiated switchover, healing, and switchback described in "Recover from a disaster" to verify these MetroCluster operations.

## Protecting configuration backup files

You can add protection for cluster configuration backup files by specifying a remote URL (HTTP or FTP) where backup files are also uploaded, in addition to the default local cluster locations.

Step: `system configuration backup settings modify URL-of-destination`. See "Cluster Management with the CLI" > *Managing configuration backups* for more information.
