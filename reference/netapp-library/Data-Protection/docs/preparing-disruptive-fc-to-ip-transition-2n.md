# Preparing for disruptive FC-to-IP transition
Source: https://docs.netapp.com/us-en/ontap-metrocluster/transition/concept_requirements_for_fc_to_ip_transition_2n_mcc_transition.html
Fetched: 2026-07-07

Before starting the transition process, you must make sure the configuration meets the requirements.

## Enable console logging

NetApp strongly recommends that you enable console logging on the devices you are using and take the following actions when performing this procedure:

- Leave AutoSupport enabled during maintenance.
- Trigger a maintenance AutoSupport message before and after maintenance to disable case creation for the duration of the maintenance activity. See KB [How to suppress automatic case creation during scheduled maintenance windows](https://kb.netapp.com/removed-link).
- Enable session logging for any CLI session. See the "Logging Session Output" section in KB [How to configure PuTTY for optimal connectivity to ONTAP systems](https://kb.netapp.com/on-prem/ontap/Ontap_OS/OS-KBs/How_to_configure_PuTTY_for_optimal_connectivity_to_ONTAP_systems).

## General requirements for disruptive FC-to-IP transition

The existing MetroCluster FC configuration must meet the following requirements:

- It must be a two-node configuration and all nodes must be running ONTAP 9.8 or later. It can be a two-node fabric-attached or stretched MetroCluster.
- It must meet all requirements and cabling as described in the *MetroCluster Installation and Configuration* procedures ([Fabric-attached](https://docs.netapp.com/us-en/ontap-metrocluster/install-fc/index.html), [Stretch](https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/concept_considerations_differences.html)).
- It cannot be configured with NetApp Storage Encryption (NSE).
- The MDV volumes cannot be encrypted.

You must have remote console access for all six nodes from either MetroCluster site or plan for travel between the sites as required by the procedure.

## Drive shelf reuse and drive requirements for disruptive FC-to-IP transition

You must ensure that adequate spare drives and root aggregate space is available on the storage shelves.

### Reusing the existing storage shelves

The existing storage shelves are retained for use by the new configuration. When node_A_1-FC and node_B_1-FC are removed, the existing drive shelves are connected to node_A_1-IP and node_A_2-IP on cluster_A and to node_B_1-IP and node_B_2-IP on cluster_B.

- The existing storage shelves (attached to node_A_1-FC and node_B_1-FC) must be supported by the new platform models. If not, see [Disruptively transitioning when existing shelves are not supported on new controllers (ONTAP 9.8 and later)](https://docs.netapp.com/us-en/ontap-metrocluster/transition/task_disruptively_transition_when_exist_shelves_are_not_supported_on_new_controllers.html).
- You must ensure you don't exceed the platform limits for drives, etc. ([NetApp Hardware Universe](https://hwu.netapp.com)).

### Storage requirements for the additional controllers

Additional storage must be added, if necessary, to accommodate the two additional controllers (node_A_2-IP and node_B_2-IP), because the configuration is changing from a two-node to a four-node arrangement.

- Depending on the spare drives available in the existing shelves, additional drives must be added — this might require additional storage shelves. You need 14–18 additional drives each for the third and fourth controllers (node_A_2-IP and node_B_2-IP): three pool0 drives, three pool1 drives, two spare drives, six to ten drives for the system volume.
- You must ensure that the configuration, including the new nodes, does not exceed the platform limits (drive count, root aggregate size capacity, etc.) — see [NetApp Hardware Universe](https://hwu.netapp.com).

## Workflow for disruptive transition

You must follow the specific workflow to ensure a successful transition. As you prepare, plan for travel between the sites — after the remote nodes are racked and cabled, you need serial terminal access to the nodes (Service Processor access is not available until the nodes are configured).

## Mapping ports from the MetroCluster FC nodes to the MetroCluster IP nodes

You must adjust the port and LIF configuration of the MetroCluster FC node so it is compatible with that of the MetroCluster IP node that will replace it.

About this task: When the new nodes are first booted during the upgrade process, each node uses the most recent configuration of the node it is replacing. When you boot node_A_1-IP, ONTAP attempts to host LIFs on the same ports that were used on node_A_1-FC. During the transition procedure, you perform steps on both the old and new nodes to ensure correct cluster, management, and data LIF configuration.

Steps:
1. Identify any conflicts between the existing MetroCluster FC port usage and the port usage for the MetroCluster IP interfaces on the new nodes. Identify the MetroCluster IP ports on the new MetroCluster IP controllers using the table below, then check and record if any data LIFs or cluster LIFs exist on those ports on the MetroCluster FC nodes (these conflicting LIFs will be moved at the appropriate step in the transition procedure).

   | Platform model | MetroCluster IP port | VLAN ID |
   |---|---|---|
   | AFF A800 | e0b, e1b | Not used |
   | AFF A700 and FAS9000 | e5a, e5b | |
   | AFF A320 | e0g, e0h | |
   | AFF A300 and FAS8200 | e1a, e1b | |
   | FAS8300/A400/FAS8700 | e1a, e1b | 10, 20 |
   | AFF A250 and FAS500f | e0c, e0b | 10, 20 |

   Record conflicting LIFs on each MetroCluster IP port on node_A_1-FC and node_B_1-FC for reference during the transition procedure.

2. Determine which physical ports are available on the new controllers and which LIFs can be hosted on the ports. Port usage depends on platform model and IP switch model — gather from the [NetApp Hardware Universe](https://hwu.netapp.com).

3. If desired, record the port information for node_A_1-FC and node_A_1-IP (LIF, ports, IPspaces, broadcast domains for Cluster 1-4, Node management, Cluster management, Data 1-4, SAN, Intercluster port) — plan IPspaces and broadcast domains for the new node.

4. If desired, record the equivalent port information for node_B_1-FC and node_B_1-IP.

## Preparing the MetroCluster IP controllers

You must prepare the four new MetroCluster IP nodes and install the correct ONTAP version. This task must be performed on node_A_1-IP, node_A_2-IP, node_B_1-IP, and node_B_2-IP.

The nodes should be connected to any **new** storage shelves — they must **not** be connected to the existing storage shelves containing data. These steps can be performed now or later once controllers/shelves are racked, but must be done **before** connecting to existing storage shelves and **before** making config changes to the MetroCluster FC nodes.

> **Note:** Do not perform these steps with the MetroCluster IP controllers connected to the existing storage shelves that were connected to the MetroCluster FC controllers.

Steps:
1. Connect the controller modules to the new storage shelves.
2. In Maintenance mode, display the HA state of the controller module and chassis: `ha-config show`. The HA state for all components should be "mccip".
3. If the displayed system state of the controller or chassis is not correct, set the HA state: `ha-config modify controller mccip` and `ha-config modify chassis mccip`
4. Exit Maintenance mode: `halt` (wait until the node stops at the LOADER prompt).
5. Repeat on all four nodes to clear the configuration:
   ```
   set-defaults
   saveenv
   bye
   ```
6. Repeat to boot all four nodes using the 9a option on the boot menu:
   - At the LOADER prompt: `boot_ontap menu`
   - At the boot menu, select option "9a" to reboot the controller.
7. Boot each of the four nodes to Maintenance mode using option "5" on the boot menu.
8. Record the system ID from each of the four nodes: `sysconfig`
9. Repeat on node_A_1-IP and node_B_1-IP:
   a. Assign ownership of all disks local to each site: `disk assign adapter.xx.*`
   b. Repeat for each HBA with attached drive shelves.
10. Repeat on node_A_1-IP and node_B_1-IP to clear the mailbox region on each local disk: `mailbox destroy local` and `mailbox destroy partner`
11. Halt all four controllers: `halt`
12. On each controller, display the boot menu: `boot_ontap menu`
13. On each of the four controllers, clear the configuration: `wipeconfig` (node automatically returns to the boot menu when complete)
14. Repeat to boot all four nodes using the 9a option again (at the LOADER prompt: `boot_ontap menu`; select "9a"; let each controller complete booting before moving to the next — nodes automatically return to the boot menu after "9a" completes)
15. Power off the controllers.

## Verifying the health of the MetroCluster FC configuration

You must verify the health and connectivity of the MetroCluster FC configuration prior to performing the transition (performed on the MetroCluster FC configuration):

1. Verify the operation of the MetroCluster configuration in ONTAP:
   a. Check whether the system is multipathed: `node run -node node-name sysconfig -a`
   b. Check for any health alerts on both clusters: `system health alert show`
   c. Confirm the MetroCluster configuration and that the operational mode is normal: `metrocluster show`
   d. Perform a MetroCluster check: `metrocluster check run`
   e. Display the results of the MetroCluster check: `metrocluster check show`
   f. Check for any health alerts on the switches (if present): `storage switch show`
   g. Run Config Advisor ([NetApp Downloads: Config Advisor](https://mysupport.netapp.com/site/tools/tool-eula/activeiq-configadvisor)).
   h. After running Config Advisor, review the tool's output and follow the recommendations to address any issues discovered.
2. Verify that the nodes are in non-HA mode: `storage failover show`

## Removing the existing configuration from the Tiebreaker or other monitoring software

If the existing configuration is monitored with MetroCluster Tiebreaker or other third-party applications (e.g., ClusterLion) that can initiate a switchover, you must remove the MetroCluster configuration from that software prior to transition.

Steps:
1. Remove the existing MetroCluster configuration from the Tiebreaker software — see [Removing MetroCluster configurations](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_configuring_the_tiebreaker_software.html#remove-metrocluster-configurations).
2. Remove the existing MetroCluster configuration from any third-party application that can initiate switchover (refer to that application's documentation).
