# Install FC-to-SAS bridges and SAS disk shelves
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/task_fb_new_install.html
Fetched: 2026-07-07

Install and cable ATTO FibreBridge bridges and SAS disk shelves when you add new storage to the configuration.

## About this task

For systems received from the factory, the FC-to-SAS bridges are preconfigured and do not require additional configuration.

This procedure is written with the assumption that you are using the recommended bridge management interfaces: the ATTO ExpressNAV GUI and ATTO QuickNAV utility.

You use the ATTO ExpressNAV GUI to configure and manage a bridge, and to update the bridge firmware. You use the ATTO QuickNAV utility to configure the bridge Ethernet management 1 port.

You can use other management interfaces instead, if needed, such as a serial port or Telnet to configure and manage a bridge and to configure the Ethernet management 1 port, and FTP to update the bridge firmware.

## In-band management of the FC-to-SAS bridges

Beginning with ONTAP 9.5 with FibreBridge 7500N or 7600N bridges, *in-band management* of the bridges is supported as an alternative to IP management of the bridges. Beginning with ONTAP 9.8, out-of-band management is deprecated.

> **Note:** Beginning with ONTAP 9.8, the `storage bridge` command is replaced with `system bridge`. The following steps show the `storage bridge` command, but if you are running ONTAP 9.8 or later, the `system bridge` command is preferred.

When using in-band management, the bridges can be managed and monitored from the ONTAP CLI using the FC connection to the bridge. Physical access to the bridge through the bridge Ethernet ports is not required, reducing the security vulnerability of the bridge.

The availability of in-band management of the bridges depends on the version of ONTAP:
- Beginning with ONTAP 9.8, bridges are managed via in-band connections by default and out-of-band management of the bridges via SNMP is deprecated.
- ONTAP 9.5 through 9.7: Either in-band management or out-of-band SNMP management is supported.
- Before ONTAP 9.5, only out-of-band SNMP management is supported.

Bridge CLI commands can be issued from the ONTAP interface: `storage bridge run-cli -name <bridge_name> -command <bridge_command_name>`.

> **Note:** Using in-band management with IP access disabled is recommended to improve security by limiting physical connectivity the bridge.

## FibreBridge 7600N and 7500N bridge limits and attachment rules

FibreBridge 7600N and 7500N bridge limits:
- The maximum number of HDD and SSD drives combined is 240.
- The maximum number of SSD drives is 96.
- The maximum number of SSDs per SAS port is 48.
- The maximum number of shelves per SAS port is 10.

FibreBridge 7600N and 7500N bridge attachment rules:
- Do not mix SSD and HDD drives on the same SAS port.
- Distribute the shelves evenly across the SAS ports.
- You shouldn't have DS460 shelves on the same SAS port as other shelf types (for example, DS212 or DS224 shelves).

Example configuration — connecting four DS224 shelves with SSD drives and six DS224 shelves with HDD drives:

| SAS port | Shelves and drives |
|---|---|
| SAS port-A | 2x DS224 shelves with SSD drives |
| SAS port-B | 2x DS224 shelves with SSD drives |
| SAS port-C | 3x DS224 shelves with HDD drives |
| SAS port-D | 3x DS224 shelves with HDD drives |

## Prepare for the installation

Before you begin:
- Your system must already be installed in a rack if it was not shipped in a system cabinet.
- Your configuration must be using supported hardware models and software versions. In the NetApp Interoperability Matrix Tool (IMT), use the **Storage Solution** field to select your MetroCluster solution, the **Component Explorer** to select components and ONTAP version, and **Show Results** to display supported configurations.
- Each FC controller must have one FC port available for one bridge to connect to it.
- You must be familiar with how to handle SAS cables and the considerations and best practices for installing and cabling disk shelves (see the *Installation and Service Guide* for your disk shelf model).
- The computer you are using to set up the bridges must be running an ATTO-supported web browser to use the ATTO ExpressNAV GUI (see the *ATTO Product Release Notes* on the ATTO web site for supported browsers).

Steps:
1. Download the *Installation and Service Guide* for your disk shelf model:
   1. Access the ATTO web site using the link provided for your FibreBridge model and download the manual and the QuickNAV utility.
      (The *ATTO FibreBridge Installation and Operation Manual* for your model bridge has more information about management interfaces.)
2. Gather the hardware and information needed to use the recommended bridge management interfaces (ATTO ExpressNAV GUI and ATTO QuickNAV utility):
   1. Determine a non-default user name and password (for accessing the bridges). You should change the default user name and password.
   2. If configuring for IP management of the bridges, you need the shielded Ethernet cable provided with the bridges (which connects from the bridge Ethernet management 1 port to your network).
   3. If configuring for IP management of the bridges, you need an IP address, subnet mask, and gateway information for the Ethernet management 1 port on each bridge.
   4. Disable VPN clients on the computer you are using for setup. Active VPN clients cause the QuickNAV scan for bridges to fail.

## Install the FC-to-SAS bridge and SAS shelves

About this task:
- The disk and shelf configuration at both sites should be identical. If a non-mirrored aggregate is used, the disk and shelf configuration at each site might be different.
  > **Note:** All disks in the disaster recovery group must use the same type of connection and be visible to all of the nodes within the disaster recovery group, regardless of the disks being used for mirrored or non-mirrored aggregate.
- The system connectivity requirements for maximum distances for disk shelves, FC controllers, and backup tape devices using 50-micron, multimode fiber-optic cables, also apply to FibreBridge bridges. See [NetApp Hardware Universe](https://hwu.netapp.com).

> **Note:** In-band ACP is supported without additional cabling in the following shelves and FibreBridge 7500N or 7600N bridge: IOM12 (DS460C) behind a 7500N or 7600N bridge with ONTAP 9.2 and later; IOM12 (DS212C and DS224C) behind a 7500N or 7600N bridge with ONTAP 9.1 and later.

> **Note:** SAS shelves in MetroCluster configurations do not support ACP cabling.

### Enable IP port access on the FibreBridge 7600N bridge if necessary

If you are using an ONTAP version prior to 9.5, or otherwise plan to use out-of-band access to the FibreBridge 7600N bridge using telnet or other IP port protocols and services (FTP, ExpressNAV, ICMP, or QuickNAV), you can enable the access services via the console port.

About this task: Unlike the ATTO FibreBridge 7500N bridges, the FibreBridge 7600N bridge is shipped with all IP port protocols and services disabled. Beginning with ONTAP 9.5, in-band management is supported (bridges configured/monitored from ONTAP CLI via the FC connection; physical access via bridge Ethernet ports not required). Beginning with ONTAP 9.8, in-band management is supported by default and out-of-band SNMP management is deprecated.

This task is required only if you are **not** using in-band management to manage the bridges.

Steps:
1. Access the bridge console interface by connecting a serial cable to the serial port on the FibreBridge 7600N bridge.
2. Using the console, enable the access services, and then save the configuration:
   `set closeport none`
   `saveconfiguration`
   The `set closeport none` command enables all access services on the bridge.
3. Disable a service, if desired, by issuing the `set closeport service` command repeatedly until all desired services are disabled. The `service` parameter can be one of: expressnav, ftp, icmp, quicknav, snmp, telnet. Check whether a specific protocol is enabled or disabled with `get closeport`.
4. If you are enabling SNMP, you must also issue: `set SNMP enabled`. SNMP is the only protocol that requires a separate enable command.
5. Save the configuration: `saveconfiguration`

### Configure the FC-to-SAS bridges

Before cabling your model of the FC-to-SAS bridges, you must configure the settings in the FibreBridge software.

Before you begin: decide whether you will be using in-band management of the bridges.

> **Note:** Beginning with ONTAP 9.8, the `storage bridge` command is replaced with `system bridge`. If you are running ONTAP 9.8 or later, the `system bridge` command is preferred.

If you will be using in-band management rather than IP management, the steps for configuring the Ethernet port and IP settings can be skipped, as noted in the relevant steps.

Steps:
1. Configure the serial console port on the ATTO FibreBridge by setting the port speed to 115000 baud:
   ```
   get serialportbaudrate
   SerialPortBaudRate = 115200
   Ready.
   set serialportbaudrate 115200
   Ready. *
   saveconfiguration
   Restart is necessary....
   Do you wish to restart (y/n) ? y
   ```
2. If configuring for in-band management, connect a cable from FibreBridge RS-232 serial port to the serial (COM) port on a personal computer. The serial connection is used for initial configuration; then in-band management via ONTAP and the FC ports can be used to monitor and manage the bridge.
3. If configuring for IP management, connect the Ethernet management 1 port on each bridge to your network by using an Ethernet cable.
4. If configuring for IP management, configure the Ethernet management 1 port for each bridge per section 2.0 of the *ATTO FibreBridge Installation and Operation Manual* for your bridge model. (Running QuickNAV only configures the Ethernet management port that is connected by the Ethernet cable.)
5. Configure the bridge. Note the user name and password you designate.
   > **Note:** Do not configure time synchronization on ATTO FibreBridge 7600N or 7500N — it is set to cluster time after discovery by ONTAP and synchronized daily. The time zone used is GMT and is not changeable.
   1. If configuring for IP management, configure the IP settings of the bridge (requires a serial connection if not using QuickNAV):
      ```
      set ipaddress mp1 ip-address
      set ipsubnetmask mp1 subnet-mask
      set ipgateway mp1 x.x.x.x
      set ipdhcp mp1 disabled
      set ethernetspeed mp1 1000
      ```
   2. Configure the bridge name (each bridge needs a unique name within the MetroCluster configuration). Example names for one stack group on each site: bridge_A_1a, bridge_A_1b, bridge_B_1a, bridge_B_1b.
      CLI: `set bridgename <bridge_name>`
   3. If running ONTAP 9.4 or earlier, enable SNMP on the bridge: `set SNMP enabled`.
6. Configure the bridge FC ports.
   1. Configure the data rate/speed of the bridge FC ports (FibreBridge 7600N supports up to 32/16/8 Gbps; FibreBridge 7500N supports up to 16/8/4 Gbps).
      > **Note:** The FCDataRate speed you select is limited to the maximum speed supported by both the bridge and the FC port of the controller module to which the bridge port connects. Cabling distances must not exceed SFP/hardware limitations.
      CLI: `set FCDataRate <port-number> <port-speed>`
   2. If configuring a FibreBridge 7500N bridge, set the connection mode for the port to "ptp" (not required for 7600N).
      CLI: `set FCConnMode <port-number> ptp`
   3. If configuring a FibreBridge 7600N or 7500N bridge, configure or disable the FC2 port. If not using the second port, disable it:
      `FCPortDisable <port-number>`
      Example:
      ```
      FCPortDisable 2
      Fibre Channel Port 2 has been disabled.
      ```
   4. If configuring a FibreBridge 7600N or 7500N bridge, disable unused SAS ports: `SASPortDisable sas-port`. SAS ports A–D are enabled by default; disable unused ones.
      Example (disabling port B; repeat similarly for C and D):
      ```
      SASPortDisable b
      SAS Port B has been disabled.
      ```
7. Secure access to the bridge and save the bridge's configuration:

   | ONTAP version | Steps |
   |---|---|
   | **ONTAP 9.5 or later** | View bridge status: `storage bridge show`. Secure the bridge: `securebridge` |
   | **ONTAP 9.4 or earlier** | View bridge status: `storage bridge show`. Check unsecured bridge's port status: `info` (shows Ethernet ports MP1/MP2). If MP1 enabled: `set EthernetPort mp1 disabled` (repeat for MP2 if needed). Save configuration: `SaveConfiguration` then `FirmwareRestart`. You are prompted to restart the bridge. |

8. After completing MetroCluster configuration, use the `flashimages` command to check your FibreBridge firmware version and update if not the latest supported version.

### Cable a FibreBridge 7600N or 7500N bridge with disk shelves using IOM12 modules

Steps:
1. Daisy-chain the disk shelves in each stack:
   1. Beginning with the logical first shelf in the stack, connect IOM A port 3 to IOM A port 1 on the next shelf until each IOM A in the stack is connected.
   2. Repeat for IOM B.
   3. Repeat for each stack.
2. Power on the disk shelves, and then set the shelf IDs. You must power-cycle each disk shelf. Shelf IDs must be unique for each SAS disk shelf within each MetroCluster DR group (including both sites).
3. Cable disk shelves to the FibreBridge bridges:
   1. For the first stack, cable IOM A of the first shelf to SAS port A on FibreBridge A, and cable IOM B of the last shelf to SAS port A on FibreBridge B.
   2. For additional shelf stacks, repeat using the next available SAS port (port B for the second stack, port C for the third, port D for the fourth).
   3. Attach stacks based on IOM12 modules to the same bridge as long as they are connected to separate SAS ports.
      > **Note:** Each stack can use different models of IOM, but all disk shelves within a stack must use the same model.

### Verify bridge connectivity and cable the FC-to-SAS bridges to the controller FC ports

Steps:
1. Verify that each bridge can detect all disk drives and disk shelves connected to it: `sastargets`. Output shows devices (disks and disk shelves) connected to the bridge, sequentially numbered.

   Example output (10 disks connected):
   ```
   Tgt VendorID ProductID        Type        SerialNumber
     0 NETAPP   X410_S15K6288A15 DISK        3QP1CLE300009940UHJV
     1 NETAPP   X410_S15K6288A15 DISK        3QP1ELF600009940V1BV
     ...
   ```
2. Verify the output shows the bridge is connected to the correct disks/shelves in the stack. If not correct, check for loose SAS cables or recable the disk shelves to the bridges, then repeat step 1.
3. Cable each bridge to the controller FC ports:
   1. Cable FC port 1 of the bridge to an FC port on the controller in cluster_A.
   2. Cable FC port 2 of the bridge to an FC port on the controller in cluster_B.
      - If the controller has a quad-port FC adapter, ensure bridges at either end of the storage stack are not connected to two FC ports on the same ASIC (e.g., port a/b share an ASIC, port c/d share an ASIC — connect FC_bridge_A_1 to port a and FC_bridge_A2 to port c).
      - If the controller has more than one FC adapter, do not cable bridges at either end of the storage stack to the same adapter (connect FC_bridge_A_1 to an onboard FC port and FC_bridge_A_2 to an FC port on an expansion adapter).
4. Repeat step 3 for all remaining bridges.

## Secure or unsecure the FibreBridge bridge

Beginning with ONTAP 9.5 you can secure a bridge to disable potentially unsecure Ethernet protocols (this disables the bridge's Ethernet ports). You can also reenable Ethernet access.

About this task:
- Securing the bridge disables telnet and other IP port protocols and services (FTP, ExpressNAV, ICMP, or QuickNAV) on the bridge.
- This procedure uses out-of-band management via the ONTAP prompt (available beginning with ONTAP 9.5). You can also issue commands from the bridge CLI if not using out-of-band management.
- The `unsecurebridge` command re-enables the Ethernet ports.
- In ONTAP 9.7 and earlier, running `securebridge` on the ATTO FibreBridge might not update the bridge status correctly on the partner cluster — if this occurs, run `securebridge` from the partner cluster.

> **Note:** Beginning with ONTAP 9.8, the `storage bridge` command is replaced with `system bridge`.

Steps:
1. From the ONTAP prompt of the cluster containing the bridge, secure or unsecure the bridge:
   - Secure: `cluster_A> storage bridge run-cli -bridge bridge_A_1 -command securebridge`
   - Unsecure: `cluster_A> storage bridge run-cli -bridge bridge_A_1 -command unsecurebridge`
2. Save the bridge configuration: `storage bridge run-cli -bridge <bridge-name> -command saveconfiguration`
   Example: `cluster_A> storage bridge run-cli -bridge bridge_A_1 -command saveconfiguration`
3. Restart the bridge's firmware: `storage bridge run-cli -bridge <bridge-name> -command firmwarerestart`
   Example: `cluster_A> storage bridge run-cli -bridge bridge_A_1 -command firmwarerestart`
