# Learn about SAN host configurations
Source: https://docs.netapp.com/us-en/ontap-sanhost/overview.html
Fetched: 2026-07-07

You should configure SAN hosts for multipathing and with specific parameters and settings critical for correct operation with ONTAP LUNs. The host configuration varies depending on the host operating system and the protocol. Correct configuration is important for best performance and successful failover.

You should configure your SAN hosts to use the NetApp SAN Host Utilities. SAN Host Utilities help you manage and monitor your LUNs and host bus adapters (HBAs). For example, you can use the SAN Host Utilities to retrieve a list of all LUNs mapped to a host or to see a list of all the attributes of a specific LUN mapped to a host. NetApp customer support can also use the SAN Host Utilities to gather information about your configuration if you have an issue that requires assistance.

NetApp recommends using the SAN Host Utilities software if it's available for your SAN host.

If your SAN configuration supports SAN booting, you can also configure your host to use SAN booting to simplify deployment and improve scalability. Using SAN boot, you can deploy multiple new servers by connecting them to SAN and configuring the appropriate boot settings. This saves time by eliminating the need to install the operating system on each server individually.

Your SAN hosts and ONTAP storage can reside either on-premises, in the cloud, or both.

> Note: In a cloud environment, hosts are typically referred to as clients. All host-specific information in this content also applies to cloud clients.

For example, you can configure on-premises ONTAP storage to connect to on-premises SAN hosts or SAN cloud clients. You can also configure storage services running on a cloud environment such as Cloud Volumes ONTAP or Amazon FSx for NetApp ONTAP to connect to on-premises SAN hosts or SAN cloud clients.

## Related information

- [ONTAP SAN configuration reference](https://docs.netapp.com/us-en/ontap/san-config/index.html)
- [ONTAP SAN storage management](https://docs.netapp.com/us-en/ontap/san-management/index.html)
- [ONTAP 9 Release Notes](https://library.netapp.com/ecm/ecm_download_file/ECMLP2492508)
- SANtricity related documentation in the E-Series systems documentation: https://docs.netapp.com/us-en/e-series/index.html
