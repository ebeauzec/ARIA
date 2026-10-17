# Detailed steps - AFF A800
Source: https://docs.netapp.com/us-en/ontap-systems/a800/install-detailed-guide.html
Fetched: 2026-07-07

This section gives detailed step-by-step instructions for installing an AFF A800 system.

## Step 1: Prepare for installation

To install your AFF A800 system, you need to create an account and register the system. You also need to inventory the appropriate number and type of cables for your system and collect specific network information.

You need access to the NetApp Hardware Universe (https://hwu.netapp.com) for site requirements and configuration info, and the Release Notes for your version of ONTAP.

What you need at your site:
- Rack space for the storage system: 4U in an HA configuration for the platform; 2U for each NS224 storage shelf
- Phillips #2 screwdriver
- Additional networking cables to connect your system to your network switch and laptop or console with a web browser

Steps:
1. Set up your account: log in or create an account, and register your system (NetApp Product Registration).
2. Download and install Config Advisor on your laptop.
3. Inventory and note the number and types of cables received, including:
   - 100 GbE cable (X66211A series) — QSFP28 connector — HA interconnect, cluster interconnect network, storage/data
   - 10 GbE cable (X6566B-3/5-R6) — data
   - 25 GbE cable (X66240A series) — data
   - RJ-45 — management
   - Fibre Channel (X66250 series) — network
   - Micro-USB console cable — console connection during software setup
   - Power cables — connecting the PSUs to power source
4. Download and complete the Cluster Configuration Worksheet (https://library.netapp.com/ecm/ecm_download_file/ECMLP2839002).

## Step 2: Install the hardware

Install your system in a 4-post rack or NetApp system cabinet.

Steps:
1. Install the rail kits (see Installing SuperRail into a four-post rack).
2. Install and secure your system using the rail kit instructions. Be aware of the safety concerns associated with the weight of the system.
3. Attach cable management devices.
4. Place the bezel on the front of the system.

## Step 3: Cable controllers

There is required cabling for your platform's cluster using the two-node switchless cluster method or the cluster interconnect network method. There is optional cabling to the Fibre Channel or iSCSI host networks or direct-attached storage. This cabling is not exclusive; you can cable to a host network and storage.

### Required cabling: Cable controllers to a cluster

#### Option 1: Cable a two-node switchless cluster

Management network ports on the controllers are connected to switches. The HA interconnect and cluster interconnect ports are cabled on both controllers. Contact your network administrator for switch connection info.

Steps (per controller module):
1. Cable the HA interconnect ports: e0b to e0b, e1b to e1b.
2. Cable the cluster interconnect ports: e0a to e0a, e1a to e1a.
3. Cable the management ports to the management network switches.
   - Attention: Do NOT plug in the power cords at this point.

#### Option 2: Cable a switched cluster

Cluster interconnect and management network ports on the controllers are connected to switches while the HA interconnect ports are cabled on both controllers.

Steps (per controller module):
1. Cable the HA interconnect ports: e0b to e0b, e1b to e1b.
2. Cable the cluster interconnect ports (e0a, e1a) to the 100 GbE cluster interconnect switches.
3. Cable the management ports to the management network switches.
   - Attention: Do NOT plug in the power cords at this point.

### Optional cabling: Cable configuration-dependent options

#### Option 1: Cable to a Fibre Channel host network

Cable ports 2a through 2d on each controller to the FC host switches.

#### Option 2: Cable to a 10GbE host network

Cable ports e4a through e4d on each controller to the 10GbE host network switches.

#### Option 3: Cable the controllers to a single drive shelf

Cable each controller to the NSM modules on the NS224 drive shelf (controller A to the shelf, then controller B to the shelf).

#### Option 4: Cable the controllers to two drive shelves

Cable each controller to the NSM modules on both NS224 drive shelves (controller A to the shelves, then controller B to the shelves).

## Step 4: Complete system setup and configuration

Complete the system setup and configuration using cluster discovery with only a connection to the switch and laptop, or by connecting directly to a controller and then to the management switch.

### Option 1: Network discovery enabled

Steps:
1. Plug the power cords into the controller power supplies, connecting to power sources on different circuits (boot may take up to eight minutes).
2. Ensure your laptop has network discovery enabled.
3. Connect your laptop to the Management switch.
4. Select an ONTAP icon to discover via File Explorer > Network > refresh; double-click the ONTAP icon and accept certificates.
5. Use System Manager guided setup to configure your system using the data from the ONTAP Configuration Guide (https://library.netapp.com/ecm/ecm_download_file/ECMLP2862613).
6. Verify system health by running Config Advisor.
7. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional feature configuration.

### Option 2: Network discovery not enabled

Steps:
1. Cable and configure your laptop or console: set console port to 115,200 baud N-8-1, connect the console cable to the controller, connect the laptop/console to the management subnet switch, and assign a TCP/IP address on the management subnet.
2. Plug in power cords to different circuits (boot may take up to eight minutes).
3. Assign an initial node management IP address (via DHCP or manually through a console session with PuTTY or equivalent).
4. Using System Manager, point your browser to the node management IP address (https://x.x.x.x) and configure the system using the ONTAP Configuration Guide data.
5. Verify system health by running Config Advisor.
6. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional feature configuration.
