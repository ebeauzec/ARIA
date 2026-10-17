# ONTAP platform-specific network speeds and switch port modes for MetroCluster-compliant switches
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept-network-speeds-and-switchport-modes.html
Fetched: 2026-07-07

If you are using MetroCluster compliant switches, you should be aware of the platform-specific network speeds and switch port mode requirements. Configure the switch port mode according to the table below.

> **Note:** Missing values indicate that the platform cannot be used with a MetroCluster-compliant switch. AFF A30, AFF C30, AFF C60, and FAS50 systems require a QSFP-to-SFP+ adapter in the card on the controller to support a 25Gbps network speed.

| Platform | Network speed (Gbps) | Switch port mode |
|---|---|---|
| FAS9500, AFF A900, ASA A900 | 100Gbps (40Gbps when upgrading PCM from FAS9000 or AFF A700) | Trunk mode |
| AFF C800, ASA C800, AFF A800, ASA A800 | 40Gbps or 100Gbps | Access mode |
| FAS9000, AFF A700 | 40Gbps | Access mode |
| FAS8300, AFF C400, ASA C400, AFF A400, ASA A400 | 40Gbps or 100Gbps | Trunk mode |
| AFF A320 | 40Gbps or 100Gbps | Access mode |
| FAS8200, AFF A300 | 25Gbps | Access mode |
| FAS500f, AFF C250, ASA C250, AFF A250, ASA A250 | – | – |
| FAS2750, AFF A220 | – | – |
| AFF A150, ASA A150 | – | – |
| AFF A20 | 25Gbps | Trunk mode |
| AFF A30 | 25Gbps or 100Gbps | Trunk mode |
| AFF C30 | 25Gbps or 100Gbps | Trunk mode |
| AFF C60 | 25Gbps or 100Gbps | Trunk mode |
| FAS50 | 25Gbps or 100Gbps | Trunk mode |
| AFF A50 | 100Gbps | Trunk mode |
| AFF A70 | 100Gbps | Trunk mode |
| AFF A90 | 100Gbps | Trunk mode |
| AFF A1K | 100Gbps | Trunk mode |
| AFF C80 | 100Gbps | Trunk mode |
| FAS70 | 100Gbps | Trunk mode |
| FAS90 | 100Gbps | Trunk mode |
