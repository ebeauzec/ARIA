# Administer Cloud Volumes ONTAP using System Manager
Source: https://docs.netapp.com/us-en/bluexp-cloud-volumes-ontap/task-administer-advanced-view.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-administer-advanced-view.html (feature formerly called "Advanced View", now "System Manager").

Last updated: 01/09/2026

Advanced storage management capabilities in Cloud Volumes ONTAP are available through ONTAP System Manager, a management interface provided with ONTAP systems. You can access System Manager directly from the NetApp Console.

## Features

- Advanced storage management: Manage consistency groups, shares, qtrees, quotas, and Storage VMs.
- Volume move: Move a volume to a different aggregate.
- Networking management: Manage IPspaces, network interfaces, portsets, and ethernet ports.
- Manage FlexGroup volumes: You can create and manage FlexGroup volumes only through System Manager. The Console does not support FlexGroup volume creation.
- Events and jobs: View event logs, system alerts, jobs, and audit logs.
- Advanced data protection: Protect storage VMs, LUNs, and consistency groups.
- Host management: Set up SAN initiator groups and NFS clients.
- ONTAP S3 object storage management: available only in System Manager, not in the Console.

## Supported configurations

- Advanced storage management through ONTAP System Manager is available in Cloud Volumes ONTAP 9.10.0 and later in standard cloud regions.
- System Manager integration is not supported in GovCloud regions or in regions that have no outbound internet access.

## Limitations

- NetApp Cloud Tiering: Cloud Volumes ONTAP does not support Cloud Tiering; set up tiering of data to object storage directly from the Standard View when creating volumes.
- Tiers: Aggregate management (including local tiers and cloud tiers) is not supported from System Manager; manage aggregates directly from the Standard View.
- Firmware upgrades: Cloud Volumes ONTAP does not support automatic firmware updates from Cluster > Settings in System Manager.
- Role-based access control: not supported from System Manager.
- SMB Continuous Availability (CA): Cloud Volumes ONTAP does not support continuously available SMB shares for nondisruptive operations.

## Configure authentication for accessing System Manager

As an administrator, you can activate authentication for users accessing ONTAP System Manager from the Console. If authentication is enabled, users must enter ONTAP user credentials every time they access System Manager from the Console (credentials aren't stored internally) or when the page reloads. If disabled, users can access System Manager using admin credentials.

> Note: This setting applies per Console agent for the ONTAP users in your organization or account, irrespective of the Cloud Volumes ONTAP system.

**Required permissions**: organization or account admin privileges to modify Console agent settings for CVO user authentication.

**Steps**

1. From the left navigation pane, go to **Administration > Agents**.
2. Click the action icon for the required Console agent and select **Edit Console agent**.
3. Under **Force user credentials**, select the **Enable/Disable** check box (disabled by default).

   > Note: If you set this to Enable, authentication is reset, and you have to modify any existing workflows to accommodate this change.

4. Click **Save**.

## Get started with System Manager

1. From the left navigation menu, select **Storage > Management**.
2. On the **Systems** page, double click the required Cloud Volumes ONTAP system.
3. Click **System Manager**.
4. If prompted, enter your ONTAP user credentials and click **Login**.
5. If a confirmation message appears, read it and click **Close**.

Use System Manager to manage your Cloud Volumes ONTAP system. Click **Go back** to return to the Console.

## Help with using System Manager

Refer to the [ONTAP documentation](https://docs.netapp.com/us-en/ontap/index.html), including:

- ONTAP roles, applications, and authentication
- Use System Manager to access a cluster
- Volume and LUN management
- Network management
- Data protection
- Create continuously available SMB shares
