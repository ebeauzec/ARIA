# Cable the hardware - AFF A20, AFF A30, and AFF A50
Source: https://docs.netapp.com/us-en/ontap-systems/a20-30-50/install-cable.html
Fetched: 2026-07-07

After you install your AFF A20, AFF A30, or AFF A50 storage system hardware, cable the controllers to the network and shelves.

## Before you begin

Contact your network administrator for information about connecting the storage system to your network switches.

## About this task

- The cabling graphics have arrow icons showing the proper orientation (up or down) of the cable connector pull-tab when inserting a connector into a port. As you insert the connector, you should feel it click into place; if you do not feel it click, remove it, turn it over and try again.
- If cabling to an optical switch, insert the optical transceiver into the controller port before cabling to the switch port.

## Step 1: Cable the cluster/HA connections

Create the ONTAP cluster connections. For switchless clusters, connect the controllers to each other. For switched clusters, connect the controllers to the cluster network switches.

> Note: The cluster/HA cabling examples show common configurations. If you do not see your configuration here, go to NetApp Hardware Universe (https://hwu.netapp.com) for comprehensive configuration and slot priority information to cable your storage system.

### Switchless cluster cabling

Use this cabling option when the two controllers are directly connected to each other without using cluster network switches.

**AFF A30 or AFF A50 with two 2-port 40/100 GbE I/O modules** — Cable the cluster/HA interconnect ports on the I/O modules in slots 2 and 4. (The cluster interconnect traffic and the HA traffic share the same physical ports on the I/O modules in slots 2 and 4; the ports are 40/100 GbE.)

Steps:
1. Cable controller A port e2a to controller B port e2a.
2. Cable controller A port e4a to controller B port e4a.
   - Note: I/O module ports e2b and e4b are unused and available for host network connectivity.

**AFF A30 or AFF A50 with one 2-port 40/100 GbE I/O module** — Cable the cluster/HA interconnect ports on the I/O module in slot 4 (40/100 GbE, shared cluster/HA traffic).

Steps:
1. Cable controller A port e4a to controller B port e4a.
2. Cable controller A port e4b to controller B port e4b.

**AFF A20 with one 2-port 10/25 GbE I/O module** — Cable the cluster/HA interconnect ports on the I/O module in slot 4 (10/25 GbE, shared cluster/HA traffic).

Steps:
1. Cable controller A port e4a to controller B port e4a.
2. Cable controller A port e4b to controller B port e4b.

### Switched cluster cabling

Use this cabling option when the controllers connect to cluster network switches instead of being directly connected to each other.

**AFF A30 or AFF A50 with two 2-port 40/100 GbE I/O modules** — Cable the cluster/HA interconnect ports on the I/O modules in slots 2 and 4 to the cluster network switches.

Steps:
1. Cable controller A port e4a to cluster network switch A.
2. Cable controller A port e2a to cluster network switch B.
3. Cable controller B port e4a to cluster network switch A.
4. Cable controller B port e2a to cluster network switch B.
   - Note: I/O module ports e2b and e4b are unused and available for host network connectivity.

**AFF A30 or AFF A50 with one 2-port 40/100 GbE I/O module** — Cable the cluster/HA interconnect ports on the I/O module in slot 4 to the cluster network switches.

Steps:
1. Cable controller A port e4a to cluster network switch A.
2. Cable controller A port e4b to cluster network switch B.
3. Cable controller B port e4a to cluster network switch A.
4. Cable controller B port e4b to cluster network switch B.

**AFF A20 with one 2-port 10/25 GbE I/O module** — Cable the cluster/HA interconnect ports on the I/O module in slot 4 to the cluster network switches.

Steps:
1. Cable controller A port e4a to cluster network switch A.
2. Cable controller A port e4b to cluster network switch B.
3. Cable controller B port e4a to cluster network switch A.
4. Cable controller B port e4b to cluster network switch B.

## Step 2: Cable the host network connections

Cable the controllers to your Ethernet or FC host network.

> Note: The host network cabling examples show common configurations. If you do not see your configuration here, go to NetApp Hardware Universe (https://hwu.netapp.com) for comprehensive configuration and slot priority information.

### Ethernet host cabling

**AFF A30 or AFF A50 with two 2-port 40/100 GbE I/O modules** — On each controller, cable ports e2b and e4b to the Ethernet host network switches. (Ports on I/O modules in slot 2 and 4 are 40/100 GbE.)

**AFF A20, AFF A30, or AFF A50 with one 4-port 10/25 GbE I/O module** — On each controller, cable ports e2a, e2b, e2c and e2d to the Ethernet host network switches.

### FC host cabling

**AFF A20, AFF A30, or AFF A50 with one 4-port 64 Gb/s FC I/O module** — On each controller, cable ports 2a, 2b, 2c and 2d to the FC host network switches.

## Step 3: Cable the management network connections

Cable the management (wrench) ports on each controller to the management network switches using 1000BASE-T RJ-45 cables.

> Important: Do not plug in the power cords yet.

## Step 4: Cable the shelf connections

This procedure shows you how to cable the controllers to one NS224 shelf.

About this task:
- For the maximum number of shelves supported for your storage system and for all cabling options (optical and switch-attached), see NetApp Hardware Universe (https://hwu.netapp.com).
- The NS224 shelf cabling procedure shows NSM100B modules instead of NSM100 modules. The cabling is the same regardless of the type of NSM modules used, only the port names differ:
  - NSM100B modules use ports e1a and e1b on an I/O module in slot 1.
  - NSM100 modules use built-in (onboard) ports e0a and e0b.
- You cable each controller to each NSM module on the NS224 shelf using the storage cables that came with your storage system (100 GbE QSFP28 copper cables).
- Controller A cabling is shown in blue and controller B cabling in yellow in the diagrams.

Steps:
1. Cable controller A port e3a to NSM A port e1a.
2. Cable controller A port e3b to NSM B port e1b.
3. Cable controller B port e3a to NSM B port e1a.
4. Cable controller B port e3b to NSM A port e1b.

## What's next?

After you've cabled the hardware for your storage system, power on the storage system: https://docs.netapp.com/us-en/ontap-systems/a20-30-50/install-power-hardware.html
