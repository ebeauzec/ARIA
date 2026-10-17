# ONTAP support for SAN host multipathing
Source: https://docs.netapp.com/us-en/ontap/san-config/host-support-multipathing-concept.html
Fetched: 2026-07-07

ONTAP uses Asymmetric Logical Unit Access (ALUA) software for multipathing with both FC and iSCSI hosts.

Beginning with ONTAP 9.5 multipath high availability (HA) pair failover/giveback is supported for NVMe hosts using Asynchronous Namespace Access (ANA). In ONTAP 9.4, NVMe supports only one path from host to target, so the application host must manage path failover to its HA partner.

For information about which specific host configurations support ALUA or ANA, see the NetApp Interoperability Matrix Tool (https://mysupport.netapp.com/matrix) and ONTAP SAN Host Configuration (https://docs.netapp.com/us-en/ontap-sanhost/index.html) for your host operating system.

Multipathing software, also known as MPIO (multipath I/O) software, is recommended in HA configurations. The multipathing software is required on your SAN host so it can access a LUN or NVMe namespace through more than one path. It presents a single disk to the operating system for all paths to a LUN or NVMe namespace. Without it, the operating system could treat each path as a separate disk, leading to data corruption.

Your solution is considered to have multiple paths if you have any of the following:

- A single initiator port in the host attaching to multiple SAN LIFs in the SVM
- Multiple initiator ports attaching to a single SAN LIF in the SVM
- Multiple initiator ports attaching to multiple SAN LIFs in the SVM

You should use Selective LUN Map, FC switch zoning or portsets to limit the paths used to access LUNs and namespaces.

Related information: Learn about SAN multipath configurations supported by ONTAP — https://docs.netapp.com/us-en/ontap/san-admin/multipath-automatic-lif-failover-support.html

## Recommended number of paths from host to nodes in cluster

You should not exceed more than eight paths from your host to each node in your cluster. You should also not exceed the total number of paths that can be supported for the host OS and the multipathing used on the host.

If you have four or more nodes in your cluster or more than four target ports being used by the SVMs in any of your nodes, you can use the following methods to limit the number of paths that can be used to access LUNs on your nodes so that you do not exceed the recommended maximum of eight paths.

- **Selective LUN Map (SLM)** (https://docs.netapp.com/us-en/ontap/san-admin/selective-lun-map-concept.html) — SLM reduces the number of paths from the host to LUN to only paths on the node owning the LUN and the owning node's HA partner. SLM is enabled by default. You should have a minimum of two paths per LUN connecting to each reporting node through SLM being used by the storage virtual machine (SVM) in your cluster. This eliminates single points of failure and enables the system to survive component failures.
- **Portsets** (https://docs.netapp.com/us-en/ontap/san-admin/limit-lun-access-portsets-igroups-concept.html) — Portsets can be used with SLM to further restrict access of certain targets to certain initiators. When using SLM with portsets, LUNs will be accessible on the set of LIFs in the portset on the node that owns the LUN and on that node's HA partner.
- **Initiator group (igroup) mappings from your host** — You can define igroups and map them to LUNs to control which initiators have access to LUNs.
- **FC switch zoning** (https://docs.netapp.com/us-en/ontap/san-config/fc-fcoe-recommended-zoning-configuration.html) — You should create a zoning configuration if your host does not have a multipathing solution installed, if four or more hosts are connected to your SAN or if SLM is not implemented on the nodes in your cluster.
