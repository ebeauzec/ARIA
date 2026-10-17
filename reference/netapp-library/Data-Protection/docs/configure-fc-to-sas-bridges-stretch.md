# Configuring the FC-to-SAS bridges
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/task_configure_the_fc_to_sas_bridges_fb_new_install_configure.html
Fetched: 2026-07-07

Before cabling your model of the FC-to-SAS bridges, you must configure the settings in the FibreBridge software.

## About this task

You should decide whether you will be using in-band management of the bridges.

> **Note:** Beginning with ONTAP 9.8, the `storage bridge` command is replaced with `system bridge`. The following steps show the `storage bridge` command. However, if you are running ONTAP 9.8 or later, the `system bridge` command is preferred.

If you will be using in-band management of the bridge rather than IP management, the steps for configuring the Ethernet port and IP settings can be skipped.

## Steps

1. If configuring for in-band management, connect a cable from FibreBridge RS-232 serial port to the serial (COM) port on a personal computer.

   The serial connection will be used for initial configuration. Then in-band management via ONTAP and the FC ports can be used to monitor and manage the bridge.

2. If configuring for IP management, connect the Ethernet management 1 port on each bridge to your network by using an Ethernet cable.

   In systems running ONTAP 9.5 or later, in-band management can be used to access the bridge via the FC ports rather than the Ethernet port. Beginning with ONTAP 9.8, only in-band management is supported and SNMP management is deprecated.

   The Ethernet management 1 port enables you to quickly download the bridge firmware (using ATTO ExpressNAV or FTP management interfaces) and to retrieve core files and extract logs.

3. If configuring for IP management, configure the Ethernet management 1 port for each bridge by following the procedure in section 2.0 of the *ATTO FibreBridge Installation and Operation Manual* for your bridge model.

   In systems running ONTAP 9.5 or later, in-band management can be used to access the bridge via the FC ports rather than the Ethernet port. Beginning with ONTAP 9.8, only in-band management is supported and SNMP management is deprecated.

   When running QuickNAV to configure an Ethernet management port, only the Ethernet management port that is connected by the Ethernet cable is configured. For example, if you also wanted to configure the Ethernet management 2 port, you would need to connect the Ethernet cable to port 2 and run QuickNAV.

4. Configure the bridge.

   You should make note of the user name and password that you designate.

   > **Note:** Do not configure time synchronization on ATTO FibreBridge 7600N or 7500N. The time synchronization for ATTO FibreBridge 7600N or 7500N is set to the cluster time after the bridge is discovered by ONTAP. It is also synchronized periodically once a day. The time zone used is GMT and is not changeable.

   1. If configuring for IP management, configure the IP settings of the bridge.

      In systems running ONTAP 9.5 or later, in-band management can be used to access the bridge via the FC ports rather than the Ethernet port. Beginning with ONTAP 9.8, only in-band management is supported and SNMP management is deprecated.

      To set the IP address without the QuickNAV utility, you need to have a serial connection to the FibreBridge.

      If using the CLI, you must run the following commands:
      ```
      set ipaddress mp1 ip-address
      set ipsubnetmask mp1 subnet-mask
      set ipgateway mp1 x.x.x.x
      set ipdhcp mp1 disabled
      set ethernetspeed mp1 1000
      ```

   2. Configure the bridge name.

      The bridges should each have a unique name within the MetroCluster configuration.

      Example bridge names for one stack group on each site:
      - bridge_A_1a
      - bridge_A_1b
      - bridge_B_1a
      - bridge_B_1b

      If using the CLI, you must run the following command:
      `set bridgename bridgename`

   3. If running ONTAP 9.4 or earlier, enable SNMP on the bridge:
      `set SNMP enabled`

      In systems running ONTAP 9.5 or later, in-band management can be used to access the bridge via the FC ports rather than the Ethernet port. Beginning with ONTAP 9.8, only in-band management is supported and SNMP management is deprecated.

5. Configure the bridge FC ports.

   1. Configure the data rate/speed of the bridge FC ports.

      The supported FC data rate depends on your model bridge.
      - The FibreBridge 7600N bridge supports up to 32, 16, or 8 Gbps.
      - The FibreBridge 7500N bridge supports up to 16, 8, or 4 Gbps.

      > **Note:** The FCDataRate speed you select is limited to the maximum speed supported by both the bridge and the FC port of the controller module to which the bridge port connects. Cabling distances must not exceed the limitations of the SFPs and other hardware.

      If using the CLI, you must run the following command:
      `set FCDataRate port-number port-speed`

   2. If you are configuring a FibreBridge 7500N bridge, configure the connection mode that the port uses to "ptp".

      > **Note:** The FCConnMode setting is not required when configuring a FibreBridge 7600N bridge.

      If using the CLI, you must run the following command:
      `set FCConnMode port-number ptp`

   3. If you are configuring a FibreBridge 7600N or 7500N bridge, you must configure or disable the FC2 port.

      - If you are using the second port, you must repeat the previous substeps for the FC2 port.
      - If you are not using the second port, then you must disable the port:
        `FCPortDisable port-number`

      Example — disabling FC port 2:
      ```
      FCPortDisable 2
      Fibre Channel Port 2 has been disabled.
      ```

   4. If you are configuring a FibreBridge 7600N or 7500N bridge, disable the unused SAS ports:
      `SASPortDisable sas-port`

      > **Note:** SAS ports A through D are enabled by default. You must disable the SAS ports that are not being used.

      If only SAS port A is used, then SAS ports B, C, and D must be disabled. Example — disabling SAS port B (repeat similarly for C and D):
      ```
      SASPortDisable b
      SAS Port B has been disabled.
      ```

6. Secure access to the bridge and save the bridge's configuration. Choose an option depending on the ONTAP version:

   | ONTAP version | Steps |
   |---|---|
   | **ONTAP 9.5 or later** | View the status of the bridges: `storage bridge show`. The output shows which bridge is not secured. Secure the bridge: `securebridge` |
   | **ONTAP 9.4 or earlier** | View the status of the bridges: `storage bridge show`. The output shows which bridge is not secured. Check the status of the unsecured bridge's ports: `info`. The output shows the status of Ethernet ports MP1 and MP2. If Ethernet port MP1 is enabled, run: `set EthernetPort mp1 disabled`. If Ethernet port MP2 is also enabled, repeat for port MP2. Save the bridge's configuration by running: `SaveConfiguration` then `FirmwareRestart`. You are prompted to restart the bridge. |

7. After completing MetroCluster configuration, use the `flashimages` command to check your version of FibreBridge firmware and, if the bridges are not using the latest supported version, update the firmware on all bridges in the configuration.

   [Maintain MetroCluster Components](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/index.html)

## Related information

[In-band management of the FC-to-SAS bridges](https://docs.netapp.com/us-en/ontap-metrocluster/install-stretch/concept_in_band_management_of_the_fc_to_sas_bridges.html)
