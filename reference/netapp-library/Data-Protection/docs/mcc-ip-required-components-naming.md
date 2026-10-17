# Required MetroCluster IP configuration components and naming conventions
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_required_mcc_ip_components_and_naming_guidelines_mcc_ip.html
Fetched: 2026-07-07

Identify the required and supported hardware and software components for a MetroCluster IP configuration. Review the naming conventions that documentation examples use for the components.

## Supported software and hardware

The hardware and software must be supported for the MetroCluster IP configuration ([NetApp Hardware Universe](https://hwu.netapp.com)). When using AFF systems, all controller modules in the MetroCluster configuration must be configured as AFF systems.

## Hardware redundancy requirements in a MetroCluster IP configuration

Because of the hardware redundancy in the MetroCluster IP configuration, there are two of each component at each site. The sites are arbitrarily assigned the letters A and B, and the individual components are arbitrarily assigned the numbers 1 and 2.

## ONTAP cluster requirements in a MetroCluster IP configuration

MetroCluster IP configurations require two ONTAP clusters, one at each MetroCluster site. Naming must be unique within the MetroCluster configuration.

Example names: Site A: cluster_A; Site B: cluster_B

## IP switch requirements in a MetroCluster IP configuration

MetroCluster IP configurations require four IP switches. The four switches form two switch storage fabrics that provide the ISL between each of the clusters in the MetroCluster IP configuration. The IP switches also provide intracluster communication among the controller modules in each cluster. Naming must be unique within the MetroCluster configuration.

Example names: Site A (cluster_A): IP_switch_A_1, IP_switch_A_2; Site B (cluster_B): IP_switch_B_1, IP_switch_B_2

## Controller module requirements in a MetroCluster IP configuration

MetroCluster IP configurations require four or eight controller modules. The controller modules at each site form an HA pair. Each controller module has a DR partner at the other site. Each controller module must be running the same ONTAP version. Supported platform models depend on the ONTAP version:

- New MetroCluster IP installations on FAS systems are not supported in ONTAP 9.4. Existing MetroCluster IP configurations on FAS systems can be upgraded to ONTAP 9.4.
- Beginning with ONTAP 9.5, new MetroCluster IP installations on FAS systems are supported.
- Beginning with ONTAP 9.4, controller modules configured for ADP are supported.

Example names: Site A (cluster_A): controller_A_1, controller_A_2; Site B (cluster_B): controller_B_1, controller_B_2

## Gigabit Ethernet adapter requirements in a MetroCluster IP configuration

MetroCluster IP configurations use a 40/100 Gbps or 10/25 Gbps Ethernet adapter for the IP interfaces to the IP switches used for the MetroCluster IP fabric.

> **Note:** Onboard ports are built into the controller hardware (Slot 0) and can't be replaced, so the required slot for adapter is not applicable.

| Platform model | Required Gigabit Ethernet adapter | Required slot for adapter | Ports |
|---|---|---|---|
| AFF A900, ASA A900, and FAS9500 | X91146A | Slot 5, Slot 7 | e5b, e7b. **Note:** Ports e5a and e7a can only be used for intercluster LIFs; cannot be used for a data LIF. |
| AFF A700 and FAS9000 | X91146A-C | Slot 5 | e5a, e5b |
| AFF A800, AFF C800, ASA A800, and ASA C800 | X1146A/onboard ports | Slot 1/Not applicable for onboard ports | e0b, e1b |
| FAS8300, AFF A400, ASA A400, ASA C400, AFF C400 | X1146A | Slot 1 | e1a, e1b |
| AFF A300, FAS8200 | X1116A | Slot 1 | e1a, e1b |
| FAS2750, AFF A150, ASA A150, AFF A220 | Onboard ports | Not applicable | e0a, e0b |
| FAS500f, AFF A250, ASA A250, ASA C250, AFF C250 | Onboard ports | Not applicable | e0c, e0d |
| AFF A320 | Onboard ports | Not applicable | e0g, e0h |
| AFF A70, FAS70, AFF C80 | X50132A | Slot 2 | e2a, e2b |
| AFF A90, AFF A1K, FAS90 | X50132A | Slot 2, Slot 3 | e2b, e3b. **Note:** Ports e2a and e3a must remain unused — using these ports for front-end networks or peering is not supported. |
| AFF A50 | X60134A | Slot 2 | e2a, e2b |
| AFF A30, AFF C30, AFF C60, FAS50 | X60134A | Slot 2 | e2a, e2b. **Note:** 25 GbE speed requires the MAM1Q00A-QSA28 transceiver adapter. |
| AFF A20 | X60132A | Slot 4, Slot 2 | e2b, e4b |

See [Considerations for automatic drive assignment and ADP systems in MetroCluster IP configurations](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_considerations_drive_assignment.html).

## Pool and drive requirements (minimum supported)

A four-node MetroCluster IP configuration requires the minimum configuration at each site:

- Each node has at least one local pool and one remote pool at the site.
- At least seven drives in each pool. In a four-node MetroCluster configuration with a single mirrored data aggregate per node, the minimum configuration requires 24 disks at the site.

  > **Note:** Aggregate names must be unique across the MetroCluster sites. This means that you cannot have two different aggregates with the same name on site A and site B.

In a minimum supported configuration, each pool has the following drive layout: three root drives, three data drives, one spare drive. At least one shelf is needed per site.

MetroCluster configurations support RAID-DP, RAID4, and RAID-TEC.

> **Note:** Beginning with ONTAP 9.4, MetroCluster IP configurations support new installations using automatic disk assignment and ADP (Advanced Drive Partitioning). See [Considerations for automatic drive assignment and ADP systems](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_considerations_drive_assignment.html).

## Drive location considerations for partially populated shelves

For correct auto-assignment of drives when using shelves that are half populated (12 drives in a 24-drive shelf), drives should be located in slots 0-5 and 18-23. In a configuration with a partially populated shelf, the drives must be evenly distributed in the four quadrants of the shelf.

## Drive location considerations for AFF A800 internal drives

For correct implementation of the ADP feature, the AFF A800 system disk slots must be divided into quarters and the disks must be located symmetrically in the quarters. An AFF A800 system has 48 drive bays, divided into quarters:

- Quarter one: bays 0–5, 24–29
- Quarter two: bays 6–11, 30–35
- Quarter three: bays 12–17, 36–41
- Quarter four: bays 18–23, 42–47

If populated with 16 drives, they must be symmetrically distributed among the four quarters: four drives in the first quarter (0,1,2,3), four in the second (6,7,8,9), four in the third (12,13,14,15), four in the fourth (18,19,20,21).
