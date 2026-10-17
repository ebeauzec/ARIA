# Detailed guide - AFF A220
Source: https://docs.netapp.com/us-en/ontap-systems/a220/install-detailed-guide.html
Fetched: 2026-07-07

This page gives detailed step-by-step instructions for installing a typical NetApp system (AFF A220).

## Step 1: Prepare for installation

To install your AFF A220 system, you need to create an account on the NetApp Support Site, register your system, and get license keys. You also need to inventory the appropriate number and type of cables for your system and collect specific network information.

You need access to the Hardware Universe (https://hwu.netapp.com) for site requirements and configuration info, and the Release Notes for your version of ONTAP.

What you need at your site: rack space, Phillips #2 screwdriver, additional networking cables, and a laptop or console with an RJ-45 connection and web browser access.

Steps:
1. Unpack the contents of all boxes.
2. Record the system serial number from the controllers.
3. Set up your account: log in or create an account, and register your system.
4. Download and install Config Advisor on your laptop.
5. Inventory cable types received, including:
   - 10 GbE cable (X6566B series) — GbE SFP copper connector — cluster interconnect network / data
   - Optical network cables (X6553-R6, X6536-R6, X6554-R6) — LC fiber connector — FC host network
   - Cat 6 RJ-45 (X6585-R6, X6562-R6) — management network and Ethernet data
   - Storage cables (X66030A/X66031A/X66032A/X66033A) — Mini-SAS to mini-SAS connector — storage
   - Micro-USB console cable — console connection during software setup
   - Power cables — powering up the system
6. Download and complete the Cluster Configuration Worksheet (https://library.netapp.com/ecm/ecm_download_file/ECMLP2839002).

## Step 2: Install the hardware

Install your system in a 4-post rack or NetApp system cabinet.

Steps:
1. Install the rail kits, as needed.
2. Install and secure your system using the rail kit instructions. Be aware of the safety concerns associated with the weight of the system.
3. Attach cable management devices.
4. Place the bezel on the front of the system.

## Step 3: Cable controllers to your network

Cable the controllers using the two-node switchless cluster method or the cluster interconnect network method, in either a unified (UTA2/FC+10GbE) or Ethernet network configuration.

### Option 1: Two-node switchless cluster, unified network configuration

Management network, UTA2 data network, and management ports connect to switches; cluster interconnect ports are cabled directly between both controllers.

Steps (per controller):
1. Cable the cluster interconnect ports to each other: e0a to e0a, e0b to e0b.
2. Cable the UTA2 data ports to your host network — as FC (0c and 0d, or 0e and 0f) or as 10GbE (e0c and e0d, or e0e and e0f). You can connect one port pair as CNA and one as FC, or both pairs as CNA or both as FC.
3. Cable the e0M ports to the management network switches with RJ45 cables.
   - Attention: Do NOT plug in the power cords at this point.

### Option 2: Switched cluster, unified network configuration

Management network, UTA2 data network, and management ports connect to switches; cluster interconnect ports connect to cluster interconnect switches.

Steps (per controller module):
1. Cable e0a and e0b to the cluster interconnect switches.
2. Cable the UTA2 data ports to your host network as FC (0c/0d or 0e/0f) or 10GbE (e0c/e0d or e0e/e0f).
3. Cable the e0M ports to the management network switches.
   - Attention: Do NOT plug in the power cords at this point.

### Option 3: Two-node switchless cluster, Ethernet network configuration

Steps (per controller):
1. Cable the cluster interconnect ports to each other: e0a to e0a, e0b to e0b.
2. Cable the e0c through e0f ports to your host network using Cat 6 RJ45 cable.
3. Cable the e0M ports to the management network switches.
   - Attention: Do NOT plug in the power cords at this point.

### Option 4: Switched cluster, Ethernet network configuration

Steps (per controller module):
1. Cable e0a and e0b to the cluster interconnect switches.
2. Cable the e0c through e0f ports to your host network using Cat 6 RJ45 cable.
3. Cable the e0M ports to the management network switches.
   - Attention: Do NOT plug in the power cords at this point.

## Step 4: Cable controllers to drive shelves

Cable the controllers to your shelves using the onboard storage ports. NetApp recommends MP-HA cabling for systems with external storage. If you have a SAS tape drive, you can use single-path cabling. If there are no external shelves, MP-HA cabling to internal drives is optional if the SAS cables were ordered with the system.

### Option 1: Cable storage on an HA pair with external drive shelves

Cable the shelf-to-shelf connections, then cable both controllers to the drive shelves (example uses DS224C; cabling is similar for other supported drive shelves):

1. Cable the shelf-to-shelf ports: port 3 on IOM A to port 1 on IOM A of the shelf directly below; port 3 on IOM B to port 1 on IOM B of the shelf directly below (mini-SAS HD to mini-SAS HD cables).
2. Connect each node to IOM A in the stack: controller 1 port 0b to IOM A port 3 on the last drive shelf in the stack; controller 2 port 0a to IOM A port 1 on the first drive shelf in the stack.
3. Connect each node to IOM B in the stack: controller 1 port 0a to IOM B port 1 on the first drive shelf in the stack; controller 2 port 0b to IOM B port 3 on the last drive shelf in the stack.

If you have more than one drive shelf stack, see the Installation and Cabling Guide for your drive shelf type.

## Step 5: Complete system setup and configuration

Complete the system setup and configuration using cluster discovery with only a connection to the switch and laptop, or by connecting directly to a controller and then to the management switch.

### Option 1: Network discovery enabled

Steps:
1. Set one or more drive shelf IDs.
2. Plug the power cords into the controller power supplies, connecting to power sources on different circuits.
3. Turn on the power switches to both nodes (initial booting may take up to eight minutes).
4. Ensure your laptop has network discovery enabled.
5. Connect your laptop to the Management switch.
6. Select an ONTAP icon to discover via File Explorer > Network > refresh; double-click and accept certificates.
7. Use System Manager guided setup to configure your system using the data from the NetApp ONTAP Configuration Guide (https://library.netapp.com/ecm/ecm_download_file/ECMLP2862613).
8. Verify system health by running Config Advisor.
9. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional feature configuration.

### Option 2: Network discovery not enabled

Steps:
1. Cable and configure your laptop or console: set console port to 115,200 baud N-8-1, connect the console cable, connect to the management subnet switch, and assign a TCP/IP address on the management subnet.
2. Set one or more drive shelf IDs.
3. Plug in power cords to different circuits and turn on both nodes (boot may take up to eight minutes).
4. Assign an initial node management IP address (via DHCP or manually through a console session with PuTTY or equivalent).
5. Using System Manager, point your browser to the node management IP address (https://x.x.x.x) and configure using the ONTAP Configuration Guide data.
6. Verify system health by running Config Advisor.
7. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional feature configuration.
