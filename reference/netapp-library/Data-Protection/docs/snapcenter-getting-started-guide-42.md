# SnapCenter Software 4.2 Getting Started Guide
Source: https://docs.netapp.com/a/snap/snapcenter/4.2/Getting-Started-Guide.pdf
Fetched: 2026-07-07

SnapCenter® Software 4.2 Getting Started Guide
August 2019 | 215-14400_2019-08_en-us

## Deciding whether to read the SnapCenter Getting Started information

Read this information if you want streamlined workflows for installing SnapCenter Server and SnapCenter plug-ins, and creating backups and generating reports. You can also read about SnapCenter architecture.

For detailed information on each step in the workflows, see the SnapCenter installation and setup information.

## SnapCenter overview

SnapCenter Software is a simple, centralized, scalable platform that provides application-consistent data protection for applications, databases, host file systems, and VMs running on ONTAP systems anywhere in the Hybrid Cloud.

SnapCenter leverages NetApp Snapshot, SnapRestore, FlexClone, SnapMirror, and SnapVault technologies to provide the following:
- Fast, space-efficient, application-consistent, disk-based backups
- Rapid, granular restore and application-consistent recovery
- Quick, space-efficient cloning

SnapCenter includes both the SnapCenter Server and individual lightweight plug-ins. You can automate deployment of plug-ins to remote application hosts, schedule backup, verification, and clone operations, and monitor all data protection operations.

SnapCenter can be deployed in the following ways:
- On premise to protect the following:
  - Data that is on ONTAP FAS or AFF primary systems and replicated to ONTAP FAS or AFF secondary systems
  - Data that is on ONTAP Select primary systems
- On premise in a Hybrid Cloud to protect the following:
  - Data that is on ONTAP FAS or AFF primary systems and replicated to Cloud Volumes ONTAP or NetApp Private Storage secondary systems
- In a public cloud to protect the following:
  - Data that is on Cloud Volumes ONTAP (formerly ONTAP Cloud) primary systems

SnapCenter includes the following key features:
- **Centralized, application-consistent data protection** — supported for Microsoft Exchange Server, Microsoft SQL Server, Oracle Databases on Linux, SAP HANA database, and Windows Host Filesystems running on ONTAP systems. Also supports other standard or custom applications/databases via a framework for user-defined SnapCenter plug-ins (e.g., IBM DB2, MongoDB, MySQL via NetApp Automation Store).
- **Policy-based backups** — leverage NetApp Snapshot copy technology to create fast, space-efficient, application-consistent, disk-based backups. Optionally automate protection of these backups to secondary storage via updates to existing protection relationships.
- **Backups for multiple resources** — back up multiple resources (applications, databases, or host file systems) of the same type at the same time using SnapCenter resource groups.
- **Restore and recovery** — rapid, granular restores of backups and application-consistent, time-based recovery. Restore from any destination in the Hybrid Cloud.
- **Cloning** — quick, space-efficient, application-consistent cloning, enabling accelerated software development. Clone on any destination in the Hybrid Cloud.
- **Single user management GUI** — one-stop interface for managing backups and clones of a resource in any destination in the Hybrid Cloud.
- **REST APIs, Windows cmdlets, Linux commands** — REST APIs for most functionality for integration with any orchestration software, plus Windows PowerShell cmdlets and a Linux command-line interface.
- **Centralized data protection Dashboard and reporting**
- **Role-Based Access Control (RBAC)** for security and delegation.
- **Repository database with High Availability** — built-in repository database with HA to store all backup metadata.
- **Automated push install of plug-ins** — automate a remote push of SnapCenter plug-ins from the SnapCenter Server host to application hosts.
- **Load balancing and High Availability** — for the SnapCenter Server, provided by integration with Application Request Routing (ARR) and Microsoft Windows Network Load Balancing (NLB), with support for horizontal scaling.

Note: The SnapCenter 4.1.1 documentation covers protecting virtualized databases/file systems using the SnapCenter 4.1.1 Plug-in for VMware vSphere. The NetApp Data Broker, SnapCenter Plug-in for VMware vSphere, documentation covers protecting virtualized databases/file systems using the Linux-based NetApp Data Broker virtual appliance (OVA format) for SnapCenter 4.2. Related docs: Deployment Guide for SnapCenter Plug-in for VMware vSphere; Data Protection Guide for VMs, Datastores, and VMDKs using the SnapCenter Plug-in for VMware vSphere; NetApp Data Broker Release Notes.

### SnapCenter architecture

The SnapCenter platform is based on a multitiered architecture that includes a centralized management server (SnapCenter Server) and a SnapCenter plug-in host. SnapCenter supports multisite data centers — the SnapCenter Server and the plug-in host can be at different geographical locations.

### SnapCenter components

SnapCenter consists of the SnapCenter Server and SnapCenter plug-ins. Install only the plug-ins appropriate for the data you want to protect.

- **SnapCenter Server**
- **SnapCenter Plug-ins Package for Windows**, includes:
  - SnapCenter Plug-in for Microsoft SQL Server
  - SnapCenter Plug-in for Microsoft Windows
  - SnapCenter Plug-in for Microsoft Exchange Server
  - SnapCenter Plug-in for SAP HANA Database
- **SnapCenter Plug-ins Package for Linux**, includes:
  - SnapCenter Plug-in for Oracle Database
  - SnapCenter Plug-in for UNIX (not standalone; must be installed with Plug-in for Oracle Database)
  - SnapCenter Plug-in for SAP HANA Database
- **SnapCenter Custom Plug-ins** — community-supported, downloadable from NetApp ToolChest or NetApp Storage Automation Store.
- **NetApp Data Broker** — SnapCenter Plug-in for VMware vSphere.

### SnapCenter licenses

SnapCenter requires several licenses depending on your storage environment and features:
- **SnapCenter Standard controller-based licenses** — required for FAS or AFF storage controllers.
- **SnapCenter Standard capacity-based licenses** — required to protect data on ONTAP Select and ONTAP Cloud platforms.
- **ONTAP licenses**, one of: SnapMirror license or SnapVault license.
- **Additional licenses** — e.g., SnapRestore, FlexClone, vSphere Standard, protocol-based licenses. See Release Notes for the complete list.

Best Practice: It is recommended (not required) to also add SnapCenter Standard licenses to secondary destinations. Without them, SnapCenter cannot be used after a failover operation. A FlexClone license is required on secondary destinations for clone and verification operations.

### SnapCenter plug-ins

Each SnapCenter plug-in supports specific environments, databases, and applications.

| Plug-in | Included in package | Requires | Installed on | OS |
|---|---|---|---|---|
| Plug-in for SQL Server | Plug-ins Package for Windows | Plug-in for Windows | SQL Server host | Windows |
| Plug-in for Windows | Plug-ins Package for Windows | — | Windows host | Windows |
| Plug-in for Exchange | Plug-ins Package for Windows | Plug-in for Windows | Exchange Server host | Windows |
| Plug-in for Oracle Database | Plug-ins Package for Linux | Plug-in for UNIX | Oracle host | Linux |
| Plug-in for SAP HANA Database | Plug-ins Package for Linux and Windows | Plug-in for UNIX or Plug-in for Windows | HDBSQL client host | Linux or Windows |
| Custom Plug-ins | NetApp ToolChest | For file system backups, Plug-in for Windows | Custom application host | Linux or Windows |
| Plug-in for VMware vSphere | NetApp Data Broker (.ova file) | — | Linux VM host | Linux or Windows |

**SnapCenter Plug-in for Microsoft SQL Server features**
- Automates application-aware backup, restore, and clone operations for Microsoft SQL Server databases.
- Supports SQL Server databases on VMDK and RDM LUNs when also deploying the NetApp Data Broker virtual appliance and enabling the Plug-in for VMware vSphere.
- Supports provisioning SMB shares only (no backup support for SQL Server databases on SMB shares).
- Supports importing backups from SnapManager for Microsoft SQL Server to SnapCenter.

**SnapCenter Plug-in for Microsoft Windows features**
- Enables application-aware data protection for other plug-ins running on Windows hosts.
- Automates application-aware backup, restore, and clone operations for Microsoft file systems.
- Supports storage provisioning, Snapshot copy consistency, and space reclamation for Windows hosts.
- Note: Provisions SMB shares and Windows file systems on physical and RDM LUNs but does not support backup operations for Windows file systems on SMB shares.

**SnapCenter Plug-in for Microsoft Exchange Server features**
- Automates application-aware backup and restore operations for Microsoft Exchange Server databases and Database Availability Groups (DAGs).
- Supports virtualized Exchange Servers on RDM LUNs when also deploying the NetApp Data Broker virtual appliance and enabling the Plug-in for VMware vSphere.
- Supports migrating backups from SnapManager 7.x to SnapCenter.

**SnapCenter Plug-in for Oracle Database features**
- Automates application-aware backup, restore, recovery, verify, mount, unmount, and clone operations for Oracle databases.
- Supports Oracle databases for SAP (SAP BR*Tools integration not provided).
- Supports importing backups from SnapManager for Oracle and SnapManager for SAP to SnapCenter.

**SnapCenter Plug-in for UNIX features**
- Enables the Plug-in for Oracle Database to perform data protection operations by handling the underlying host storage stack on Linux systems.
- Supports NFS and SAN protocols on a storage system running ONTAP.
- Supports Oracle databases on VMDK and RDM LUNs when also deploying the NetApp Data Broker virtual appliance and enabling the Plug-in for VMware vSphere.

**SnapCenter Plug-in for SAP HANA Database features**
- Automates application-aware backup, restore, and cloning of SAP HANA databases.

**SnapCenter Custom Plug-ins features**
- Supports custom plug-ins for applications/databases not supported by other SnapCenter plug-ins (not included with base install).
- Supports creating mirror copies of backup sets on another volume and disk-to-disk backup replication.
- Supports both Windows and Linux environments; in Windows, custom apps can optionally use the Plug-in for Microsoft Windows for file system consistent backups.
- MySQL, DB2, and MongoDB custom plug-in samples can be downloaded from NetApp ToolChest; you can create your own using the developer's guide. Note: MySQL, DB2, and MongoDB custom plug-ins are supported via NetApp communities only. NetApp supports the capability to create/use custom plug-ins, but the custom plug-ins themselves are not supported by NetApp.

### Installation and navigation tour videos for SnapCenter
- Video: Overview of the SnapCenter interface (first of two).
- Video: Tour through the SnapCenter interface (second of two) — monitoring backup operations, log reports, reporting, scheduling backups, managing clones.

## Preparing storage systems for SnapMirror and SnapVault replication

You can use a SnapCenter plug-in with ONTAP SnapMirror technology to create mirror copies of backup sets on another volume, and with ONTAP SnapVault technology to perform disk-to-disk backup replication for standards compliance and other governance-related purposes. Before performing these tasks, you must configure a data-protection relationship between the source and destination volumes and initialize the relationship.

Note: If you are coming to SnapCenter from a NetApp SnapManager product and are satisfied with existing data protection relationships, you can skip this section.

A data protection relationship replicates data on primary storage (source volume) to secondary storage (destination volume). When you initialize the relationship, ONTAP transfers the data blocks referenced on the source volume to the destination volume.

**Important:** SnapCenter does not support cascade relationships between SnapMirror and SnapVault volumes (Primary > Mirror > Vault). Use fanout relationships only (Primary > Mirror, Primary > Vault).

SnapCenter supports the management of version-flexible SnapMirror relationships. See the ONTAP documentation for details on setting these up.

## Workflow overview

To get started with SnapCenter: install the SnapCenter Server, add a host (which automatically installs the appropriate plug-in), then run a backup.

### Workflow 1: Prepare for installation

Before installing SnapCenter, verify that your environment meets all SnapCenter requirements.

1. **Check host requirements** — domain/workgroup requirements, space/sizing requirements, SAN host requirements, operating system requirements, connection/port requirements, SnapCenter repository requirements.
2. **Check supported storage systems, applications, and browsers** — supported storage systems (ONTAP) and applications; supported browsers (Chrome, Internet Explorer, Microsoft Edge); high availability for the SnapCenter MySQL repository.
3. **Check licensing requirements** — viewing, retrieving, and adding SnapCenter Standard controller-based and capacity-based licenses.

### Workflow 2: Install and configure SnapCenter Server

1. **Install SnapCenter Server.**
   - Download the SnapCenter Server installation package from the NetApp Support Site (NetApp Downloads: SnapCenter Software).
   - Initiate installation by double-clicking the downloaded Version.exe file. Prechecks run automatically; warnings can be ignored, but errors must be fixed.
   - Review auto-populated values required for installation and modify if needed. (No need to specify the MySQL Server repository database password — it is auto-generated.)
   - Click Install Now.

2. **Log in to SnapCenter Server.**
   - Launch SnapCenter from the desktop shortcut, the URL provided at the end of installation, or the URL from your SnapCenter administrator.
   - Enter credentials. Username formats:
     - Domain administrator: `NetBIOS\UserName` or `UserName@UPN suffix` (e.g., [e-mail address omitted])
     - Domain: `FQDN\UserName`
     - Local administrator: `UserName`
   - If assigned more than one role, select the role for this session.
   - Note: Untrusted Active Directory domains must be registered with SnapCenter before proceeding.

3. **Configure role-based access control (RBAC).**
   - Add users/groups to roles: Settings > Roles > select role > Modify > Next through to Users/Groups page > specify domain, enter user/group, Add > Next > Finish.
   - Assign users/groups access to assets: Settings > User Access > select asset type from dropdown > Assign > select Domain or Workgroup authentication type > enter info > Add > OK.

4. **Add the storage system.**
   If replicating Snapshot copies to a SnapMirror or SnapVault destination, set up storage system connections for both destination and source SVM.
   - Storage Systems > New. Enter:
     - Storage System: unique name or IP address.
     - User name/Password: credentials (usually "vsadmin" for an SVM, "admin" for a cluster).
     - EMS & AutoSupport Settings: optionally send EMS messages to storage system syslog, or AutoSupport messages for applied protection, completed/failed restore operations. Selecting "Send AutoSupport Notification for failed operations to storage system" also selects "Log SnapCenter Server events to syslog" (EMS messaging required for AutoSupport notifications).
     - Platform: select platform; if SVM is secondary storage in a backup relationship, select the Secondary checkbox.
     - Protocol: typically HTTPS.
     - Port: storage system's accepted port (defaults typically work).
     - Timeout: seconds before communication attempts halt (default 60).
     - Preferred IP: if SVM has multiple management interfaces, select and enter preferred IP.

5. **Add licenses.**
   - Controller-based license via ONTAP CLI: `system license add -license-code license_key`; verify with `license show`.
   - Capacity-based license via SnapCenter GUI: Settings > Software > License icon > enter info in wizard > select license method > on Notifications page set capacity threshold for email/EMS/AutoSupport notifications (default 90%) > Settings > Global Settings > Notification Server Settings to configure SMTP for email (recommend enabling AutoSupport).

6. **Provision LUNs, SMB shares, or VMDKs for Windows environments.**
   You can assign NetApp storage to supported Windows Server hosts (requires SnapCenter Plug-ins Package for Windows installed via adding a Windows host); can also provision LUNs on supported VMware guest OSes on supported ESXi versions.
   - **Configure LUN storage** (FC- or iSCSI-connected, or connect existing LUN):
     - Establish iSCSI session: Hosts > iSCSI Session > select SVM for target > select host > Establish Session > enter info > Connect. Repeat per target.
     - Create igroups: Hosts > Igroup > New > define igroup > OK.
     - Create disks: Hosts > Disks > select host > New > define disk in wizard > Finish.
   - **Create SMB shares** (SnapCenter UI or PowerShell cmdlets; cmdlets recommended for template-based automation):
     - Hosts > Shares > select SVM > New > define share in New Share dialog > OK.

### Workflow 3: Add hosts and install plug-ins

Use the SnapCenter Add Host wizard to add hosts and install plug-in packages automatically on the specified remote hosts.

Note: SnapCenter 4.1.1 docs cover the 4.1.1 Plug-in for VMware vSphere; NetApp Data Broker docs cover the Linux-based NetApp Data Broker virtual appliance (OVA) for SnapCenter 4.2 (Deployment Guide for SnapCenter Plug-in for VMware vSphere; Data Protection Guide for VMs, Datastores, and VMDKs using the SnapCenter Plug-in for VMware vSphere).

1. **Log in to SnapCenter Server** — start SnapCenter, enter credentials (Domain\UserName), select role if applicable.
2. **Prepare for the plug-in installation** — know storage types each plug-in supports and installation prerequisites.
3. **Set up credentials** — SnapCenter uses credentials to authenticate users for operations. Create credentials for installing plug-ins and separate credentials for data protection operations on databases/Windows file systems. The credential user must have administrator privileges including on the remote host.
   - Settings > Credentials > New > enter info. Username formats: Built-in domain administrator (`NetBIOS\username`, `username@upn`, `DomainFQDN\username`); Built-in local administrator (`username`).
4. **Add hosts and install plug-ins remotely.**
   - Hosts > Managed Hosts tab > Add > enter info:
     - Hosts page: select host type and enter host info (determines which plug-in(s) install). Note: before adding a vSphere host, deploy the NetApp Data Broker virtual appliance and enable the Plug-in for VMware vSphere.
     - Installed plug-ins: review currently installed plug-in packages (none for new deployments).
     - Select Plug-ins to Install: choose plug-ins.
5. **If required, click More Options for additional configuration:**
   - Plug-in for Microsoft SQL Server: configure host log directory — Hosts > Managed Hosts > select SQL host > Configure Plug-in > Browse > enter log directory info > Next.
   - Plug-ins Package for Linux: SnapCenter Plug-in Loader service starts automatically after install.
   - Plug-in for SAP HANA Database: add databases to back up — select plug-in from left nav dropdown > Resources > Add SAP HANA Database > Provide Resource Details > Provide Storage Footprint (select storage system, choose volumes/LUNs/qtrees, Save; can add more from other storage systems) > Resource Settings > enter required info.
6. **If needed, import data from SnapManager:**
   - Microsoft SQL Server: only backups archived using SnapVault technology can be imported from SnapManager for Microsoft SQL Server.
   - Oracle: import data from SnapManager for Oracle and SnapManager for SAP.

### Workflow 4: Run backups (and restore and clone, if needed)

1. **Define backup strategy** — determine databases/files to back up, timing, retention count/duration, and pre/post-backup scripts.
2. **Create or select backup policies** — policies define backup type, frequency, retention, and replication. Settings > Policies > New > enter info in wizard.
3. **Create resource groups, attach policies, and create schedules** — resource groups define resources to back up, policy used, and backup schedule. Resources > select plug-in > Database or File Systems from View dropdown > New Resource Group > enter info in wizard.
4. **Run backups** — resources in resource groups back up automatically per associated policies/schedules; individual resources or resource groups can also be backed up on demand. Resources > select plug-in > select resource type from View dropdown > select resources > enter info in wizard.
5. **If needed, restore backups** — restore data from one or more backups to the active file system. File system restores copy data from a specified backup to the original location; database restores copy data and logs to a specified database.
6. **If needed, clone backups** — clone operations create a copy of a backup.

### Workflow 5: Monitor operations and generate reports

1. **Monitor jobs, schedules, events, and logs** — Monitor menu > Jobs, Schedules, Events, or Logs. For jobs: select job type and status > Apply > select a backup > Details.
2. **Generate reports** — Dashboard > select plug-in from Protection Summary tile > click a pie slice in the chart > Reports tab > configure report > Apply.

## Copyright

Copyright © 2019 NetApp, Inc. All rights reserved. Printed in the U.S. Software derived from copyrighted NetApp material is subject to NetApp's standard license and disclaimer (provided "AS IS" without warranties; NetApp not liable for damages arising from use).

## Trademark

NETAPP, the NETAPP logo, and the marks listed on the NetApp Trademarks page are trademarks of NetApp, Inc. Other company and product names may be trademarks of their respective owners.

## How to send comments about documentation and receive update notifications

Email: [e-mail address omitted]. Include product name, version, and OS in the subject line. Follow @NetAppDoc on Twitter for release notifications.

NetApp, Inc., 1395 Crossman Ave., Sunnyvale, CA 94089 U.S. Telephone: +1 (408) 822-6000. Fax: +1 (408) 822-4501. Support telephone: +1 (888) 463-8277.
