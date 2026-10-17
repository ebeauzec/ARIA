# Upgrade controllers in a MetroCluster FC configuration using switchover and switchback
Source: https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_upgrade_controllers_in_a_four_node_fc_mcc_us_switchover_and_switchback_mcc_fc_4n_cu.html
Fetched: 2026-07-07

You can use the MetroCluster switchover operation to provide nondisruptive service to clients while the controller modules on the partner cluster are upgraded. Other components (such as storage shelves or switches) cannot be upgraded as part of this procedure.

## Supported platform combinations

You can upgrade certain platforms using the switchover and switchback operation in a MetroCluster FC configuration. For supported platform upgrade combinations, review the MetroCluster FC upgrade table in [Choose a controller upgrade procedure](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/concept_choosing_controller_upgrade_mcc.html#supported-metrocluster-fc-controller-upgrades). Refer to [Choosing an upgrade or refresh method](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/concept_choosing_an_upgrade_method_mcc.html) for additional procedures.

## About this task

- You can use this procedure only for controller upgrade. Other components (storage shelves, switches) cannot be upgraded at the same time.
- Supported ONTAP versions: Two-node configurations — ONTAP 9.3 and later. Four- and eight-node configurations — ONTAP 9.8 and later. Do not use this procedure on four- or eight-node configurations running ONTAP versions prior to 9.8.
- Your original and new platforms must be compatible and supported ([NetApp Hardware Universe](https://hwu.netapp.com)).

  > **Note:** If the original or new platforms are FAS8020 or AFF8020 systems using ports 1c and 1d in FC-VI mode, see KB [Upgrading controllers when FCVI connections on existing FAS8020 or AFF8020 nodes use ports 1c and 1d](https://kb.netapp.com/Advice_and_Troubleshooting/Data_Protection_and_Security/MetroCluster/Upgrading_controllers_when_FCVI_connections_on_existing_FAS8020_or_AFF8020_nodes_use_ports_1c_and_1d).

- The licenses at both sites must match. Obtain new licenses from [NetApp Support](https://mysupport.netapp.com/site/).
- This procedure applies to controller modules in a MetroCluster FC configuration (two-node stretch, or two/four/eight-node fabric-attached).
- All controllers in the same DR group should be upgraded during the same maintenance period. Operating the MetroCluster configuration with different controller types in the same DR group is not supported outside of this maintenance activity. For eight-node configurations, controllers within a DR Group must be the same, but both DR groups can use different controller types.
- Mapping storage, FC, and Ethernet connections between original and new nodes in advance is recommended.
- If the new platform has fewer slots, or fewer/different port types, you might need to add an adapter ([NetApp Hardware Universe](https://hwu.netapp.com/)).

Example names used in this procedure: site_A (before: node_A_1-old, node_A_2-old; after: node_A_1-new, node_A_2-new); site_B (before: node_B_1-old, node_B_2-old; after: node_B_1-new, node_B_2-new).

## Enable console logging

NetApp strongly recommends enabling console logging and:
- Leave AutoSupport enabled during maintenance.
- Trigger a maintenance AutoSupport message before and after maintenance to disable case creation. See KB [How to suppress automatic case creation during scheduled maintenance windows](https://kb.netapp.com/removed-link).
- Enable session logging for any CLI session — see "Logging Session Output" in KB [How to configure PuTTY for optimal connectivity to ONTAP systems](https://kb.netapp.com/on-prem/ontap/Ontap_OS/OS-KBs/How_to_configure_PuTTY_for_optimal_connectivity_to_ONTAP_systems).

## Prepare for the upgrade

### Verify the health of the MetroCluster configuration

> **Caution:** After you upgrade the controllers at the first site and before you upgrade the second, `metrocluster check run` followed by `metrocluster check show` returns an error in the `config-replication` field. This indicates an NVRAM size mismatch between the nodes at each site and is expected behavior with different platform models on both sites. Ignore the error until the controller upgrade completes for all nodes in the DR group.

Steps:
1. Verify the operation of the MetroCluster configuration in ONTAP:
   a. Check whether the nodes are multipathed (each node): `node run -node node-name sysconfig -a`
   b. Verify no broken disks (each node): `storage disk show -broken`
   c. Check for health alerts (each cluster): `system health alert show`
   d. Verify licenses (each cluster): `system license show`
   e. Verify connected devices (each cluster): `network device-discovery show`
   f. Verify time zone/time correct on both sites (each cluster): `cluster date show`
2. Check for health alerts on the switches, if present (each cluster): `storage switch show`
3. Confirm the operational mode and perform a MetroCluster check:
   a. `metrocluster show`
   b. `metrocluster node show`
   c. `metrocluster check run`
   d. `metrocluster check show`
4. Check MetroCluster cabling with Config Advisor: download and run [Config Advisor](https://mysupport.netapp.com/site/tools/tool-eula/activeiq-configadvisor), then review output and follow recommendations.

### Map ports from the old nodes to the new nodes

About this task: When the new node first boots during upgrade, it replays the most recent configuration of the old node it replaces. When you boot node_A_1-new, ONTAP attempts to host LIFs on the same ports used on node_A_1-old — you must adjust port/LIF configuration to be compatible. You'll perform steps on both old and new nodes for correct cluster, management, and data LIF configuration.

Example configuration-change table:

| Cluster interconnect physical ports: Old controller | New controller | Required action |
|---|---|---|
| e0a, e0b | e3a, e3b | No matching port. After upgrade, recreate the cluster ports — see [Prepare cluster ports on an existing controller module](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_prepare_cluster_ports_on_the_exist_controller.html). |
| e0c, e0d | e0a, e0b, e0c, e0d | e0c and e0d are matching ports — no configuration change required, but after upgrade you can spread cluster LIFs across the available cluster ports. |

Steps:
1. Determine what physical ports are available on the new controllers and what LIFs can be hosted on them (port usage depends on platform module and switches — see [NetApp Hardware Universe](https://hwu.netapp.com)). Identify FC-VI card slot usage too.
2. Plan your port usage; optionally fill in a reference table per node (LIF: Cluster 1-4, Node management, Cluster management, Data 1-4, SAN, Intercluster port — old ports/IPspaces/broadcast domains vs. new).

### Gather information before the upgrade

Performed on the existing MetroCluster FC configuration.

Steps:
1. Label the cables for the existing controllers for easy identification when setting up new controllers.
2. Gather system IDs: `metrocluster node show -fields node-systemid,dr-partner-systemid`. During the upgrade, you replace old system IDs with new controller module system IDs.

   Example (four-node):
   ```
   metrocluster-siteA::> metrocluster node show -fields node-systemid,ha-partner-systemid,dr-partner-systemid,dr-auxiliary-systemid
   dr-group-id   cluster        node            node-systemid   ha-partner-systemid   dr-partner-systemid   dr-auxiliary-systemid
   -----------   ------------   -------------   -------------   -------------------   -------------------   ---------------------
   1             Cluster_A      Node_A_1-old    4068741258      4068741260            4068741256            4068741256
   1             Cluster_A      Node_A_2-old    4068741260      4068741258            4068741254            4068741254
   1             Cluster_B      Node_B_1-old    4068741254      4068741256            4068741258            4068741260
   1             Cluster_B      Node_B_2-old    4068741256      4068741254            4068741260            4068741258
   4 entries were displayed.
   ```

   Example (two-node):
   ```
   metrocluster node show -fields node-systemid,dr-partner-systemid
   dr-group-id cluster    node          node-systemid dr-partner-systemid
   ----------- ---------- ------------  ------------- ------------
   1           Cluster_A  Node_A_1-old  4068741258    4068741254
   1           Cluster_B  node_B_1-old  -             -
   2 entries were displayed.
   ```

3. Gather port and LIF information for each old node — collect output of:
   - `network interface show -role cluster,node-mgmt`
   - `network port show -node node-name -type physical`
   - `network port vlan show -node node-name`
   - `network port ifgrp show -node node_name -instance`
   - `network port broadcast-domain show`
   - `network port reachability show -detail`
   - `network ipspace show`
   - `volume show`
   - `storage aggregate show`
   - `system node run -node node-name sysconfig -a`
4. If nodes are in a SAN configuration, also collect:
   - `fcp adapter show -instance`
   - `fcp interface show -instance`
   - `iscsi interface show`
   - `ucadmin show`
5. If configured with an external key manager for the admin SVM (cluster), copy the key server information to a secure location. If using Onboard Key Manager, copy backup information and passphrase.

   **Onboard Key Manager**: `security key-manager onboard show-backup` (you'll also need the current passphrase later).

   **External key manager**:
   a. Display the admin SVM name: `vserver show -type admin`
   b. Get address/port of a primary key server: `security key-manager external show -instance -vserver <admin_svm_name>` (admin SVM can have up to 4 primary key servers; you only need one for recovery; also note username/password if applicable).
   c. If running ONTAP 9.16.1 or later, obtain the keystore UUID: `security key-manager show-key-store -vserver <admin_svm_name> -fields uuid`
   d. Save gathered info securely: primary key server port/address, username/password if any, keystore UUID (9.16.1+).

### Remove the existing configuration from the Tiebreaker or other monitoring software

If monitored by Tiebreaker or third-party apps (e.g., ClusterLion) that can initiate switchover, remove the MetroCluster configuration from that software prior to transition.

Steps:
1. Remove from Tiebreaker software — see [Remove MetroCluster configurations](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_configuring_the_tiebreaker_software.html#remove-metrocluster-configurations).
2. Remove from any third-party application that can initiate switchover (refer to that app's documentation).

### Send a custom AutoSupport message prior to maintenance

Performed on each MetroCluster site.

1. Issue: `system node autosupport invoke -node * -type all -message MAINT=maintenance-window-in-hours` (max 72 hours). To end early: `system node autosupport invoke -node * -type all -message MAINT=end`
2. Repeat on the partner cluster.

## Switch over the MetroCluster configuration

Performed on site_A. After completing, cluster_A is active and serving data for both sites; cluster_B is inactive and ready for upgrade.

Steps:
1. Switch over to site_A:
   - **Four- or eight-node FC configuration running ONTAP 9.8 or later**: `metrocluster switchover -controller-replacement true`
   - **Two-node FC configuration running ONTAP 9.3 and later**: `metrocluster switchover` (can take several minutes)
   - Monitor: `metrocluster operation show`
   - Confirm switchover state: `metrocluster show`
   - Check node status: `metrocluster node show`
2. Heal the data aggregates: `metrocluster heal data-aggregates`, then confirm with `metrocluster operation show` on the healthy cluster:
   ```
   cluster_A::> metrocluster operation show
     Operation: heal-aggregates
         State: successful
    Start Time: 7/29/2020 20:54:41
      End Time: 7/29/2020 20:54:42
        Errors: -
   ```
3. Heal the root aggregates: `metrocluster heal root-aggregates`, then confirm:
   ```
   cluster_A::> metrocluster operation show
     Operation: heal-root-aggregates
         State: successful
    Start Time: 7/29/2020 20:58:41
      End Time: 7/29/2020 20:59:42
        Errors: -
   ```

## Prepare the network configuration of the old controllers

Performed on each of the old nodes, using the port-mapping info gathered earlier.

Steps:
1. Boot the old nodes and log in: `boot_ontap`
2. Assign the home port of all data LIFs on the old controller to a common port present on both old and new controllers:
   a. `network interface show` (all data LIFs will be admin up / operationally down since active at switchover site cluster_A)
   b. Find a common physical port not used as a cluster port on either old or new controllers (e.g., e0d) — check [NetApp Hardware Universe](https://hwu.netapp.com/) for port usage.
   c. Modify data LIFs: `network interface modify -vserver svm-name -lif data-lif -home-port port-id` (e.g., `network interface modify -vserver vs0 -lif datalif1 -home-port e0d`)
3. Modify broadcast domains to remove VLAN and physical ports to be deleted: `broadcast-domain remove-ports -broadcast-domain broadcast-domain-name -ports node-name:port-id` (repeat for all VLAN and physical ports).
4. Remove VLAN ports and ifgrps using cluster ports as members:
   a. Delete VLAN ports: `network port vlan delete -node node-name -vlan-name portid-vlandid` (e.g., `network port vlan delete -node node1 -vlan-name e1c-80`)
   b. Remove physical ports from ifgrps: `network port ifgrp remove-port -node node-name -ifgrp interface-group-name -port portid` (e.g., `network port ifgrp remove-port -node node1 -ifgrp a1a -port e0d`)
   c. Remove VLAN/ifgrp ports from broadcast domain: `network port broadcast-domain remove-ports -ipspace ipspace -broadcast-domain broadcast-domain-name -ports nodename:portname,...`
   d. Modify ifgrp ports to use other physical ports as members as needed: `ifgrp add-port -node node-name -ifgrp interface-group-name -port port-id`
5. Halt the nodes (both): `halt -inhibit-takeover true -node node-name`

## Remove the old platforms

Performed on site_B.

Steps:
1. Connect to the serial console of node_B_1-old and node_B_2-old, verify LOADER prompt.
2. Disconnect storage and network connections; label cables for reuse on new nodes.
3. Disconnect power cables.
4. Remove the old controllers from the rack.

## Configure the new controllers

### Set up the new controllers

Steps:
1. Plan positioning of new controller modules and storage shelves (rack space depends on platform model, switch types, number of shelves).
2. Properly ground yourself.
3. Install the controller modules — see [ONTAP Hardware Systems Documentation](https://docs.netapp.com/platstor/index.jsp).
4. If new modules lack FC-VI cards and old FC-VI cards are compatible, swap them into the correct slots (see [NetApp Hardware Universe](https://hwu.netapp.com) for slot info).
5. Cable power, serial console, and management connections per the *MetroCluster Installation and Configuration Guides*. Do not connect other cables disconnected from old controllers yet.
6. Power up the new nodes and press Ctrl-C when prompted to display the LOADER prompt.

### Netboot the new controllers

Performed on each new controller module.

Steps:
1. Access [NetApp Support Site](https://mysupport.netapp.com/site/) to download netboot files.
2. Download the appropriate ONTAP software and store the `ontap-version_image.tgz` file on a web-accessible directory.
3. Verify needed files are available:

   | If the platform model is… | Then… |
   |---|---|
   | FAS/AFF8000 series systems | Extract contents: `tar -zxvf ontap-version_image.tgz` (on Windows use 7-Zip or WinRAR). Directory should contain `netboot/kernel`. |
   | All other systems | Directory should contain the `netboot` folder with kernel file: `ontap-version_image.tgz` (no extraction needed). |

4. At the LOADER prompt, configure the netboot connection:
   - DHCP: `ifconfig e0M -auto`
   - Static: `ifconfig e0M -addr=ip_addr -mask=netmask -gw=gateway`
5. Perform netboot:
   - 80xx series: `netboot http://web_server_ip/path_to_web-accessible_directory/netboot/kernel`
   - Other systems: `netboot http://web_server_ip/path_to_web-accessible_directory/ontap-version_image.tgz`
6. From the boot menu, select option **(7) Install new software first**. (Disregard the message "This procedure is not supported for Non-Disruptive Upgrade on an HA pair" — it applies to software NDU, not controller upgrades.)
7. Confirm with `y`; when prompted for the package, enter the image URL.
8. Enter `n` to skip backup recovery when prompted.
9. Enter `y` to reboot when prompted.

### Clear the configuration on a controller module

Steps:
1. Halt if necessary: `halt`
2. At LOADER: `set-defaults`
3. Save: `saveenv`
4. Launch boot menu: `boot_ontap menu`
5. Clear config: `wipeconfig` (respond `yes`; node reboots and shows boot menu again)
6. Select option **5** to boot into Maintenance mode (respond `yes`).

### Restore the HBA configuration

Steps:
1. In Maintenance mode:
   a. `ucadmin show`
   b. Update per HBA type:

   | HBA type / desired mode | Command |
   |---|---|
   | CNA FC | `ucadmin modify -m fc -t initiator adapter-name` |
   | CNA Ethernet | `ucadmin modify -mode cna adapter-name` |
   | FC target | `fcadmin config -t target adapter-name` |
   | FC initiator | `fcadmin config -t initiator adapter-name` |

2. Exit Maintenance mode: `halt` (wait for LOADER prompt)
3. Reboot into Maintenance mode: `boot_ontap maint`
4. Verify: `ucadmin show` (CNA) or `fcadmin show` (FC)

### Set the HA state on the new controllers and chassis

Steps:
1. `ha-config show` — expected states:

   | MetroCluster configuration | HA state |
   |---|---|
   | Two nodes | mcc-2n |
   | Four or eight nodes | mcc |

2. If incorrect:

   | Configuration | Commands |
   |---|---|
   | Two nodes | `ha-config modify controller mcc-2n`; `ha-config modify chassis mcc-2n` |
   | Four or eight nodes | `ha-config modify controller mcc`; `ha-config modify chassis mcc` |

### Reassign root aggregate disks

Performed in Maintenance mode, using system IDs gathered earlier. Example: node_B_1 old sysid 4068741254 → new sysid 1574774970.

Steps:
1. Cable all other connections to the new controller modules (FC-VI, storage, cluster interconnect, etc.).
2. Halt and boot to Maintenance mode: `boot_ontap maint`
3. Display disks owned by node_B_1-old: `disk show -a` (new controller's system ID shows, but root aggregate disks still owned by old system ID).
4. Reassign root aggregate disks: `disk reassign -s old-sysid -d new-sysid`
   ```
   *> disk reassign -s 4068741254 -d 1574774970
   Partner node must not be in Takeover mode during disk reassignment from maintenance mode.
   Serious problems could result!!
   Do not proceed with reassignment if the partner is in takeover mode. Abort reassignment (y/n)? n
   After the node becomes operational, you must perform a takeover and giveback of the HA partner node to ensure disk reassignment is successful.
   Do you want to continue (y/n)? y
   Disk ownership will be updated on all disks previously belonging to Filer with sysid 4068741254.
   Do you want to continue (y/n)? y
   ```
5. Check reassignment: `disk show`
6. Display aggregate status: `aggr status`
7. Repeat on the partner node (node_B_2-new).

### Boot up the new controllers

Performed on all new controllers.

Steps:
1. Halt: `halt`
2. If external key manager configured, set bootargs: `setenv bootarg.kmip.init.ipaddr ip-address`, `setenv bootarg.kmip.init.netmask netmask`, `setenv bootarg.kmip.init.gateway gateway-address`, `setenv bootarg.kmip.init.interface interface-id`
3. Display boot menu: `boot_ontap menu`
4. If admin SVM configured with a key manager, select the correct option:

   **ONTAP 9.8 and later**: Option `10` for Onboard key management (backup + passphrase); Option `11` for External key management (primary key server port/address, username/password if applicable, keystore UUID for ONTAP 9.16.1+).

   **ONTAP 9.7 and earlier**: `recover_onboard_keymanager` or `recover_external_keymanager` at the boot menu prompt.

5. If autoboot enabled, interrupt with CTRL-C.
6. From the boot menu, run option "6" (reboots the node twice before completing). Respond "y" to system id change prompts; wait for "Successfully restored env file from boot media... Rebooting to load the restored env file..."
7. Verify partner-sysid: `printenv partner-sysid` (set if incorrect: `setenv partner-sysid partner-sysID`)
8. If root volume encryption is used, repeat the boot menu option/command for your key management configuration (same options as step 4; may need to issue the recover command multiple times until nodes fully boot).
9. Boot the nodes: `boot_ontap`
10. Wait for nodes to boot up. If either is in takeover mode, perform giveback: `storage failover giveback`
11. Verify all ports are in a broadcast domain:
    a. `network port broadcast-domain show`
    b. Add ports to a broadcast domain as needed.
    c. Add the physical port hosting intercluster LIFs to the corresponding broadcast domain.
    d. Modify intercluster LIFs to use the new physical port as home port.
    e. Check cluster peer status and re-establish peering as needed (see [Create a cluster peer relationship](https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/concept_configure_the_mcc_software_in_ontap.html#peering-the-clusters)).
    f. Recreate VLANs and interface groups as needed (membership may differ from the old node).
12. If encryption is used, restore keys:

    | Key management | Command |
    |---|---|
    | Onboard | `security key-manager onboard sync` |
    | External | `security key-manager external restore -vserver <admin-svm> -key-server <host_name\|IP_address:port>` |

### Verify LIF configuration

Performed on site_B after nodes booted with root aggregates.

Steps:
1. Verify LIFs are hosted on appropriate node/ports prior to switchback:
   a. `set -privilege advanced`
   b. Override port configuration: `vserver config override -command "network interface modify -vserver vserver_name -home-port active_port_after_upgrade -lif lif_name -home-node new_node_name"` (build the inner command with autocomplete first, then wrap it).
   c. `set -privilege admin`
2. Revert interfaces to home node: `network interface revert * -vserver vserver-name` (perform on all SVMs as required).

### Install the new licenses

1. See [Installing licenses for the new controller module](https://docs.netapp.com/us-en/ontap-metrocluster/upgrade/task_install_licenses_on_the_new_controller_module_cluster_mode.html).

## Switch back the MetroCluster configuration

Nodes on site_A are still awaiting upgrade at this point.

Steps:
1. `metrocluster node show` on site_B — verify new nodes represented correctly and in "Waiting for switchback state."
2. Switch back: `metrocluster switchback`
3. Check progress: `metrocluster show` (in progress = `waiting-for-switchback`; complete = `normal`):
   ```
   cluster_B::> metrocluster show
   Cluster                   Entry Name          State
   ------------------------- ------------------- -----------
    Local: cluster_B         Configuration state configured
                             Mode                switchover
                             AUSO Failure Domain -
   Remote: cluster_A         Configuration state configured
                             Mode                waiting-for-switchback
                             AUSO Failure Domain -
   ```
   ```
   cluster_B::> metrocluster show
   Cluster                   Entry Name          State
   ------------------------- ------------------- -----------
    Local: cluster_B         Configuration state configured
                             Mode                normal
                             AUSO Failure Domain -
   Remote: cluster_A         Configuration state configured
                             Mode                normal
                             AUSO Failure Domain -
   ```
   If switchback takes a long time, check in-progress baselines with `metrocluster config-replication resync-status show` (advanced privilege).

## Check the health of the MetroCluster configuration

Can be performed on any node.

Steps:
1. `metrocluster show`
2. `metrocluster check run`
3. `metrocluster check show`

> **Note:** After running `metrocluster check run`/`show`, you may see an error like: `Failed to validate the node and cluster components before the switchover operation. Cluster_A:: node_A_1 (non-overridable veto): DR partner NVLog mirroring is not online. Make sure that the links between the two sites are healthy and properly configured.` This is expected behavior due to a controller mismatch during the upgrade and can be safely ignored.

## Upgrade the nodes on cluster_A

1. Repeat the entire procedure beginning with "Prepare for the upgrade," with all cluster/node references reversed (e.g., switchover from cluster_B instead of cluster_A).

## Send a custom AutoSupport message after maintenance

1. `system node autosupport invoke -node * -type all -message MAINT=end`
2. Repeat on the partner cluster.

## Restore Tiebreaker monitoring

1. Use the steps in "Add MetroCluster configurations" in the *MetroCluster Tiebreaker Installation and Configuration* guide.
