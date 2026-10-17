# Requirements to deploy MetroCluster IP configurations in shared layer 2 or layer 3 networks
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept-considerations-layer-2-layer-3.html
Fetched: 2026-07-07

Depending on your requirements, you can use shared layer 2 or layer 3 networks to deploy MetroCluster.

Beginning with ONTAP 9.6, MetroCluster IP configurations with supported switches can share existing networks for Inter-Switch Links (ISLs) instead of using dedicated MetroCluster ISLs — this topology is known as *shared layer 2 networks*.

Beginning with ONTAP 9.9.1, MetroCluster IP configurations can be implemented with IP-routed (layer 3) backend connections — this topology is known as *shared layer 3 networks*.

> **Note:** Not all features are supported in all network topologies. You must verify that you have adequate network capacity and that the ISL size is appropriate for your configuration. Low latency is critical for replication of data between the MetroCluster sites — latency issues on these connections can impact client I/O. All references to MetroCluster backend switches refer to switches that are NetApp-validated switches or MetroCluster-compliant (see [NetApp-validated and MetroCluster-compliant switches](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/mcc-compliant-netapp-validated-switches.html)).

## ISL requirements for layer 2 and layer 3 networks

- The speed and number of ISLs between the MetroCluster switches and the intermediate network switches does not need to match. Similarly, the speed between the intermediate network switches does not need to match. For example, MetroCluster switches can connect using one 40Gbps ISL to the intermediate switches, and the intermediate switches can connect to each other using two 100Gbps ISLs.
- Network monitoring should be configured on the intermediate network to monitor the ISLs for utilization, errors (drops, link flaps, corruption, and so on), and failures.
- The MTU size must be set to 9216 on all ports carrying MetroCluster end-to-end traffic.
- No other traffic can be configured with a higher priority than class of service (COS) 5.
- Explicit congestion notification (ECN) must be configured on all paths carrying end-to-end MetroCluster traffic.
- ISLs carrying MetroCluster traffic must be native links between the switches. Link sharing services such as Multiprotocol Label Switching (MPLS) links are not supported.
- The layer 2 VLANs must natively span the sites. VLAN overlay such as Virtual Extensible LAN (VXLAN) is not supported.
- The number of intermediate switches is not limited. However, NetApp recommends keeping the number of switches to the minimum required.
- ISLs on MetroCluster switches are configured with: switch port mode 'trunk' as part of an LACP port-channel; MTU size 9216; no native VLAN configured; only VLANs carrying cross-site MetroCluster traffic allowed; the switch default VLAN is not allowed.

## Considerations for layer 2 networks

The MetroCluster backend switches are connected to the customer network. The intermediate customer-provided switches must meet the following requirements:

- The intermediate network must provide the same VLANs between the sites — this must match the MetroCluster VLANs set in the RCF file.
- The RcfFileGenerator does not allow the creation of an RCF file using VLANs that are not supported by the platform.
- The RcfFileGenerator might restrict the use of certain VLAN IDs (e.g., if intended for future use) — reserved VLANs are generally up to and including 100.
- Layer 2 VLANs with IDs that match the MetroCluster VLAN IDs must span the shared network.

**VLAN configuration in ONTAP**

You can only specify the VLAN during interface creation. You can configure the default VLANs 10 and 20, or VLANs within the range 101 to 4096 (or the number supported by the switch vendor, whichever is lower). After the MetroCluster interfaces are created, you cannot change the VLAN ID.

> **Note:** Some switch vendors might reserve the use of certain VLANs.

The following systems do NOT require VLAN configuration within ONTAP (the VLAN is specified by the switch port configuration): FAS8200 and AFF A300; AFF A320; FAS9000 and AFF A700; AFF A800, ASA A800, AFF C800, and ASA C800.

> **Note:** These systems might be configured using VLANs 100 and below; however, some VLANs in this range might be reserved for other or future use.

For all other systems, you must configure the VLAN when creating the MetroCluster interfaces in ONTAP:
- The default VLAN is 10 and 20.
- If running ONTAP 9.7 or earlier, you can only use the default VLAN 10 and 20.
- If running ONTAP 9.8 or later, you can use the default VLAN 10 and 20, and a VLAN over 100 (101 and higher) can also be used.

## Considerations for layer 3 networks

The MetroCluster backend switches are connected to the routed IP network, either directly to routers or through other intervening switches. The MetroCluster environment is configured and cabled as a standard MetroCluster IP configuration (see [Configure the MetroCluster hardware components](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_parts_of_an_ip_mcc_configuration_mcc_ip.html)) with additional layer-3-specific steps. The following applies:

- You can connect MetroCluster switches directly to the router or to one or more intervening switches.
- You can connect MetroCluster IP interfaces directly to the router or to one of the intervening switches.
- The VLAN must be extended to the gateway device.
- You use the `-gateway` parameter to configure the MetroCluster IP interface address with an IP gateway address.
- The VLAN IDs for the MetroCluster VLANs must be the same at each site; however, the subnets can be different.
- Dynamic routing is not supported for MetroCluster traffic.
- The following features are NOT supported: eight-node MetroCluster configurations; refreshing a four-node MetroCluster configuration; transition from MetroCluster FC to MetroCluster IP.
- Two subnets are required on each MetroCluster site — one in each network.
- Auto-IP assignment is not supported.

When configuring routers and gateway IP addresses, you must meet the following requirements:
- Two interfaces on one node cannot have the same gateway IP address.
- The corresponding interfaces on the HA pairs on each site must have the same gateway IP address.
- The corresponding interfaces on a node and its DR and AUX partners cannot have the same gateway IP address.
- The corresponding interfaces on a node and its DR and AUX partners must have the same VLAN ID.

## Required settings for intermediate switches

When MetroCluster traffic traverses an ISL in an intermediate network, verify that the intermediate switch configuration ensures MetroCluster traffic (RDMA and storage) meets the required service levels across the entire path between the MetroCluster sites.

In the reference examples, the following policies and maps are created for MetroCluster traffic:
- The `MetroClusterIP_ISL_Ingress` policy is applied to ports on the intermediate switch that connect to the MetroCluster IP switches — it maps incoming tagged traffic to the appropriate queue on the intermediate switch.
- A `MetroClusterIP_ISL_Egress` policy is applied to ports on the intermediate switch that connect to ISLs between intermediate switches.
- You must configure the intermediate switches with matching QoS access-maps, class-maps, and policy-maps along the path between the MetroCluster IP switches. The intermediate switches map RDMA traffic to COS5 and storage traffic to COS4.

The following examples are for Cisco Nexus 3232C and 9336C-FX2 switches (verify appropriate configuration for your own switch vendor/model).

**Configure the class map for the intermediate switch ISL port**

Classify traffic on ingress:
```
ip access-list rdma
  10 permit tcp any eq 10006 any
  20 permit tcp any any eq 10006
ip access-list storage
  10 permit tcp any eq 65200 any
  20 permit tcp any any eq 65200

class-map type qos match-all rdma
  match access-group name rdma
class-map type qos match-all storage
  match access-group name storage
```

Match traffic on ingress:
```
class-map type qos match-any c5
  match cos 5
  match dscp 40
class-map type qos match-any c4
  match cos 4
  match dscp 32
```

**Create an ingress policy map on the ISL port of the intermediate switch**

Classify the traffic on ingress:
```
policy-map type qos MetroClusterIP_ISL_Ingress_Classify
  class rdma
    set dscp 40
    set cos 5
    set qos-group 5
  class storage
    set dscp 32
    set cos 4
    set qos-group 4
  class class-default
    set qos-group 0
```

Match the traffic on ingress:
```
policy-map type qos MetroClusterIP_ISL_Ingress_Match
  class c5
    set dscp 40
    set cos 5
    set qos-group 5
  class c4
    set dscp 32
    set cos 4
    set qos-group 4
  class class-default
    set qos-group 0
```

**Configure the egress queuing policy for the ISL ports**

```
policy-map type queuing MetroClusterIP_ISL_Egress
   class type queuing c-out-8q-q7
      priority level 1
   class type queuing c-out-8q-q6
      priority level 2
   class type queuing c-out-8q-q5
      priority level 3
      random-detect threshold burst-optimized ecn
   class type queuing c-out-8q-q4
      priority level 4
      random-detect threshold burst-optimized ecn
   class type queuing c-out-8q-q3
      priority level 5
   class type queuing c-out-8q-q2
      priority level 6
   class type queuing c-out-8q-q1
      priority level 7
   class type queuing c-out-8q-q-default
      bandwidth remaining percent 100
      random-detect threshold burst-optimized ecn
```

These settings must be applied on all switches and ISLs carrying MetroCluster traffic.

Q4 and Q5 are configured with `random-detect threshold burst-optimized ecn`. Depending on your configuration, you might need to set the minimum and maximum thresholds:
```
class type queuing c-out-8q-q5
  priority level 3
  random-detect minimum-threshold 3000 kbytes maximum-threshold 4000 kbytes drop-probability 0 weight 0 ecn
class type queuing c-out-8q-q4
  priority level 4
  random-detect minimum-threshold 2000 kbytes maximum-threshold 3000 kbytes drop-probability 0 weight 0 ecn
```

> **Note:** Minimum and maximum values vary depending on the switch and your requirements.

**Example 1: Cisco** — If your configuration has Cisco switches, you do not need to classify on the first ingress port of the intermediate switch. Configure: `class-map type qos match-any c5`; `class-map type qos match-any c4`; `MetroClusterIP_ISL_Ingress_Match`. Assign the `MetroClusterIP_ISL_Ingress_Match` policy map to the ISL ports carrying MetroCluster traffic.

**Example 2: Broadcom** — If your configuration has Broadcom switches, you must classify on the first ingress port of the intermediate switch. Configure: `ip access-list rdma`; `ip access-list storage`; `class-map type qos match-all rdma`; `class-map type qos match-all storage`; `MetroClusterIP_ISL_Ingress_Classify`; `MetroClusterIP_ISL_Ingress_Match`. Assign the `MetroClusterIP_ISL_Ingress_Classify` policy map to the ISL ports on the intermediate switch connecting the Broadcom switch. Assign the `MetroClusterIP_ISL_Ingress_Match` policy map to the ISL ports on the intermediate switch that is carrying MetroCluster traffic but does not connect the Broadcom switch.
