# Detailed guide - FAS8300 and FAS8700
Source: https://docs.netapp.com/us-en/ontap-systems/fas8300/install-detailed-guide.html
Fetched: 2026-07-07

This guide gives detailed step-by-step instructions for installing a typical NetApp system (FAS8300 and FAS8700).

## Step 1: Prepare for installation

Create an account, register the system, and get license keys. Inventory cables and collect network information.

Access needed: Hardware Universe (https://hwu.netapp.com); Release Notes for your version of ONTAP.

At your site you need: rack space, Phillips #2 screwdriver, additional networking cables.

Steps:
1. Unpack the contents of all boxes.
2. Record the system serial number from the controllers.
3. Inventory cable types received:
   - 100 GbE cable (QSFP28, X66211A series) — storage, cluster interconnect/HA, and Ethernet data (order-dependent)
   - 25 GbE cable (SFP28, X66240 series) — GbE network connection (order-dependent)
   - 32 Gb FC (SFP+, X66250 series) — FC network connection
   - Storage cables (X66030A/X66031A/X66032A/X66033A) — Mini-SAS HD to mini-SAS HD (order-dependent)
   - Optical cables (X66250-2-N-C) — LC fiber connector — 16 Gb FC or 25GbE cables for mezzanine cards (order-dependent)
   - RJ-45 (X6585-R6, X6562-R6) — management network
   - Micro-USB console cable — console connection during software setup if laptop/console does not support network discovery
   - Power cables — powering up the system
4. Review the NetApp ONTAP Configuration Guide (https://library.netapp.com/ecm/ecm_download_file/ECMLP2862613) and collect required information.

## Step 2: Install the hardware

Install your system in a 4-post rack or NetApp system cabinet.

Steps:
1. Install the rail kits, as needed.
2. Install and secure your system using the rail kit instructions (be aware of weight safety concerns).
3. Attach cable management devices.
4. Place the bezel on the front of the system.

## Step 3: Cable controllers to your network

Cable the controllers using the two-node switchless cluster method or the cluster interconnect network.

> Note: If the port labels on the card are not visible, check the card installation orientation (the PCIe connector socket is on the left side of the card slot in the A400 and FAS8300/8700), then look up the card by part number in the NetApp Hardware Universe (https://hwu.netapp.com) for a graphic showing port labels. The card part number can be found using the `sysconfig -a` command or on the system packing list.

### Option 1: Cable a two-node switchless cluster

The optional data ports, optional NIC cards, and management ports on the controller modules connect to switches. The cluster interconnect and HA ports are cabled directly between both controller modules. Cable pull-tabs are up for onboard ports and down for expansion (NIC) cards. Contact your network administrator for switch connection info.

### Option 2: Cable a switched cluster

The optional data ports, optional NIC cards, mezzanine cards, and management ports on the controller modules connect to switches. The cluster interconnect and HA ports are cabled to the cluster/HA switch.

## Step 4: Cable controllers to drive shelves

### Option 1: Cable the controllers to SAS drive shelves

Cable each controller to the IOM modules on both SAS drive shelves. Cable pull-tabs for the DS224-C are down.

## Step 5: Complete system setup and configuration

### Option 1: Network discovery enabled

Steps:
1. Set one or more drive shelf IDs.
2. Plug the power cords into the controller power supplies, connecting to power sources on different circuits.
3. Ensure your laptop has network discovery enabled.
4. Connect your laptop to the Management switch.
5. Select an ONTAP icon to discover via File Explorer > Network > refresh; accept certificates.
6. Use System Manager guided setup to configure your system using the ONTAP Configuration Guide data.
7. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
8. Verify system health with Config Advisor.
9. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional features.

### Option 2: Network discovery not enabled

Steps:
1. Cable and configure your laptop/console (115,200 baud N-8-1 console port; connect console cable; connect to management subnet switch; assign TCP/IP address on management subnet).
2. Set one or more drive shelf IDs.
3. Plug the power cords into the controller power supplies, connecting to power sources on different circuits (initial booting may take up to eight minutes).
4. Assign an initial node management IP address (via DHCP or manually via console session with PuTTY or equivalent).
5. Using System Manager, point your browser to the node management IP address (https://x.x.x.x) and configure using ONTAP Configuration Guide data.
6. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
7. Verify system health with Config Advisor.
8. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional features.
