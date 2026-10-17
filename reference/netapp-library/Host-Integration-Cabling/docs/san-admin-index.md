# SAN management overview
Source: https://docs.netapp.com/us-en/ontap/san-admin/index.html
Fetched: 2026-07-07

The content in this section shows you how to configure and manage SAN environments with the ONTAP command line interface (CLI) and System Manager in ONTAP 9.7 and later releases.

If you are using the classic System Manager (available only in ONTAP 9.7 and earlier), see these topics:

- iSCSI protocol: https://docs.netapp.com/us-en/ontap-system-manager-classic/online-help-96-97/concept_iscsi_protocol.html
- FC/FCoE protocol: https://docs.netapp.com/us-en/ontap-system-manager-classic/online-help-96-97/concept_fc_fcoe_protocol.html

You can use the iSCSI and FC protocols to provide storage in a SAN environment.

With iSCSI and FC, storage targets are called LUNs (logical units) and are presented to hosts as standard block devices. You create LUNs and then map them to initiator groups (igroups). Initiator groups are tables of FC host WWPs and iSCSI host node names and control which initiators have access to which LUNs.

FC targets connect to the network through FC switches and host-side adapters and are identified by world-wide port names (WWPNs). iSCSI targets connect to the network through standard Ethernet network adapters (NICs), TCP offload engine (TOE) cards with software initiators, converged network adapters (CNAs) or dedicated host bus adapters (HBAs) and are identified by iSCSI qualified names (IQNs).

## For more information

If you have an ASA r2 storage system (ASA A1K, ASA A90, ASA A70, ASA A50, ASA A30, or ASA A20), see the ASA r2 storage system documentation: https://docs.netapp.com/us-en/asa-r2/index.html
