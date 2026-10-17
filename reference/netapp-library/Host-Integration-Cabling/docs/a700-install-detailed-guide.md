# Detailed guide - AFF A700
Source: https://docs.netapp.com/us-en/ontap-systems/a700/install-detailed-guide.html
Fetched: 2026-07-07

This guide gives detailed step-by-step instructions for installing a typical NetApp system. Use this guide if you want more detailed installation instructions.

## Step 1: Prepare for installation

To install your system, you need to create an account on the NetApp Support Site, register your system, and get license keys. You also need to inventory the appropriate number and type of cables for your system and collect specific network information.

Before you begin: You need access to the Hardware Universe (https://hwu.netapp.com) for site requirements and configuration info, and the Release Notes for your version of ONTAP.

You need to provide at your site: rack space for the storage system, a Phillips #2 screwdriver, and additional networking cables to connect your system to your network switch and laptop/console with a web browser.

Steps:
1. Unpack the contents of all boxes.
2. Record the system serial number from the controllers.
3. Inventory and note the number and types of cables received. Cable types include:
   - 10 GbE network cable (X6566B-2/3/5-R6) — GbE SFP copper connector — network cable
   - 40 GbE network/cluster interconnect cable (X66100-1/3) — 100 GbE QSFP28 connector — 40 GbE network/cluster interconnect
   - 100 GbE network/storage cable (X66211A series) — 100 GbE QSFP28 connector — network/storage cable (AFF A700 only)
   - Optical network cables (X6553-R6, X6536-R6) — LC fiber connector — FC host network
   - Cat 6 RJ-45 (X6585-R6, X6562-R6) — RJ-45 connector — management network and Ethernet data
   - Storage cables (X66031A/X66032A/X66033A) — Mini-SAS to mini-SAS connector — storage
   - Micro-USB console cable — console connection during software setup on non-Windows/Mac laptop
   - Power cables — powering up the system
4. Review the NetApp ONTAP Configuration Guide (https://library.netapp.com/ecm/ecm_download_file/ECMLP2862613) and collect the required information listed in that guide.

## Step 2: Install the hardware

You need to install your system in a 4-post rack or NetApp system cabinet, as applicable.

Steps:
1. Install the rail kits, as needed.
2. Install and secure your system using the instructions included with the rail kit. Be aware of the safety concerns associated with the weight of the system.
3. Attach cable management devices.
4. Place the bezel on the front of the system.

## Step 3: Cable controllers to your network

You can cable the controllers to your network using the two-node switchless cluster method or by using the cluster interconnect network.

### Option 1: Two-node switchless cluster

Management network, data network, and management ports on the controllers are connected to switches. The cluster interconnect ports are cabled between both controllers directly. Contact your network administrator for switch connection info. Cable pull-tabs are up for all networking module ports; you should feel the connector click into place.

### Option 2: Switched cluster

Management network, data network, and management ports on the controllers are connected to switches. The cluster interconnect and HA ports are cabled to the cluster/HA switch.

After either option, proceed to Step 4 for drive shelf cabling.

## Step 4: Cable controllers to drive shelves

You can cable your new system to DS212C, DS224C, or NS224 shelves, depending on whether it is an AFF or FAS system.

### Option 1: Cable the controllers to DS212C or DS224C drive shelves

Cable the shelf-to-shelf connections, then cable both controllers to the DS212C or DS224C drive shelves. Cables are inserted into the drive shelf with pull-tabs facing down; the other end into the controller storage modules with pull-tabs up. Cabling for SAS shelves in FAS9000, AFF A700, and ASA AFF A700 differs slightly between ONTAP 9.7 and earlier vs. ONTAP 9.8 and later. If you have more than one drive shelf stack, see the Installation and Cabling Guide for your drive shelf type (e.g., shelves with IOM12 modules: https://docs.netapp.com/us-en/ontap-systems/sas3/install-new-system.html).

### Option 2: Cable the controllers to a single NS224 drive shelf (AFF A700/ASA AFF A700, ONTAP 9.8+ only)

Applies only to AFF A700 and ASA AFF A700 running ONTAP 9.8 or later. Systems must have at least one X91148A module installed in slots 3 and/or 7 for each controller. Cable pull-tabs for storage modules are up; pull-tabs on the shelves are down.

### Option 3: Cable the controllers to two NS224 drive shelves (AFF A700/ASA AFF A700, ONTAP 9.8+ only)

Applies only to AFF A700 and ASA AFF A700 running ONTAP 9.8 or later. Systems must have two X91148A modules per controller, installed in slots 3 and 7.

## Step 5: Complete system setup and configuration

You can complete system setup and configuration using cluster discovery with only a connection to the switch and laptop, or by connecting directly to a controller and then to the management switch.

### Option 1: Network discovery enabled

Steps:
1. Set drive shelf IDs (NS224 shelves are pre-set to shelf ID 00 and 01).
2. Plug the power cords into the controller power supplies, connecting them to power sources on different circuits.
3. Turn on the power switches to both nodes (initial booting may take up to eight minutes).
4. Ensure your laptop has network discovery enabled.
5. Connect your laptop to the Management switch.
6. Select an ONTAP icon to discover in File Explorer > Network, and accept any certificates displayed.
7. Use System Manager guided setup to configure your system using the data collected in the ONTAP Configuration Guide.
8. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
9. Verify the health of your system by running Config Advisor.
10. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for configuring additional features.

### Option 2: Network discovery not enabled

Steps:
1. Cable and configure your laptop or console: set console port to 115,200 baud with N-8-1, connect the console cable, connect the laptop to the management switch, and assign a TCP/IP address on the management subnet.
2. Set drive shelf IDs.
3. Plug in power cords to different circuits and power on both nodes (boot may take up to eight minutes).
4. Assign an initial node management IP address to one of the nodes (via DHCP or manually through a console session).
5. Using System Manager on your laptop/console, point your browser to the node management IP address (https://x.x.x.x) and configure the system using the data from the ONTAP Configuration Guide.
6. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
7. Verify system health by running Config Advisor.
8. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for configuring additional features.
