# NetApp supported plug-ins overview
Source: https://docs.netapp.com/us-en/snapcenter/protect-nsp/netapp_supported_plugins_overview.html
Fetched: 2026-07-07

You can use the NetApp supported plug-ins like MongoDB, ORASCPM (Oracle Applications), SAP ASE, SAP MaxDB, and Storage plug-in for applications that you use and then use SnapCenter to backup, restore, or clone these applications. Your NetApp supported plug-ins act as host-side components of the NetApp SnapCenter Software, enabling application-aware data protection and management of resources.

When NetApp supported plug-ins are installed, you can use SnapCenter with NetApp SnapMirror technology to create mirror copies of backup sets on another volume and use NetApp SnapVault technology to perform disk-to-disk backup replication. The NetApp supported plug-ins can be used in both Windows and Linux environments.

Note: SnapCenterCLI does not support NetApp supported plug-ins commands.

NetApp provides the Storage plug-in to perform data protection operations of the data volume on the ONTAP storage using the plug-in framework built into SnapCenter.

You can install the NetApp supported plug-ins from the Add Host page. See: [Add hosts and install plug-in packages on remote hosts](https://docs.netapp.com/us-en/snapcenter/protect-nsp/add_hosts_and_install_plug_in_packages_on_remote_hosts.html).

Note: SnapCenter support policy will cover support for the plug-in framework, core engine, and the associated APIs. Support will not cover the plug-in source code and the associated scripts built on the plug-in framework.
