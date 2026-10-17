# Requirements and limitations for MetroCluster-compliant switches
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept-requirement-and-limitations-mcc-compliant-switches.html
Fetched: 2026-07-07

Beginning with ONTAP 9.7, MetroCluster IP configurations can use MetroCluster-compliant switches. These are switches that are not NetApp-validated but are compliant with NetApp specifications. NetApp does not provide troubleshooting or configuration support services for any non-validated switch.

## MetroCluster-compliant versus NetApp-validated switches

A switch is NetApp-validated if it meets ALL of the following:
- Provided by NetApp as part of the MetroCluster IP configuration.
- Listed in the [NetApp Hardware Universe](https://hwu.netapp.com/) as a supported switch under *MetroCluster-over-IP-connections*.
- Used only to connect MetroCluster IP controllers and, in some configurations, NS224 drive shelves.
- Configured using the Reference Configuration File (RCF) provided by NetApp.

Any switch not meeting these requirements is not NetApp-validated. A MetroCluster-compliant switch is not NetApp-validated but can be used in a MetroCluster IP configuration if it meets certain requirements/guidelines.

Note: NetApp does not provide troubleshooting or configuration support services for any non-validated MetroCluster-compliant switch.

## General requirements for MetroCluster-compliant switches

- Must support quality of service (QoS) and traffic classification.
- Must support explicit congestion notification (ECN).
- Must support a load-balancing policy that preserves order along the path.
- Must support L2 Flow Control (L2FC).
- Switch port must provide a dedicated rate and must not be overallocated.
- Cables and transceivers connecting nodes to switches must be NetApp-provided and supported by the switch vendor. For optical cabling, the switch-side transceiver may not be NetApp-provided — verify compatibility with the controller's transceiver.
- Switches connecting MetroCluster nodes can carry non-MetroCluster traffic.
- Only platforms with dedicated ports for switchless cluster interconnects can be used with a MetroCluster-compliant switch. Platforms like FAS2750 and AFF A220 cannot be used because MetroCluster traffic and MetroCluster interconnect traffic share the same network ports.
- The MetroCluster-compliant switch must not be used for local cluster connections.
- The MetroCluster IP interface can connect to any switch port configurable to meet the requirements.
- Four IP switches are required (two per switch fabric). If using directors, a single director can be used per side, but MetroCluster IP interfaces must connect to two different blades in two different failure domains on that director.
- MetroCluster interfaces from one node must connect to two different network switches or blades — never the same switch/blade.
- Network must meet requirements in "Considerations for ISLs" and "Considerations when deploying MetroCluster in shared layer 2 or layer 3 networks".
- MTU of 9216 must be configured on all switches carrying MetroCluster IP traffic.
- Reverting to ONTAP 9.6 or earlier is not supported.

Any intermediate switches between the MetroCluster IP interface switches at both sites must also meet these requirements per "Considerations when deploying MetroCluster in shared layer 2 or layer 3 networks."

## Limitations when using MetroCluster-compliant switches

Any configuration/feature requiring local cluster connections to be switch-connected is NOT supported, including:
- Eight-node MetroCluster configurations.
- Transitioning from MetroCluster FC to MetroCluster IP configurations.
- Refreshing a four-node MetroCluster IP configuration.
- Platforms sharing a physical interface for local cluster and MetroCluster traffic (see "Platform-specific network speeds and switch port modes for MetroCluster-compliant switches" for supported speeds).
