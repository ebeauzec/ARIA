# Detailed guide - FAS9000
Source: https://docs.netapp.com/us-en/ontap-systems/fas9000/install-detailed-guide.html
Fetched: 2026-07-07

This guide gives detailed step-by-step instructions for installing a typical NetApp system (FAS9000, shares chassis/cabling with AFF A700).

## Step 1: Prepare for installation

Create an account on the NetApp Support Site, register your system, and get license keys. Inventory the appropriate number and type of cables and collect specific network information.

Access needed: Hardware Universe (https://hwu.netapp.com) for site requirements and configuration info; Release Notes for your version of ONTAP.

At your site you need: rack space, Phillips #2 screwdriver, additional networking cables.

Steps:
1. Unpack the contents of all boxes.
2. Record the system serial number from the controllers.
3. Inventory cable types received:
   - 10 GbE network cable (X6566B series) — GbE SFP copper connector — network cable
   - 40 GbE network/cluster interconnect cable (X66100-1/3) — 100 GbE QSFP28 connector — 40 GbE network / cluster interconnect
   - 100 GbE network/storage cable (X66211A series) — 100 GbE QSFP28 connector — network/storage cable (applies to AFF A700 only)
   - Optical network cables (X6553-R6, X6536-R6) — LC fiber connector — FC host network
   - Cat 6 RJ-45 (X6585-R6, X6562-R6) — management network and Ethernet data
   - Storage cables (X66031A/X66032A/X66033A) — Mini-SAS to mini-SAS connector — storage
   - Micro-USB console cable — console connection during software setup
   - Power cables — powering up the system
4. Review the NetApp ONTAP Configuration Guide (https://library.netapp.com/ecm/ecm_download_file/ECMLP2862613) and collect required information.

## Step 2: Install the hardware

Install your system in a 4-post rack or NetApp system cabinet.

Steps:
1. Install the rail kits, as needed.
2. Install and secure your system using the rail kit instructions (be aware of weight safety concerns — the label differs for an empty chassis vs. fully-populated system).
3. Attach cable management devices.
4. Place the bezel on the front of the system.

## Step 3: Cable controllers to your network

Cable the controllers using the two-node switchless cluster method or the cluster interconnect network.

### Option 1: Two-node switchless cluster

Management network, data network, and management ports connect to switches; cluster interconnect ports are cabled directly between both controllers. Cable pull-tabs are up for all networking module ports. Contact your network administrator for switch connection info.

### Option 2: Switched cluster

Management network, data network, and management ports connect to switches; cluster interconnect and HA ports are cabled to the cluster/HA switch.

After either option, proceed to Step 4 for drive shelf cabling.

## Step 4: Cable controllers to drive shelves

Cable your new system to DS212C, DS224C, or NS224 shelves, depending on whether it is an AFF or FAS system.

### Option 1: Cable the controllers to DS212C or DS224C drive shelves

Cable the shelf-to-shelf connections, then cable both controllers to the drive shelves. Cables are inserted into the drive shelf with pull-tabs facing down; controller storage module ends have pull-tabs up. Cabling for SAS shelves in FAS9000, AFF A700, and ASA AFF A700 differs slightly between ONTAP 9.7 and earlier vs. 9.8 and later. If you have more than one drive shelf stack, see the Installation and Cabling Guide for your drive shelf type.

### Option 2: Cable the controllers to a single NS224 drive shelf (ASA AFF A700, ONTAP 9.8+ only)

Applies only to ASA AFF A700 running ONTAP 9.8 or later. Systems must have at least one X91148A module installed in slots 3 and/or 7 per controller.

### Option 3: Cable the controllers to two NS224 drive shelves (ASA AFF A700, ONTAP 9.8+ only)

Applies only to ASA AFF A700 running ONTAP 9.8 or later. Systems must have two X91148A modules per controller, installed in slots 3 and 7.

## Step 5: Complete system setup and configuration

### Option 1: Network discovery enabled

Steps:
1. Set drive shelf IDs (NS224 shelves pre-set to shelf ID 00/01).
2. Plug power cords into the controller power supplies, connecting to power sources on different circuits.
3. Turn on both nodes (boot may take up to eight minutes).
4. Ensure your laptop has network discovery enabled.
5. Connect your laptop to the Management switch.
6. Select an ONTAP icon to discover via File Explorer > Network > refresh; accept certificates.
7. Use System Manager guided setup to configure your system using the ONTAP Configuration Guide data.
8. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
9. Verify system health with Config Advisor.
10. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional features.

### Option 2: Network discovery not enabled

Steps:
1. Cable and configure your laptop/console (115,200 baud N-8-1 console port; connect console cable; connect to management subnet switch; assign TCP/IP address on management subnet).
2. Set drive shelf IDs.
3. Plug in power cords to different circuits and power on both nodes (boot up to eight minutes).
4. Assign an initial node management IP address (via DHCP or manually via console session).
5. Using System Manager, point your browser to the node management IP address (https://x.x.x.x) and configure using ONTAP Configuration Guide data.
6. Set up your NetApp Support account, register your system, and download Active IQ Config Advisor.
7. Verify system health with Config Advisor.
8. After initial configuration, go to ONTAP 9 documentation (https://docs.netapp.com/us-en/ontap/index.html) for additional features.
