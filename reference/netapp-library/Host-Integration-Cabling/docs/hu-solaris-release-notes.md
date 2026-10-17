# Solaris Host Utilities Release Notes
Source: https://docs.netapp.com/us-en/ontap-sanhost/hu-solaris-release-notes.html
Fetched: 2026-07-07

The Solaris Host Utilities release notes describe new features, enhancements, known issues, limitations, and important cautions related to configuring and managing your specific Solaris host with your ONTAP storage system.

For specific information about the operating system versions and updates that the Host Utilities support, see the Interoperability Matrix Tool (https://imt.netapp.com/matrix/#welcome).

## What's new in Solaris Host Utilities 8.0

- Solaris Host Utilities 8.0 introduces the `disksort:false` and `cache-nonvolatile:true` parameter settings. These parameters suppress constant sync calls from the host. The sync calls impact performance and aren't required because ONTAP doesn't have volatile cache. For more information, see Oracle: Cache Flush Behavior for Flash and NVRAM Storage Devices (https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/tuning/ensuring-proper-cache-flush-behavior-flash-and-nvram-storage-devices.html).
- Solaris Host Utilities 8.0 supports automated updates for FC drivers. The FC drivers that bind the parameters for Solaris 11.4 use SCSI disks. For more information, see Oracle Support Doc ID 2595926.1 (https://support.oracle.com/knowledge/Sun%20Microsystems/2595926_1.html).

## Known issues and limitations

| Bug ID | Affects version | Title | Description |
| --- | --- | --- | --- |
| — | Solaris Host Utilities 8.0 | — | The Solaris Host Utilities 8.0 release only supports Solaris 11.4 with SPARC and x86 platforms. For Solaris 11.3 and earlier versions, you need to use the Solaris Host Utilities 6.2. |
| 1385189 (https://mysupport.netapp.com/site/bugs-online/product/HOSTUTILITIES/BURT/1385189) | Solaris 11.4 | Solaris 11.4 FC driver binding changes required in HUK 6.2 | Solaris 11.4 and HUK recommendations: FC driver binding is changed from `ssd(4D)` to `sd(4D)`. Move configuration that you have in `ssd.conf` to `sd.conf` as mentioned in Oracle (Doc ID 2595926.1). The behavior varies across newly installed Solaris 11.4 systems and systems upgraded from 11.3 or lower versions. |

NetApp Bugs Online (https://mysupport.netapp.com/site/) provides complete information for most known issues, including suggested workarounds where possible. Some keyword combinations and bug types that you might want to use include the following:

- FCP General: Displays FC and host bus adapter (HBA) bugs that are not associated with a specific host.
- FCP - Solaris

## What's next

Learn about installing Solaris Host Utilities: https://docs.netapp.com/us-en/ontap-sanhost/hu-solaris-80.html
