# Linux Host Utilities Release Notes
Source: https://docs.netapp.com/us-en/ontap-sanhost/hu-luhu-release-notes.html
Fetched: 2026-07-07

The release notes describe new features, enhancements, fixed issues, known issues, limitations, and important cautions for configuring and managing your specific host with your ONTAP storage system.

For specific information about the operating system versions and updates that the Host Utilities support, see the Interoperability Matrix Tool (https://imt.netapp.com/matrix/#welcome).

## What's New in Linux Host Utilities 8.0

The Linux Host Utilities 8.0 release contains the following new features and enhancements.

Linux Host Utilities 8.0 includes support for 64-bit speed QLogic and Emulex FC host bus adapters (HBA).

The following operating systems are supported:

- Red Hat Enterprise Linux (RHEL) 9 and 8 series
- SUSE Linux Enterprise Server
- Oracle Linux 9 and 8 series
- Ubuntu

## What's New in Linux Host Utilities 7.1

The Linux Host Utilities 7.1 release contains the following new features and enhancements:

- Linux Host Utilities is now called *Linux Unified Host Utilities* because it supports NetApp E-Series storage systems running SANtricity as well as AFF, FAS, and ASA systems running ONTAP.
- The following operating systems are supported:
  - Citrix XenServer
  - KVM and XEN, RHEV 6.5 and 6.4
  - Oracle VM 3.2 series
  - Oracle Linux 7 and 6 series
  - RHEL 7 and 6 series
  - SUSE Linux Enterprise Server 15 series
  - SUSE Linux Enterprise Server 11 SP4
- On RHEL 6 and 7 hosts, a tuned package for setting server profiles is now supported. You can use the `tuned-adm` command to set different profiles, depending on the environment. For example, you can use the virtual guest profile as a guest virtual machine and the enterprise storage profile for configurations when LUNs from enterprise storage arrays are used. Using these tuned packages can result in improvement in throughput and latency in ONTAP.
- Linux Host Utilities 7.1 adds support for 32GB FC adapters from Broadcom Emulex and Marvell Qlogic.

> Note: NetApp continues to work with the Linux Host Utilities to add support for features after the initial release. For latest information about the features that are supported and the new features that have been added, see the Interoperability Matrix Tool (https://imt.netapp.com/matrix/#welcome).

## Fixed issues

| Fixed in version | Description |
| --- | --- |
| 7.1 | The intermittent host OS failure issue that occurs when running the `sanlun lun show -p` command in SUSE Linux Enterprise Server 12 SP1, Oracle Linux 7.2, RHEL 7.2, and RHEL 6.8. |

## Known issues and limitations

| NetApp Bug ID | Affects version | Title | Description |
| --- | --- | --- | --- |
| 1457017 | 7.1 | `sanlun` installation issues warning messages related to `libdevmapper.so` and `libnl.so` libraries. These warnings do not affect the functionality of `sanlun` kit. | When you execute the Linux Host Utilities CLI command "sanlun fcp show adapter -v" on a SAN host, the command fails with an error message displaying that the library dependencies required for a host bus adapter (HBA) discovery cannot be located: `[root@hostname ~]# sanlun fcp show adapter -v` `Unable to locate /usr/lib64/libHBAAPI.so library` `Make sure the package installing the library is installed & loaded`. Refer to NetApp Bugs Online - 1508554 (https://mysupport.netapp.com/site/bugs-online/product/HOSTUTILITIES/1508554). |

NetApp Bugs Online (https://mysupport.netapp.com/site/bugs-online/product) provides complete information for most known issues, including suggested workarounds where possible.

## What's next

Learn about installing Linux Host Utilities: https://docs.netapp.com/us-en/ontap-sanhost/hu-luhu-80.html
