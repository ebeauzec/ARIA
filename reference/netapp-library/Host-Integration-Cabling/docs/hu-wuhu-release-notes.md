# Windows Host Utilities Release Notes
Source: https://docs.netapp.com/us-en/ontap-sanhost/hu-wuhu-release-notes.html
Fetched: 2026-07-07

The release notes describe new features, enhancements, known issues, limitations, and important cautions related to configuring and managing your specific Windows host with your ONTAP storage system.

For specific information about the operating system versions and updates that the Host Utilities support, see the Interoperability Matrix Tool (https://imt.netapp.com/matrix/#welcome).

## What's new in Windows Host Utilities 8.0

Windows Host Utilities 8.0 include additional parameter settings for NVMe/FC drivers. These parameters are automatically loaded when you install the Windows Host Utilities 8.0.

## What's new in Windows Host Utilities 7.2

Windows Host Utilities 7.2 includes support for NVMe/FC driver parameter settings and bug fixes for new vendor cards.

## What's new in Windows Host Utilities 7.1

Windows Host Utilities 7.1 includes support for E-Series storage systems, ONTAP 9 software, and enhanced iSCSI timeouts for faster failover.

## Known issues and limitations

| Title | Affects version | Description | Workaround |
| --- | --- | --- | --- |
| Running the `linux_gos_timeout-install.sh` script is no longer required on Hyper-V guests running Red Hat Enterprise Linux or SUSE Linux Enterprise Server | 7.1 | You are no longer required to run the `linux_gos_timeout-install.sh` script to change disk timeouts on Red Hat Enterprise Linux 5, Red Hat Enterprise Linux 6, or SUSE Linux Enterprise Server 11 Hyper-V guests because the default timeout settings are being used. The `linux_gos_timeout-install.sh` script that was included in previous versions of the Host Utilities is no longer included in the Windows Host Utilities 7.1 version. Windows Host Utilities 7.1 uses the default disk timeout settings. | Not Applicable |

NetApp Bugs Online (https://mysupport.netapp.com/site/bugs-online/product) provides complete information for most known issues, including suggested workarounds where possible.

## What's next

Learn about installing Windows Host Utilities: https://docs.netapp.com/us-en/ontap-sanhost/hu-wuhu-80.html
