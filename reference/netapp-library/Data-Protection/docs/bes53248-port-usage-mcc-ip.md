# Platform port assignments for Broadcom supported BES-53248 IP switches in a MetroCluster IP configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/port_usage_bes53248.html
Fetched: 2026-07-07

The port usage in a MetroCluster IP configuration depends on the switch model and platform type.

Considerations before using the configuration tables:

- You cannot use the switches with remote ISL ports of different speeds (for example, a 25 Gbps port connected to a 10 Gbps ISL port).
- If you configure the switch for MetroCluster FC to IP Transition, the following ports are used depending on the target platform:

  | Target platform | Port |
  |---|---|
  | FAS500f, AFF C250, ASA C250, AFF A250, ASA A250, FAS8300, AFF C400, ASA C400, AFF A400, ASA A400, or FAS8700 platforms | ports 1–6, 10Gbps |
  | FAS8200 or AFF A300 platforms | ports 3–4 and 9–12, 10Gbps |

- AFF A320 systems configured with Broadcom BES-53248 switches might not support all features. Any configuration or feature that requires that the local cluster connections are connected to a switch is not supported, for example: eight-node MetroCluster configurations; transitioning from MetroCluster FC to MetroCluster IP configurations; refreshing a four-node MetroCluster IP configuration (ONTAP 9.8 and later).

## Choose the correct cabling table for your configuration

| If your system is… | Use this cabling table… |
|---|---|
| AFF A150, ASA A150; FAS2750; AFF A220 | Broadcom BES-53248 platform port assignments (group 1) |
| FAS500f; AFF C250, ASA C250; AFF A250, ASA A250 | Broadcom BES-53248 platform port assignments (group 2) |
| AFF A20 | Broadcom BES-53248 platform port assignments (group 3) |
| AFF C30, AFF A30; FAS50; AFF C60 | Broadcom BES-53248 platform port assignments (group 4) |
| FAS8200, AFF A300 | Broadcom BES-53248 platform port assignments (group 5) |
| AFF A320 | Broadcom BES-53248 platform port assignments (group 6) |
| FAS8300; AFF C400, ASA C400; AFF A400, ASA A400; FAS8700 | Broadcom BES-53248 platform port assignments (group 7) |

**Group 1** — AFF A150, ASA A150, FAS2750, or AFF A220 to a Broadcom BES-53248 switch. Note 1: Using these ports requires an additional license. If both MetroCluster configurations use the same platform, NetApp recommends selecting group "MetroCluster 3" for one configuration and group "MetroCluster 4" for the other. If the platforms differ, select "MetroCluster 3" or "MetroCluster 4" for the first configuration, and "MetroCluster 1" or "MetroCluster 2" for the second.

**Group 2** — FAS500f, AFF C250, ASA C250, AFF A250, or ASA A250 to a Broadcom BES-53248 switch. Same Note 1 and MetroCluster group-selection guidance as group 1.

**Group 3** — AFF A20 to a Broadcom BES-53248 switch. Note 1: Using these ports requires an additional license.

**Group 4** — AFF A30, AFF C30, AFF C60, or FAS50 to a Broadcom BES-53248 switch using a four-port 25G Ethernet card.
> **Note:** This configuration requires a four-port 25G Ethernet card in slot 4 to connect the local cluster and HA interfaces, and a QSFP-to-SFP+ adapter in the card on the controller to support a 25Gbps network speed.
Note 1: Using these ports requires an additional license.

**Group 5** — FAS8200 or AFF A300 to a Broadcom BES-53248 switch. Note 1: Using these ports requires an additional license.

**Group 6** — AFF A320 to a Broadcom BES-53248 switch. Note 1: Using these ports requires an additional license. Note 2: Only a single four-node MetroCluster using AFF A320 systems can be connected to the switch. Features that require a switched cluster are not supported in this configuration (includes MetroCluster FC to IP transition and tech refresh procedures).

**Group 7** — FAS8300, AFF C400, ASA C400, AFF A400, ASA A400, or FAS8700 to a Broadcom BES-53248 switch. Note 1: Using these ports requires an additional license. Note 2: Only a single four-node MetroCluster using AFF A320 systems can be connected to the switch; features requiring a switched cluster are not supported (MetroCluster FC to IP transition and tech refresh procedures).

(Cabling diagrams for each group are image-based in the source and are not reproduced here — see the source URL for the port-assignment diagrams.)
