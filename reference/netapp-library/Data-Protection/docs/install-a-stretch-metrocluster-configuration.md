# Install a stretch MetroCluster configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/pdfs/sidebar/Install_a_stretch_MetroCluster_configuration.pdf
Fetched: 2026-07-07

(PDF generated from https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/index.html)

## Overview

To install your stretch MetroCluster configuration, you must perform a number of procedures in the correct order.

- Prepare for the installation and understand all requirements
- Choose the correct installation procedure
- Cable the components
  - Two-node SAS-attached configuration
  - Two-node bridge-attached configuration
- Configure the software
- Test the configuration

## Prepare for the MetroCluster installation

### Differences between the ONTAP MetroCluster configurations

The various MetroCluster configurations have key differences in the required components. In all configurations, each of the two MetroCluster sites are configured as an ONTAP cluster. In a two-node MetroCluster configuration, each node is configured as a single-node cluster.

| Feature | IP configurations (Four- or eight-node) | Fabric attached — Two-node | Stretch — Two-node bridge-attached | Stretch — Two-node direct-attached |
|---|---|---|---|---|
| Number of controllers | Four or eight | Four or eight | Two | Two | Two |
| Uses an FC switch storage fabric | No | Yes | Yes | No | No |
| Uses an IP switch storage fabric | Yes | No | No | No | No |
| Uses FC-to-SAS bridges | No | Yes | Yes | Yes | No |
| Uses direct-attached SAS storage | Yes (local attached only) | No | No | No | Yes |
| Supports ADP | Yes (beginning with ONTAP 9.4) | No | No | No | No |
| Supports local HA | Yes | Yes | No | No | No |
| Supports ONTAP automatic unplanned switchover (AUSO) | No | Yes | Yes | Yes | Yes |
| Supports unmirrored aggregates | Yes (beginning with ONTAP 9.8) | Yes | Yes | Yes | Yes |
| Supports ONTAP Mediator | Yes (beginning with ONTAP 9.7) | No | No | No | No |
| Supports MetroCluster Tiebreaker | Yes (not in combination with ONTAP Mediator) | Yes | Yes | Yes | Yes |
| Supports All SAN Arrays | Yes | Yes | Yes | Yes | Yes |

Notes:
1. Eight-node MetroCluster IP configurations — considerations:
   - Eight-node configurations are supported beginning with ONTAP 9.9.1.
   - Only NetApp-validated MetroCluster switches (ordered from NetApp) are supported.
   - Configurations using IP-routed (layer 3) backend connections are not supported.

#### Support for All SAN Array systems in MetroCluster configurations

Some of the All SAN Arrays (ASAs) are supported in MetroCluster configurations. In the MetroCluster documentation, the information for AFF models applies to the corresponding ASA system. For example, all cabling and other information for the AFF A400 system also applies to the ASA AFF A400 system. Supported platform configurations are listed in the NetApp Hardware Universe.

### Cluster peering

Each MetroCluster site is configured as a peer to its partner site. You must be familiar with the prerequisites and guidelines for configuring the peering relationships. This is important when deciding on whether to use shared or dedicated ports for those relationships.

Related information: Cluster and SVM peering express configuration

#### Prerequisites for cluster peering

Before you set up cluster peering, you should confirm that connectivity between port, IP address, subnet, firewall, and cluster-naming requirements are met.

**Connectivity requirements**

Every intercluster LIF on the local cluster must be able to communicate with every intercluster LIF on the remote cluster.

Although it is not required, it is typically simpler to configure the IP addresses used for intercluster LIFs in the same subnet. The IP addresses can reside in the same subnet as data LIFs, or in a different subnet. The subnet used in each cluster must meet the following requirements:

- The subnet must have enough IP addresses available to allocate to one intercluster LIF per node. For example, in a four-node cluster, the subnet used for intercluster communication must have four available IP addresses.
- Each node must have an intercluster LIF with an IP address on the intercluster network. Intercluster LIFs can have an IPv4 address or an IPv6 address.
- ONTAP 9 enables you to migrate your peering networks from IPv4 to IPv6 by optionally allowing both protocols to be present simultaneously on the intercluster LIFs. In earlier releases, all intercluster relationships for an entire cluster were either IPv4 or IPv6. This meant that changing protocols was a potentially disruptive event.

**Port requirements**

You can use dedicated ports for intercluster communication, or share ports used by the data network. Ports must meet the following requirements:

- All ports used to communicate with a given remote cluster must be in the same IPspace. You can use multiple IPspaces to peer with multiple clusters. Pair-wise full-mesh connectivity is required only within an IPspace.
- The broadcast domain used for intercluster communication must include at least two ports per node so that intercluster communication can fail over from one port to another port. Ports added to a broadcast domain can be physical network ports, VLANs, or interface groups (ifgrps).
- All ports must be cabled.
- All ports must be in a healthy state.
- The MTU settings of the ports must be consistent.

**Firewall requirements**

Firewalls and the intercluster firewall policy must allow the following protocols:

- ICMP service
- TCP to the IP addresses of all the intercluster LIFs over the ports 10000, 11104, and 11105
- Bidirectional HTTPS between the intercluster LIFs

The default intercluster firewall policy allows access through the HTTPS protocol and from all IP addresses (0.0.0.0/0). You can modify or replace the policy if necessary.

**Considerations when using dedicated ports**

When determining whether using a dedicated port for intercluster replication is the correct intercluster network solution, you should consider configurations and requirements such as LAN type, available WAN bandwidth, replication interval, change rate, and number of ports.

- If the amount of available WAN bandwidth is similar to that of the LAN ports, and the replication interval is such that replication occurs while regular client activity exists, then you should dedicate Ethernet ports for intercluster replication to avoid contention between replication and the data protocols.
- If the network utilization generated by the data protocols (CIFS, NFS, and iSCSI) is such that the network utilization is above 50 percent, then dedicate ports for replication to allow for nondegraded performance if a node failover occurs.
- When physical 10 GbE or faster ports are used for data and replication, you can create VLAN ports for replication and dedicate the logical ports for intercluster replication. The bandwidth of the port is shared between all VLANs and the base port.
- Consider the data change rate and replication interval and whether the amount of data, that must be replicated on each interval, requires enough bandwidth. This might cause contention with data protocols if sharing data ports.

**Considerations when sharing data ports**

When determining whether sharing a data port for intercluster replication is the correct intercluster network solution, you should consider configurations and requirements such as LAN type, available WAN bandwidth, replication interval, change rate, and number of ports.

- For a high-speed network, such as a 40-Gigabit Ethernet (40-GbE) network, a sufficient amount of local LAN bandwidth might be available to perform replication on the same 40-GbE ports that are used for data access. In many cases, the available WAN bandwidth is far less than the 10 GbE LAN bandwidth.
- All nodes in the cluster might have to replicate data and share the available WAN bandwidth, making data port sharing more acceptable.
- Sharing ports for data and replication eliminates the extra port counts required to dedicate ports for replication.
- The maximum transmission unit (MTU) size of the replication network will be the same size as that used on the data network.
- Consider the data change rate and replication interval and whether the amount of data, that must be replicated on each interval, requires enough bandwidth. This might cause contention with data protocols if sharing data ports.
- When data ports for intercluster replication are shared, the intercluster LIFs can be migrated to any other intercluster-capable port on the same node to control the specific data port that is used for replication.

### Considerations when using unmirrored aggregates

If your configuration includes unmirrored aggregates, you must be aware of potential access issues that follow switchover operations.

**Considerations for unmirrored aggregates when doing maintenance requiring power shutdown**

If you are performing a negotiated switchover for maintenance reasons requiring site-wide power shutdown, you should first manually take offline any unmirrored aggregates owned by the disaster site.

If you do not take any unmirrored aggregates offline, nodes at the surviving site might go down due to multi-disk panics. This could occur if switched over unmirrored aggregates go offline, or are missing, because of the loss of connectivity to storage at the disaster site. This is the result of a power shutdown or a loss of ISLs.

**Considerations for unmirrored aggregates and hierarchical namespaces**

If you are using hierarchical namespaces, you should configure the junction path so that all of the volumes in that path are either on mirrored aggregates only or on unmirrored aggregates only. Configuring a mix of unmirrored and mirrored aggregates in the junction path might prevent access to the unmirrored aggregates after the switchover operation.

**Considerations for unmirrored aggregates and CRS metadata volume and data SVM root volumes**

The configuration replication service (CRS) metadata volume and data SVM root volumes must be on a mirrored aggregate. You cannot move these volumes to an unmirrored aggregate. If they are on an unmirrored aggregate, negotiated switchover and switchback operations are vetoed. The MetroCluster check command provides a warning if this is the case.

**Considerations for unmirrored aggregates and SVMs**

SVMs should be configured on mirrored aggregates only, or on unmirrored aggregates only. Configuring a mix of unmirrored and mirrored aggregates can result in a switchover operation that exceeds 120 seconds and result in a data outage if the unmirrored aggregates do not come online.

**Considerations for unmirrored aggregates and SAN**

In ONTAP versions prior to 9.9.1, a LUN should not be located on an unmirrored aggregate. Configuring a LUN on an unmirrored aggregate can result in a switchover operation that exceeds 120 seconds and a data outage.

### Firewall usage at MetroCluster sites

If you are using a firewall at a MetroCluster site, you must ensure access for required ports.

The following table shows TCP/UDP port usage in an external firewall positioned between two MetroCluster sites.

| Traffic type | Port/services |
|---|---|
| Cluster peering | 11104 / TCP, 11105 / TCP |
| ONTAP System Manager | 443 / TCP |
| MetroCluster IP intercluster LIFs | 65200 / TCP, 10006 / TCP and UDP |
| Hardware assist | 4444 / TCP |

## Choosing the correct installation procedure for your configuration

You must choose the correct installation procedure based on how the storage controllers connect to storage shelves.

| For this installation type… | Use these procedures… |
|---|---|
| Two-node stretch configuration with FC-to-SAS bridges | 1. Cabling a two-node bridge-attached stretch MetroCluster configuration; 2. Configuring the MetroCluster software in ONTAP |
| Two-node stretch configuration with direct-attached SAS cabling | 1. Cabling a two-node SAS-attached stretch MetroCluster configuration; 2. Configuring the MetroCluster software in ONTAP |

## Cable a two-node SAS-attached stretch MetroCluster configuration

### Parts of a two-node SAS-attached stretch MetroCluster configuration

The two-node MetroCluster SAS-attached configuration requires a number of parts, including two single-node clusters in which the storage controllers are directly connected to the storage using SAS cables.

The MetroCluster configuration includes the following key hardware elements:

- **Storage controllers** — The storage controllers connect directly to the storage using SAS cables. Each storage controller is configured as a DR partner to a storage controller on the partner site.
  - Copper SAS cables can be used for shorter distances.
  - Optical SAS cables can be used for longer distances.

  NetApp Interoperability Matrix Tool: In the IMT, you can use the Storage Solution field to select your MetroCluster solution. You use the Component Explorer to select the components and ONTAP version to refine your search. You can click Show Results to display the list of supported configurations that match the criteria.

- **Cluster peering network** — The cluster peering network provides connectivity for mirroring of the storage virtual machine (SVM) configuration. The configuration of all SVMs on one cluster is mirrored to the partner cluster.

### Required MetroCluster hardware components and naming guidelines for two-node SAS-attached stretch configurations

The MetroCluster configuration requires a variety of hardware components. For convenience and clarity, standard names for components are used throughout the MetroCluster documentation. One site is referred to as Site A and the other site is referred to as Site B.

**Supported software and hardware**

The hardware and software must be supported for the MetroCluster FC configuration (NetApp Hardware Universe). When using AFF systems, all controller modules in the MetroCluster configuration must be configured as AFF systems.

**Hardware redundancy in the MetroCluster configuration**

Because of the hardware redundancy in the MetroCluster configuration, there are two of each component at each site. The sites are arbitrarily assigned the letters A and B and the individual components are arbitrarily assigned the numbers 1 and 2.

**Two single-node ONTAP clusters**

The SAS-attached stretch MetroCluster configuration requires two single-node ONTAP clusters. Naming must be unique within the MetroCluster configuration.

Example names: Site A: cluster_A; Site B: cluster_B

**Two storage controller modules**

The SAS-attached stretch MetroCluster configuration requires two storage controller modules.

- Naming must be unique within the MetroCluster configuration.
- All controller modules in the MetroCluster configuration must be running the same version of ONTAP.
- All controller modules in a DR group must be of the same model.
- All controller modules in a DR group must use the same FC-VI configuration.
  Some controller modules support two options for FC-VI connectivity: onboard FC-VI ports, or an FC-VI card in slot 1. A mix of one controller module using onboard FC-VI ports and another using an add-on FC-VI card is not supported. For example, if one node uses onboard FC-VI configuration, then all other nodes in the DR group must use onboard FC-VI configuration as well.

Example names: Site A: controller_A_1; Site B: controller_B_1

**At least four SAS disk shelves (recommended)**

The SAS-attached stretch MetroCluster configuration requires at least two SAS disk shelves. Four SAS disk shelves is recommended. Two shelves are recommended at each site to allow disk ownership on a per-shelf basis. A minimum of one shelf at each site is supported.

Example names: Site A: shelf_A_1_1, shelf_A_1_2; Site B: shelf_B_1_1, shelf_B_1_2

### Install and cable MetroCluster components for two-node SAS-attached stretch configurations

The storage controllers must be cabled to the storage media and to each other. The storage controllers must also be cabled to the data and management network.

Before you begin any procedure in this document:
- Prior to installation you must have familiarized yourself with the considerations and best practices for installing and cabling disk shelves for your disk shelf model.
- All MetroCluster components must be supported (NetApp Interoperability Matrix Tool — Storage Solution field, Component Explorer, Show Results).

About this task: The terms node and controller are used interchangeably.

**Racking the hardware components**

If you have not received the equipment already installed in cabinets, you must rack the components. This task must be performed on both MetroCluster sites.

Steps:
1. Plan the positioning of the MetroCluster components. The amount of rack space needed depends on the platform model of the storage controllers, the switch types, and the number of disk shelf stacks in your configuration.
2. Using standard shop practices for working with electrical equipment make sure you are properly grounded.
3. Install the storage controllers in the rack or cabinet (see ONTAP Hardware Systems Documentation).
4. Install the disk shelves, daisy-chain the disk shelves in each stack, power them on, and set the shelf IDs. See the appropriate guide for your disk shelf model for information about daisy-chaining disk shelves and setting shelf IDs. Shelf IDs must be unique for each SAS disk shelf within each MetroCluster DR group (including both sites). When manually setting shelf IDs, you must power-cycle the disk shelf.

**Cabling the controllers to each other and the storage shelves**

The controller FC-VI adapters must be cabled directly to each other. The controller SAS ports must be cabled to both the remote and local storage stacks. This task must be performed at both MetroCluster sites.

Steps:
1. Cable the FC-VI ports.
   - FAS8200 and AFF A300 controller modules can be ordered with one of two options for FC-VI connectivity: onboard ports 0e and 0f configured in FC-VI mode, or ports 1a and 1b on an FC-VI card in slot 1.
   - AFF A700 and FAS9000 storage systems controller modules use four FC-VI ports each.
   - AFF A400 and FAS8300 storage system controller modules use FC-VI ports 2a and 2b.
2. Cable the SAS ports. Your port usage might be different depending on the available SAS and FC-VI ports on the controller module.

**Cabling the cluster peering connections**

You must cable the controller module ports used for cluster peering so that they have connectivity with the cluster on their partner site. This task must be performed on each controller module in the MetroCluster configuration. At least two ports on each controller module should be used for cluster peering. The recommended minimum bandwidth for the ports and network connectivity is 1 GbE.

Steps:
1. Identify and cable at least two ports for cluster peering and verify they have network connectivity with the partner cluster. Cluster peering can be done on dedicated ports or on data ports. Using dedicated ports provides a higher throughput for the cluster peering traffic (see Cluster and SVM peering express configuration).

**Cabling the management and data connections**

You must cable the management and data ports on each storage controller to the site networks. This task must be repeated for each new controller at both MetroCluster sites. You can connect the controller and cluster switch management ports to existing switches in your network. In addition you can connect controller to new dedicated network switches such as NetApp CN1601 cluster management switches.

Steps:
1. Cable the controller's management and data ports to the management and data networks at the local site (see ONTAP Hardware Systems Documentation).

## Cable a two-node bridge-attached stretch MetroCluster configuration

### Parts of a two-node bridge-attached stretch MetroCluster configuration

As you plan your MetroCluster configuration, you should understand the parts of the configuration and how they work together. The MetroCluster configuration includes the following key hardware elements:

- **Storage controllers** — The storage controllers are not connected directly to the storage but connected to FC-to-SAS bridges. The storage controllers are connected to each other by FC cables between each controller's FC-VI adapters. Each storage controller is configured as a DR partner to a storage controller on the partner site.
- **FC-to-SAS bridges** — The FC-to-SAS bridges connect the SAS storage stacks to the FC initiator ports on the controllers, providing bridging between the two protocols.
- **Cluster peering network** — The cluster peering network provides connectivity for mirroring of the storage virtual machine (SVM) configuration. The configuration of all SVMs on one cluster is mirrored to the partner cluster.

The configuration consists of two single-node clusters. Each site has one or more stacks of SAS storage. SAS shelves in MetroCluster configurations are not supported with ACP cabling. Additional storage stacks are supported, but only one is shown at each site (in the illustration).

### Required MetroCluster hardware components and naming conventions for two-node bridge-attached stretch configurations

**Supported software and hardware**: The hardware and software must be supported for the MetroCluster FC configuration (NetApp Hardware Universe). When using AFF systems, all controller modules in the MetroCluster configuration must be configured as AFF systems.

**Hardware redundancy**: Because of the hardware redundancy in the MetroCluster configuration, there are two of each component at each site. The sites are arbitrarily assigned the letters A and B and the individual components are arbitrarily assigned the numbers 1 and 2.

**Requirement for two single-node ONTAP clusters**: The bridge-attached stretch MetroCluster configuration requires two single-node ONTAP clusters. Naming must be unique within the MetroCluster configuration. Example names: Site A: cluster_A; Site B: cluster_B

**Requirement for two storage controller modules**: The bridge-attached stretch MetroCluster configuration requires two storage controller modules. The controllers must meet the following requirements:
- Naming must be unique within the MetroCluster configuration.
- All controller modules in the MetroCluster configuration must be running the same version of ONTAP.
- All controller modules in a DR group must be of the same model.
- All controller modules in a DR group must use the same FC-VI configuration (onboard FC-VI ports or an FC-VI card in slot 1 — mixing is not supported).

Example names: Site A: controller_A_1; Site B: controller_B_1

**Requirement for FC-to-SAS bridges**: The bridge-attached stretch MetroCluster configuration requires two or more FC-to-SAS bridges at each site. These bridges connect the SAS disk shelves to the controller modules.

- FibreBridge 6500N bridges are not supported in configurations running ONTAP 9.8 and later.
- FibreBridge 7600N and 7500N bridges support up to four SAS stacks.
- Each stack can use different models of IOM, but all shelves within a stack must use the same model. The supported IOM models depend on the ONTAP version you are running.
- Naming must be unique within the MetroCluster configuration. The suggested names used as examples in this procedure identify the controller module that the bridge connects to and the port.

Example names: Site A: bridge_A_1_port-number, bridge_A_2_port-number; Site B: bridge_B_1_port-number, bridge_B_2_port-number

**Requirement for at least four SAS shelves (recommended)**: The bridge-attached stretch MetroCluster configuration requires at least two SAS shelves. However, two shelves are recommended at each site to allow disk ownership on a per-shelf basis, for a total of four SAS shelves. A minimum of one shelf at each site is supported.

Example names: Site A: shelf_A_1_1, shelf_A_1_2; Site B: shelf_B_1_1, shelf_B_1_2

### Information gathering worksheet for FC-to-SAS bridges

Before beginning to configure the MetroCluster sites, you should gather required configuration information. Each SAS stack requires at least two FC-to-SAS bridges, and each bridge connects to Controller_A_1_port-number and Controller_B_1_port-number.

| Site | Bridge | Fields to record |
|---|---|---|
| Site A | FC_bridge_A_1a | IP address, Username, Password |
| Site A | FC_bridge_A_1b | IP address, Username, Password |
| Site B | FC_bridge_B_1a | IP address, Username, Password |
| Site B | FC_bridge_B_1b | IP address, Username, Password |

### Install and cable MetroCluster components

**Racking the hardware components**

If you have not received the equipment already installed in cabinets, you must rack the components. This task must be performed on both MetroCluster sites.

Steps:
1. Plan out the positioning of the MetroCluster components. The rack space depends on the platform model of the storage controllers, switch types, and the number of disk shelf stacks in your configuration.
2. Properly ground yourself.
3. Install the storage controllers in the rack or cabinet (ONTAP Hardware Systems Documentation).
4. Install the disk shelves, power them on, and set the shelf IDs.
   - You must power-cycle each disk shelf.
   - Shelf IDs must be unique for each SAS disk shelf within each MetroCluster DR group (including both sites).
5. Install each FC-to-SAS bridge:
   a. Secure the "L" brackets on the front of the bridge to the front of the rack (flush-mount) with the four screws. The openings in the bridge "L" brackets are compliant with rack standard ETA-310-X for 19-inch (482.6 mm) racks. For more information and an illustration of the installation, see the ATTO FibreBridge Installation and Operation Manual for your bridge model.
   b. Connect each bridge to a power source that provides a proper ground.
   c. Power on each bridge. For maximum resiliency, bridges that are attached to the same stack of disk shelves must be connected to different power sources. The bridge Ready LED might take up to 30 seconds to illuminate, indicating that the bridge has completed its power-on self test sequence.

**Cabling the controllers to each other**

Each controller's FC-VI adapters must be cabled directly to its partner.

Steps:
1. Cable the FC-VI ports.
   - AFF A300 and FAS8200 controller modules can be ordered with one of two options for FC-VI connectivity: onboard ports 0e and 0f configured in FC-VI mode, or ports 1a and 1b on an FC-VI card in slot 1.
   - AFF A700 and FAS9000 storage systems controller modules use four FC-VI ports each.

**Cabling the cluster peering connections**

You must cable the controller module ports used for cluster peering so that they have connectivity with the cluster on their partner site. This task must be performed on each controller module in the MetroCluster configuration. At least two ports on each controller module should be used for cluster peering. The recommended minimum bandwidth for the ports and network connectivity is 1 GbE.

Steps:
1. Identify and cable at least two ports for cluster peering and verify they have network connectivity with the partner cluster. Cluster peering can be done on dedicated ports or on data ports. Using dedicated ports provides a higher throughput for the cluster peering traffic (Cluster and SVM peering express configuration).

**Cabling the management and data connections**

You must cable the management and data ports on each storage controller to the site networks. This task must be repeated for each new controller at both MetroCluster sites.

Steps:
1. Cable the controller's management and data ports to the management and data networks at the local site (ONTAP Hardware Systems Documentation).

### Install FC-to-SAS bridges and SAS disk shelves

> Note: The full content of this section (in-band management, bridge limits/attachment rules, prepare-for-installation, install steps, enabling IP port access, configuring the FC-to-SAS bridges, cabling with IOM12 modules, verifying bridge connectivity, and securing/unsecuring the bridge) is identical to the standalone page fetched separately — see `install-fc-to-sas-bridges-sas-disk-shelves.md` in this same folder for the complete procedure text.

## Configuring the MetroCluster software in ONTAP

You must set up each node in the MetroCluster configuration in ONTAP, including the node-level configurations and the configuration of the nodes into two sites. You must also implement the MetroCluster relationship between the two sites.

Steps:
1. Gather the required IP addresses for the controller modules before you begin the configuration process.
2. Complete the IP network information worksheet for site A.

### IP network information worksheet for Site A

You must obtain IP addresses and other network information for the first MetroCluster site (site A) from your network administrator before you configure the system.

**Site A cluster creation information** — when you first create the cluster, you need: Cluster name (example: site_A), DNS domain, DNS name servers, Location, Administrator password.

**Site A node information** — for each node in the cluster, you need a management IP address, a network mask, and a default gateway (Node 1 example: controller_A_1; Node 2 not required if using two-node MetroCluster configuration — example: controller_A_2).

**Site A LIFs and ports for cluster peering** — for each node, you need the IP addresses of two intercluster LIFs (IC LIF 1, IC LIF 2), including a network mask and default gateway.

**Site A time server information** — you must synchronize the time, which requires one or more NTP time servers (NTP server 1, NTP server 2 — host name, IP address, network mask, default gateway).

**Site A AutoSupport information** — you must configure AutoSupport on each node, which requires: From email address, Mail hosts IP addresses or names, Transport protocol (HTTP, HTTPS, or SMTP), Proxy server, Recipient email addresses or distribution lists, Full-length messages, Concise messages, Partners.

**Site A SP information** — you must enable access to the Service Processor (SP) of each node for troubleshooting and maintenance: IP address, network mask, default gateway for Node 1.

### IP network information worksheet for site B

Same categories as Site A worksheet, for site B: Cluster name (example: site_B), DNS domain, DNS name servers, Location, Administrator password; Node information (Node 1 example: controller_B_1; Node 2 example: controller_B_2, not required for two-node configurations); LIFs and ports for cluster peering (IC LIF 1, IC LIF 2); time server information (NTP server 1, NTP server 2); AutoSupport information; SP information (Node 1 — controller_B_1).

### Similarities and differences between standard cluster and MetroCluster configurations

The configuration of the nodes in each cluster in a MetroCluster configuration is similar to that of nodes in a standard cluster. The MetroCluster configuration is built on two standard clusters. Physically, the configuration must be symmetrical, with each node having the same hardware configuration, and all of the MetroCluster components must be cabled and configured. However, the basic software configuration for nodes in a MetroCluster configuration is the same as that for nodes in a standard cluster.

| Configuration step | Standard cluster configuration | MetroCluster configuration |
|---|---|---|
| Configure management, cluster, and data LIFs on each node | Same in both types of clusters | Same in both types of clusters |
| Configure the root aggregate | Same in both types of clusters | Same in both types of clusters |
| Set up the cluster on one node in the cluster | Same in both types of clusters | Same in both types of clusters |
| Join the other node to the cluster | Same in both types of clusters | Same in both types of clusters |
| Create a mirrored root aggregate | Optional | Required |
| Peer the clusters | Optional | Required |
| Enable the MetroCluster configuration | Does not apply | Required |

### Restoring system defaults and configuring the HBA type on a controller module

To ensure a successful MetroCluster installation, reset and restore defaults on the controller modules.

> **Important:** This task is only required for stretch configurations using FC-to-SAS bridges.

Steps:
1. At the LOADER prompt, return the environmental variables to their default setting: `set-defaults`
2. Boot the node into Maintenance mode, then configure the settings for any HBAs in the system:
   a. Boot into Maintenance mode: `boot_ontap maint`
   b. Check the current settings of the ports: `ucadmin show`
   c. Update the port settings as needed:

   | HBA type / desired mode | Command |
   |---|---|
   | CNA FC | `ucadmin modify -m fc -t initiator adapter_name` |
   | CNA Ethernet | `ucadmin modify -mode cna adapter_name` |
   | FC target | `fcadmin config -t target adapter_name` |
   | FC initiator | `fcadmin config -t initiator adapter_name` |

3. Exit Maintenance mode: `halt` (wait until the node stops at the LOADER prompt)
4. Boot the node back into Maintenance mode to enable the configuration changes to take effect: `boot_ontap maint`
5. Verify the changes you made:

   | HBA type | Command |
   |---|---|
   | CNA | `ucadmin show` |
   | FC | `fcadmin show` |

6. Exit Maintenance mode: `halt` (wait until the node stops at the LOADER prompt)
7. Boot the node to the boot menu: `boot_ontap menu` (wait until the boot menu is shown)
8. Clear the node configuration by typing "wipeconfig" at the boot menu prompt, and then press Enter.

   ```
   Please choose one of the following:
     (1) Normal Boot.
     (2) Boot without /etc/rc.
     (3) Change password.
     (4) Clean configuration and initialize all disks.
     (5) Maintenance mode boot.
     (6) Update flash from backup config.
     (7) Install new software first.
     (8) Reboot node.
     (9) Configure Advanced Drive Partitioning.
     Selection (1-9)? wipeconfig
    This option deletes critical system configuration, including cluster membership.
    Warning: do not run this option on a HA node that has been taken over.
    Are you sure you want to continue?: yes
    Rebooting to finish wipeconfig request.
   ```

### Configuring FC-VI ports on a X1132A-R6 quad-port card on FAS8020 systems

If you are using the X1132A-R6 quad-port card on a FAS8020 system, you can enter Maintenance mode to configure the 1a and 1b ports for FC-VI and initiator usage. This is not required on MetroCluster systems received from the factory, in which the ports are set appropriately for your configuration.

This task must be performed in Maintenance mode. Converting an FC port to an FC-VI port with the `ucadmin` command is only supported on the FAS8020 and AFF 8020 systems. Converting FC ports to FC-VI ports is not supported on any other platform.

Steps:
1. Disable the ports:
   ```
   storage disable adapter 1a
   storage disable adapter 1b
   ```
   Example output:
   ```
   *> storage disable adapter 1a
   Jun 03 02:17:57 [controller_B_1:fci.adapter.offlining:info]: Offlining Fibre Channel adapter 1a.
   Host adapter 1a disable succeeded
   Jun 03 02:17:57 [controller_B_1:fci.adapter.offline:info]: Fibre Channel adapter 1a is now offline.
   *> storage disable adapter 1b
   Jun 03 02:18:43 [controller_B_1:fci.adapter.offlining:info]: Offlining Fibre Channel adapter 1b.
   Host adapter 1b disable succeeded
   Jun 03 02:18:43 [controller_B_1:fci.adapter.offline:info]: Fibre Channel adapter 1b is now offline.
   ```
2. Verify that the ports are disabled: `ucadmin show`
   ```
   *> ucadmin show
     Current Current Pending Pending Admin
   Adapter Mode Type Mode Type Status
   ------- ------- --------- ------- --------- -------
     ...
     1a fc initiator - - offline
     1b fc initiator - - offline
     1c fc initiator - - online
     1d fc initiator - - online
   ```
3. Set the a and b ports to FC-VI mode: `ucadmin modify -adapter 1a -type fcvi` (the command sets the mode on both ports in the port pair, 1a and 1b, even though only 1a is specified).
   ```
   *> ucadmin modify -t fcvi 1a
   Jun 03 02:19:13 [controller_B_1:ucm.type.changed:info]: FC-4 type has changed to fcvi on adapter 1a. Reboot the controller for the changes to take effect.
   Jun 03 02:19:13 [controller_B_1:ucm.type.changed:info]: FC-4 type has changed to fcvi on adapter 1b. Reboot the controller for the changes to take effect.
   ```
4. Confirm that the change is pending: `ucadmin show`
   ```
   *> ucadmin show
     Current Current Pending Pending Admin
   Adapter Mode Type Mode Type Status
   ------- ------- --------- ------- --------- -------
     ...
     1a fc initiator - fcvi offline
     1b fc initiator - fcvi offline
     1c fc initiator - - online
     1d fc initiator - - online
   ```
5. Shut down the controller, and then reboot into Maintenance mode.
6. Confirm the configuration change: `ucadmin show local`
   ```
   Node Adapter Mode Type Mode Type Status
   ------------ ------- ------- --------- ------- --------- -----------
   ...
   controller_B_1  1a fc fcvi - - online
   controller_B_1  1b fc fcvi - - online
   controller_B_1  1c fc initiator - - online
   controller_B_1  1d fc initiator - - online
   6 entries were displayed.
   ```

### Verifying disk assignment in Maintenance mode in a two-node configuration

Before fully booting the system to ONTAP, you can optionally boot the system to Maintenance mode and verify the disk assignment on the nodes. The disks should be assigned to create a fully symmetric configuration with both sites owning their own disk shelves and serving data, where each node and each pool have an equal number of mirrored disks assigned to them.

Before you begin: the system must be in Maintenance mode.

New MetroCluster systems have disk assignments completed prior to shipment. Disks are assigned to pools on a per-shelf basis. Example pool assignments:

| Disk shelf (example name) | At site | Belongs to | And is assigned to that node's… |
|---|---|---|---|
| Disk shelf 1 (shelf_A_1_1), Disk shelf 2 (shelf_A_1_3) | Site A | Node A 1 | Pool 0 |
| Disk shelf 3 (shelf_B_1_1), Disk shelf 4 (shelf_B_1_3) | Site A | Node B 1 | Pool 1 |
| Disk shelf 9 (shelf_B_1_2), Disk shelf 10 (shelf_B_1_4) | Site B | Node B 1 | Pool 0 |
| Disk shelf 11 (shelf_A_1_2), Disk shelf 12 (shelf_A_1_4) | Site B | Node A 1 | Pool 1 |

If your configuration includes DS460C disk shelves, you should manually assign the disks using the following guidelines for each 12-disk drawer: disks 1–6 → local node's pool 0; disks 7–12 → DR partner's pool 1. This disk assignment pattern minimizes the effect on an aggregate if a drawer goes offline.

Steps:
1. If your system was received from the factory, confirm the shelf assignments: `disk show –v`
2. If necessary, you can explicitly assign disks on the attached disk shelves to the appropriate pool: `disk assign`. Disk shelves at the same site as the node are assigned to pool 0 and disk shelves located at the partner site are assigned to pool 1. You should assign an equal number of shelves to each pool.
   a. If you have not done so, boot each system into Maintenance mode.
   b. On the node on site A, systematically assign the local disk shelves to pool 0 and the remote disk shelves to pool 1: `disk assign -shelf disk_shelf_name -p pool`
      Example (node_A_1 with four shelves):
      ```
      *> disk assign -shelf shelf_A_1_1 -p 0
      *> disk assign -shelf shelf_A_1_3 -p 0
      *> disk assign -shelf shelf_A_1_2 -p 1
      *> disk assign -shelf shelf_A_1_4 -p 1
      ```
   c. On the node at the remote site (site B), systematically assign its local disk shelves to pool 0 and its remote disk shelves to pool 1:
      ```
      *> disk assign -shelf shelf_B_1_2 -p 0
      *> disk assign -shelf shelf_B_1_4 -p 0
      *> disk assign -shelf shelf_B_1_1 -p 1
      *> disk assign -shelf shelf_B_1_3 -p 1
      ```
   d. Show the disk shelf IDs and bays for each disk: `disk show –v`

### Verifying the HA state of components

In a stretch MetroCluster configuration that is not preconfigured at the factory, you must verify that the HA state of the controller and chassis component is set to "mcc-2n" so that they boot up properly. For systems received from the factory, this value is preconfigured and you do not need to verify it.

Before you begin: the system must be in Maintenance mode.

Steps:
1. In Maintenance mode, view the HA state of the controller module and chassis: `ha-config show`. The controller module and chassis should show the value "mcc-2n".
2. If the displayed system state of the controller is not "mcc-2n", set the HA state for the controller: `ha-config modify controller mcc-2n`
3. If the displayed system state of the chassis is not "mcc-2n", set the HA state for the chassis: `ha-config modify chassis mcc-2n`. Halt the node and wait until the node is back at the LOADER prompt.
4. Repeat these steps on each node in the MetroCluster configuration.

### Setting up ONTAP in a two-node MetroCluster configuration

In a two-node MetroCluster configuration, on each cluster you must boot up the node, exit the Cluster Setup wizard, and use the cluster setup command to configure the node into a single-node cluster.

Before you begin: you must not have configured the Service Processor.

This task is for two-node MetroCluster configurations using native NetApp storage, and must be performed on both clusters in the MetroCluster configuration.

Steps:
1. Power on the first node (repeat on the node at the DR site). The node boots, then the Cluster Setup wizard starts on the console informing you that AutoSupport will be enabled automatically.
   ```
   ::> Welcome to the cluster setup wizard.
   You can enter the following commands at any time:
     "help" or "?" - if you want to have a question clarified,
     "back" - if you want to change previously answered questions, and
     "exit" or "quit" - if you want to quit the cluster setup wizard.
     Any changes you made before quitting will be saved.
   You can return to cluster setup at any time by typing "cluster setup".
   To accept a default or omit a question, do not enter a value.
   This system will send event messages and periodic reports to NetApp Technical Support.
   To disable this feature, enter autosupport modify -support disable within 24 hours.
   Enabling AutoSupport can significantly speed problem determination and resolution, should a problem occur on your system.
   For further information on AutoSupport, see: http://support.netapp.com/autosupport/
   Type yes to confirm and continue {yes}: yes
   Enter the node management interface port [e0M]:
   Enter the node management interface IP address [10.101.01.01]:
   Enter the node management interface netmask [101.010.101.0]:
   Enter the node management interface default gateway [10.101.01.0]:
   Do you want to create a new cluster or join an existing cluster? {create, join}:
   ```
2. Create a new cluster: `create`
3. Choose whether the node is to be used as a single node cluster: `Do you intend for this node to be used as a single node cluster? {yes, no} [yes]:`
4. Accept the system default "yes" by pressing Enter, or enter your own values by typing "no", and then pressing Enter.
5. Follow the prompts to complete the Cluster Setup wizard, pressing Enter to accept the default values or typing your own values and then pressing Enter. The default values are determined automatically based on your platform and network configuration.
6. After you complete the Cluster Setup wizard and it exits, verify that the cluster is active and the first node is healthy: `cluster show`
   ```
   cluster1::> cluster show
   Node Health Eligibility
   --------------------- ------- ------------
   cluster1-01 true true
   ```
   If it becomes necessary to change any of the settings you entered for the admin SVM or node SVM, you can access the Cluster Setup wizard by using the `cluster setup` command.

### Configuring the clusters into a MetroCluster configuration

You must peer the clusters, mirror the root aggregates, create a mirrored data aggregate, and then issue the command to implement the MetroCluster operations.

#### Peering the clusters

The clusters in the MetroCluster configuration must be in a peer relationship so that they can communicate with each other and perform the data mirroring essential to MetroCluster disaster recovery.

Related information: Cluster and SVM peering express configuration; Considerations when using dedicated ports; Considerations when sharing data ports

**Configuring intercluster LIFs**

You must create intercluster LIFs on ports used for communication between the MetroCluster partner clusters. You can use dedicated ports or ports that also have data traffic.

*Configuring intercluster LIFs on dedicated ports*

Steps:
1. List the ports in the cluster: `network port show`
   ```
   cluster01::> network port show
                                                          Speed (Mbps)
   Node   Port  IPspace  Broadcast Domain  Link  MTU  Admin/Oper
   ------ ----- -------- ---------------- ----- ------- ------------
   cluster01-01
     e0a Cluster Cluster up 1500 auto/1000
     e0b Cluster Cluster up 1500 auto/1000
     e0c Default Default up 1500 auto/1000
     e0d Default Default up 1500 auto/1000
     e0e Default Default up 1500 auto/1000
     e0f Default Default up 1500 auto/1000
   cluster01-02
     e0a Cluster Cluster up 1500 auto/1000
     e0b Cluster Cluster up 1500 auto/1000
     e0c Default Default up 1500 auto/1000
     e0d Default Default up 1500 auto/1000
     e0e Default Default up 1500 auto/1000
     e0f Default Default up 1500 auto/1000
   ```
2. Determine which ports are available to dedicate to intercluster communication: `network interface show -fields home-port,curr-port`. Example shows ports "e0e" and "e0f" have not been assigned LIFs.
3. Create a failover group for the dedicated ports: `network interface failover-groups create -vserver system_SVM -failover-group failover_group -targets physical_or_logical_ports`
   Example (assigns e0e and e0f to failover group "intercluster01" on SVM "cluster01"):
   ```
   cluster01::> network interface failover-groups create -vserver cluster01 -failover-group intercluster01 -targets cluster01-01:e0e,cluster01-01:e0f,cluster01-02:e0e,cluster01-02:e0f
   ```
4. Verify that the failover group was created: `network interface failover-groups show`
5. Create intercluster LIFs on the system SVM and assign them to the failover group.

   | ONTAP version | Command |
   |---|---|
   | ONTAP 9.6 and later | `network interface create -vserver system_SVM -lif LIF_name -service-policy default-intercluster -home-node node -home-port port -address port_IP -netmask netmask -failover-group failover_group` |
   | ONTAP 9.5 and earlier | `network interface create -vserver system_SVM -lif LIF_name -role intercluster -home-node node -home-port port -address port_IP -netmask netmask -failover-group failover_group` |

   Example creates intercluster LIFs "cluster01_icl01" and "cluster01_icl02" in the failover group "intercluster01":
   ```
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl01 -service-policy default-intercluster -home-node cluster01-01 -home-port e0e -address 192.168.1.201 -netmask 255.255.255.0 -failover-group intercluster01
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl02 -service-policy default-intercluster -home-node cluster01-02 -home-port e0e -address 192.168.1.202 -netmask 255.255.255.0 -failover-group intercluster01
   ```
6. Verify that the intercluster LIFs were created:

   | ONTAP version | Command |
   |---|---|
   | ONTAP 9.6 and later | `network interface show -service-policy default-intercluster` |
   | ONTAP 9.5 and earlier | `network interface show -role intercluster` |

7. Verify that the intercluster LIFs are redundant:

   | ONTAP version | Command |
   |---|---|
   | ONTAP 9.6 and later | `network interface show -service-policy default-intercluster -failover` |
   | ONTAP 9.5 and earlier | `network interface show -role intercluster -failover` |

   Example shows LIFs "cluster01_icl01" and "cluster01_icl02" on port "e0e" will fail over to port "e0f".

Related information: Considerations when using dedicated ports

*Configuring intercluster LIFs on shared data ports*

Steps:
1. List the ports in the cluster: `network port show`
2. Create intercluster LIFs on the system SVM:

   | ONTAP version | Command |
   |---|---|
   | ONTAP 9.6 and later | `network interface create -vserver system_SVM -lif LIF_name -service-policy default-intercluster -home-node node -home-port port -address port_IP -netmask netmask` |
   | ONTAP 9.5 and earlier | `network interface create -vserver system_SVM -lif LIF_name -role intercluster -home-node node -home-port port -address port_IP -netmask netmask` |

   Example creates intercluster LIFs "cluster01_icl01" and "cluster01_icl02":
   ```
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl01 -service-policy default-intercluster -home-node cluster01-01 -home-port e0c -address 192.168.1.201 -netmask 255.255.255.0
   cluster01::> network interface create -vserver cluster01 -lif cluster01_icl02 -service-policy default-intercluster -home-node cluster01-02 -home-port e0c -address 192.168.1.202 -netmask 255.255.255.0
   ```
3. Verify that the intercluster LIFs were created (same commands as above per ONTAP version).
4. Verify that the intercluster LIFs are redundant (same commands as above per ONTAP version). Example shows LIFs on port "e0c" will fail over to port "e0d".

Related information: Considerations when sharing data ports

#### Creating a cluster peer relationship

You must create the cluster peer relationship between the MetroCluster clusters.

*Creating a cluster peer relationship (ONTAP 9.3 and later)*

You can use the `cluster peer create` command to create a peer relationship between a local and remote cluster. After the peer relationship has been created, you can run `cluster peer create` on the remote cluster to authenticate it to the local cluster.

Before you begin: you must have created intercluster LIFs on every node in the clusters that are being peered. The clusters must be running ONTAP 9.3 or later.

Steps:
1. On the destination cluster, create a peer relationship with the source cluster: `cluster peer create -generate-passphrase -offer-expiration MM/DD/YYYY HH:MM:SS|1…7days|1…168hours -peer-addrs peer_LIF_IPs -ipspace ipspace`. If you specify both `-generate-passphrase` and `-peer-addrs`, only the cluster whose intercluster LIFs are specified in `-peer-addrs` can use the generated password. You can ignore the `-ipspace` option if you are not using a custom IPspace.
   Example creates a cluster peer relationship on an unspecified remote cluster:
   ```
   cluster02::> cluster peer create -generate-passphrase -offer-expiration 2days
     Passphrase: UCa+6lRVICXeL/gq1WrK7ShR
     Expiration Time: 6/7/2017 08:16:10 EST
     Initial Allowed Vserver Peers: -
     Intercluster LIF IP: 192.140.112.101
     Peer Cluster Name: Clus_7ShR (temporary generated)
   Warning: make a note of the passphrase - it cannot be displayed again.
   ```
2. On source cluster, authenticate the source cluster to the destination cluster: `cluster peer create -peer-addrs peer_LIF_IPs -ipspace ipspace`
   Example authenticates the local cluster to the remote cluster at intercluster LIF IP addresses 192.140.112.101 and 192.140.112.102:
   ```
   cluster01::> cluster peer create -peer-addrs 192.140.112.101,192.140.112.102
   Notice: Use a generated passphrase or choose a passphrase of 8 or more characters.
     To ensure the authenticity of the peering relationship, use a phrase or sequence of characters that would be hard to guess.
   Enter the passphrase:
   Confirm the passphrase:
   Clusters cluster02 and cluster01 are peered.
   ```
3. Verify that the cluster peer relationship was created: `cluster peer show -instance`
4. Check the connectivity and status of the nodes in the peer relationship: `cluster peer health show`

*Creating a cluster peer relationship (ONTAP 9.2 and earlier)*

You can use the `cluster peer create` command to initiate a request for a peering relationship between a local and remote cluster. After the peer relationship has been requested by the local cluster, you can run `cluster peer create` on the remote cluster to accept the relationship.

Before you begin: you must have created intercluster LIFs on every node in the clusters being peered. The cluster administrators must have agreed on the passphrase each cluster will use to authenticate itself to the other.

Steps:
1. On the data protection destination cluster, create a peer relationship with the data protection source cluster: `cluster peer create -peer-addrs peer_LIF_IPs -ipspace ipspace`
   Example (remote cluster at 192.168.2.201 and 192.168.2.202):
   ```
   cluster02::> cluster peer create -peer-addrs 192.168.2.201,192.168.2.202
   Enter the passphrase:
   Please enter the passphrase again:
   ```
2. On the data protection source cluster, authenticate the source cluster to the destination cluster: `cluster peer create -peer-addrs peer_LIF_IPs -ipspace ipspace`
   Example (remote cluster at 192.140.112.203 and 192.140.112.204... local cluster at 192.168.2.203/204):
   ```
   cluster01::> cluster peer create -peer-addrs 192.168.2.203,192.168.2.204
   Please confirm the passphrase:
   Please confirm the passphrase again:
   ```
3. Verify that the cluster peer relationship was created: `cluster peer show –instance`
4. Check the connectivity and status of the nodes in the peer relationship: `cluster peer health show`

#### Mirroring the root aggregates

You must mirror the root aggregates to provide data protection.

By default, the root aggregate is created as RAID-DP type aggregate. You can change the root aggregate from RAID-DP to RAID4 type aggregate: `storage aggregate modify –aggregate aggr_name -raidtype raid4`. On non-ADP systems, the RAID type of the aggregate can be modified from the default RAID-DP to RAID4 before or after the aggregate is mirrored.

Steps:
1. Mirror the root aggregate: `storage aggregate mirror aggr_name`
   Example mirrors the root aggregate for "controller_A_1":
   ```
   controller_A_1::> storage aggregate mirror aggr0_controller_A_1
   ```
   This mirrors the aggregate, so it consists of a local plex and a remote plex located at the remote MetroCluster site.
2. Repeat the previous step for each node in the MetroCluster configuration.

Related information: Logical storage management; ONTAP concepts

#### Creating a mirrored data aggregate on each node

You must create a mirrored data aggregate on each node in the DR group.

Before you begin: you should know what drives will be used in the new aggregate; if you have multiple drive types (heterogeneous storage), understand how to ensure the correct drive type is selected.

About this task:
- Drives are owned by a specific node; when you create an aggregate, all drives in that aggregate must be owned by the same node, which becomes the home node for that aggregate.
- Aggregate names should conform to the naming scheme you determined when you planned your MetroCluster configuration (see Disk and aggregate management).
- Aggregate names must be unique across the MetroCluster sites — you cannot have two different aggregates with the same name on site A and site B.

Steps:
1. Display a list of available spares: `storage disk show -spare -owner node_name`
2. Create the aggregate: `storage aggregate create -mirror true`. If logged in on the cluster management interface, you can create an aggregate on any node in the cluster; to ensure it's created on a specific node, use the `-node` parameter or specify drives owned by that node. Options include: aggregate's home node, list of specific drives, number of drives, checksum style, drive type, drive size, drive speed, RAID type, max drives per RAID group, whether mixed RPM drives are allowed. In the minimum supported configuration (limited drives available), you must use the `-force-small-aggregate` option to allow creation of a three-disk RAID-DP aggregate.
   Example creates a mirrored aggregate with 10 disks:
   ```
   cluster_A::> storage aggregate create aggr1_node_A_1 -diskcount 10 -node node_A_1 -mirror true
   [Job 15] Job is queued: Create aggr1_node_A_1.
   [Job 15] The job is starting.
   [Job 15] Job succeeded: DONE
   ```
3. Verify the RAID group and drives of your new aggregate: `storage aggregate show-status -aggregate aggregate-name`

#### Creating unmirrored data aggregates

You can optionally create unmirrored data aggregates for data that does not require the redundant mirroring provided by MetroCluster configurations.

> **ATTENTION:** In MetroCluster FC configurations, the unmirrored aggregates will only be online after a switchover if the remote disks in the aggregate are accessible. If the ISLs fail, the local node may be unable to access the data in the unmirrored remote disks. The failure of an aggregate can lead to a reboot of the local node. The unmirrored aggregates must be local to the node owning them.

Before you begin: know what drives will be used; understand heterogeneous drive-type selection if applicable.

Steps:
1. Display a list of available spares: `storage disk show -spare -owner node_name`
2. Create the aggregate: `storage aggregate create` (same options list as above, minus mirroring).
   Example creates an unmirrored aggregate with 10 disks:
   ```
   controller_A_1::> storage aggregate create aggr1_controller_A_1 -diskcount 10 -node controller_A_1
   [Job 15] Job is queued: Create aggr1_controller_A_1.
   [Job 15] The job is starting.
   [Job 15] Job succeeded: DONE
   ```
3. Verify the RAID group and drives of your new aggregate: `storage aggregate show-status -aggregate aggregate-name`

#### Implementing the MetroCluster configuration

You must run the `metrocluster configure` command to start data protection in a MetroCluster configuration.

Before you begin:
- There should be at least two non-root mirrored data aggregates on each cluster. Additional data aggregates can be either mirrored or unmirrored. Verify the aggregate types: `storage aggregate show`. If you want to use a single mirrored data aggregate, see the instructions below.
- The ha-config state of the controllers and chassis must be "mcc-2n".

You can issue the `metrocluster configure` command once, on any of the nodes, to enable the MetroCluster configuration. You do not need to issue the command on each of the sites or nodes, and it does not matter which node or site you choose to issue the command on.

Steps:
1. Configure the MetroCluster:

   | If your MetroCluster configuration has… | Then do this… |
   |---|---|
   | Multiple data aggregates | From any node's prompt: `metrocluster configure node-name` |
   | A single mirrored data aggregate | a. From any node's prompt, change to the advanced privilege level: `set -privilege advanced` (respond "y" when prompted). b. Configure with `metrocluster configure -allow-with-one-aggregate true node-name`. c. Return to admin privilege: `set -privilege admin` |

   The best practice is to have multiple data aggregates. If the first DR group has only one aggregate and you want to add a DR group with one aggregate, you must move the metadata volume off the single data aggregate (see Moving a metadata volume in MetroCluster configurations).

   Example enables the MetroCluster configuration on all nodes in the DR group containing "controller_A_1":
   ```
   cluster_A::*> metrocluster configure -node-name controller_A_1
   [Job 121] Job succeeded: Configure is successful.
   ```
2. Verify the networking status on site A: `network port show`
3. Verify the MetroCluster configuration from both sites: `metrocluster show`
   ```
   cluster_A::> metrocluster show
   Cluster Entry Name State
   ------------------------- ------------------- -----------
    Local: cluster_A Configuration state configured
     Mode normal
     AUSO Failure Domain auso-on-cluster-disaster
   Remote: cluster_B Configuration state configured
     Mode normal
     AUSO Failure Domain auso-on-cluster-disaster
   ```
   And from site B similarly (Local: cluster_B, Remote: cluster_A).

#### Configuring FC-to-SAS bridges for health monitoring

In systems running ONTAP versions prior to 9.8, if your configuration includes FC-to-SAS bridges, you must perform some special configuration steps to monitor the FC-to-SAS bridges in the MetroCluster configuration.

- Third-party SNMP monitoring tools are not supported for FibreBridge bridges.
- Beginning with ONTAP 9.8, FC-to-SAS bridges are monitored via in-band connections by default, and additional configuration is not required.
- Beginning with ONTAP 9.8, the `storage bridge` command is replaced with `system bridge`. The following steps show the `storage bridge` command, but if you are running ONTAP 9.8 or later, the `system bridge` command is preferred.

Steps:
1. From the ONTAP cluster prompt, add the bridge to health monitoring:
   a. Add the bridge, using the command for your version of ONTAP:

   | ONTAP version | Command |
   |---|---|
   | ONTAP 9.5 and later | `storage bridge add -address 0.0.0.0 -managed-by in-band -name bridge-name` |
   | ONTAP 9.4 and earlier | `storage bridge add -address bridge-ip-address -name bridge-name` |

   b. Verify that the bridge has been added and is properly configured: `storage bridge show`. It might take as long as 15 minutes to reflect all of the data because of the polling interval. The ONTAP health monitor can contact and monitor the bridge if the value in the "Status" column is "ok", and other information, such as the worldwide name (WWN), is displayed.

   Example showing configured FC-to-SAS bridges:
   ```
   controller_A_1::> storage bridge show
   Bridge          Symbolic Name  Is Monitored  Monitor Status  Vendor  Model              Bridge WWN
   ------------------ ------------- ------------ -------------- ------ ----------------- ----------
   ATTO_10.10.20.10   atto01         true          ok             Atto   FibreBridge 7500N  20000010867038c0
   ATTO_10.10.20.11   atto02         true          ok             Atto   FibreBridge 7500N  20000010867033c0
   ATTO_10.10.20.12   atto03         true          ok             ...
   ```

> Note: The PDF source text was truncated at this point in the extraction (end of available page content). Remaining sections of the full PDF per its table of contents — Checking for MetroCluster configuration errors with Config Advisor; Verifying switchover, healing, and switchback; Protecting configuration backup files; Considerations for using virtual IP and BGP; Testing the MetroCluster configuration (verifying negotiated switchover, healing/manual switchback, loss of a single FC-to-SAS bridge, power line disruption, loss of a single storage shelf); Remove MetroCluster configurations; Using Active IQ Unified Manager and ONTAP System Manager; Considerations when using ONTAP in a MetroCluster configuration (licensing, SnapMirror, FlexCache, FabricPool, FlexGroup support, job schedules, cluster peering to a third cluster, LDAP client configuration replication, networking/LIF guidelines, SVM disaster recovery, disk/shelf show command output nuances, NVFAIL flag); Transitioning from stretch to fabric-attached MetroCluster — were not returned by the fetch tool (content window limit) and are not included in this file. Refer to the live doc site or the individual HTML pages under https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/ for that material.
