# What are Best Practices for Network Configuration for ONTAP?
Source: https://kb.netapp.com/Advice_and_Troubleshooting/Data_Storage_Software/ONTAP_OS/Best_Practices_for_Network_Configuration_with_NetApp_Storage_Systems
Fetched: 2026-07-07

## Applies to

- ONTAP 9
- Data ONTAP 7

## Answer

- Use virtual LANs (VLANs) to logically separate/isolate traffic on layer 2, mainly for security purposes and reducing complexity when troubleshooting. Use cases can be among others by type (e.g. data, management) or service (Frontend-webhost, SQL Server 1a, Kubernetes Cluster X) or department/team (e.g. HR, IT, Support): Configure VLANs over physical ports (https://docs.netapp.com/us-en/ontap/networking/configure_vlans_over_physical_ports.html#edit-a-vlan)
- Networking Best Practices for ONTAP 9 are in the respective sections in Ethernet Storage Design Considerations, Best Practices for Clustered Data ONTAP | TR-4182 (https://www.netapp.com/pdf.html?item=/media/16885-tr-4182.pdf)

**Examples:**

- Use Failover Groups instead of single mode interface groups (ifgrps) (p. 12, single mode)
- Disable flow control on all cluster network ports in an ONTAP cluster. No recommendations for other network ports. (p. 30, Ethernet Flow Control)

## Additional Information

- Network Management (https://docs.netapp.com/us-en/ontap/network-management/)
- Ethernet Storage Design Considerations, Best Practices for Clustered Data ONTAP | TR-4182 (https://www.netapp.com/pdf.html?item=/media/16885-tr-4182.pdf)
- Data ONTAP 8.2 Network Management Guide For 7-Mode (https://library.netapp.com/ecm/ecm_download_file/ECMP1368834)

NetApp provides no representations or warranties regarding the accuracy or reliability or serviceability of any information or recommendations provided in this publication or with respect to any results that may be obtained by the use of the information or observance of any recommendations provided herein. The information in this document is distributed AS IS and the use of this information or the implementation of any recommendations or techniques herein is a customer's responsibility and depends on the customer's ability to evaluate and integrate them into the customer's operational environment. This document and the information contained herein may be used solely in connection with the NetApp products discussed in this document.
