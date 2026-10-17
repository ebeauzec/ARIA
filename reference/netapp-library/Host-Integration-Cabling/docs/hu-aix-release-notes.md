# AIX Host Utilities Release Notes
Source: https://docs.netapp.com/us-en/ontap-sanhost/hu-aix-release-notes.html
Fetched: 2026-07-07

The release notes describe new features and enhancements, issues fixed in the current release, known issues and limitations, and important cautions related to configuring and managing your specific AIX host with your ONTAP storage system.

For specific information about the operating system versions and updates that the Host Utilities support, see the Interoperability Matrix Tool (https://imt.netapp.com/matrix/#welcome).

The AIX Host Utilities releases contain the following new features and enhancements.

## What's new in AIX Host Utilities 8.0

An IBM Interim Fix (ifix) is available for AIX Host Utilities 8.0 that ensures the `sanlun fcp show adapter –v` command displays the correct HBA speed information, such as supported and negotiated speeds for the adapters. You can install the ifix on the following AIX and VIOS versions:

- AIX: 7.3 TL3 SP0, 7.3 TL2 SP2, 7.3 TL1 SP4, 7.2 TL5 SP9, 7.2 TL5 SP8
- VIOS: 4.1.1.0, 4.1.0.21, 3.1.4.50, 3.1.4.41

## What's new in AIX Host Utilities 7.0

AIX Host Utilities 7.0 supports SCSI UNMAP on the AIX host OS. With AIX Host Utilities 7.0, SCSI thin provisioning functions seamlessly with AIX and NetApp LUNs for FC devices.

## What's new in AIX Host Utilities 6.1

AIX Host Utilities 6.1 includes support for the memory fault issue that occurred in earlier versions of the AIX host OS. With AIX Host Utilities 6.1, only the sanlun binary has changed. The Microsoft Multipath I/O (MPIO) and related ODM remain unchanged.

## Known problems and limitations

| Bug ID | Affects version | Title | Description |
| --- | --- | --- | --- |
| N/A | 7.0 | SCSI UNMAP support for ONTAP iSCSI LUNs | AIX Host Utilities 7.0 only supports the SCSI UNMAP feature for FC devices. SCSI UNMAP support for iSCSI devices are not included in this release. |
| 1069147 (https://mysupport.netapp.com/site/bugs-online/product/HOSTUTILITIES/BURT/1069147) |  | AIX HU Sanlun reports incorrect HBA speed | Instances of sanlun displaying incorrect HBA speeds are reported while running the `sanlun fcp show adapter –v` command. The `sanlun fcp show adapter –v` command displays the HBA cards information, such as supported and negotiated speeds for the adapters. This seems to be a reporting issue only. To identify the actual speed, use the `fcstat fcsx` command. |

NetApp Bugs Online (https://mysupport.netapp.com/site/) provides complete information for most known issues, including suggested workarounds where possible. Some keyword combinations and bug types that you might want to use include the following:

- FCP General: Displays FC and HBA bugs that are not associated with a specific host.
- FCP - AIX

## What's next?

Learn about installing AIX Host Utilities: https://docs.netapp.com/us-en/ontap-sanhost/hu-aix-80.html
