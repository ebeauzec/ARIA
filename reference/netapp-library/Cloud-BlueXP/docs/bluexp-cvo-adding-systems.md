# Add an existing Cloud Volumes ONTAP system to NetApp Console
Source: https://docs.netapp.com/us-en/bluexp-cloud-volumes-ontap/task-adding-systems.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/storage-management-cloud-volumes-ontap/task-adding-systems.html

Last updated: 02/18/2026

You can discover and add existing Cloud Volumes ONTAP systems to the NetApp Console for centralized management. When you onboard a system with an account, the system is registered with that account. In environments with multiple accounts or organizations, you can only discover and manage systems registered with your Console login account.

When working with system registrations, ensure that all actions are performed within the same organization and account where the systems were originally onboarded. For example, you can move a Cloud Volumes ONTAP system to a new Console agent when the migration stays within the same organization.

> CAUTION: You can't discover, view, or manage systems that are registered with a different account or organization.

## Before you begin

You must know the password for the Cloud Volumes ONTAP admin user account.

## Steps

1. From the left navigation menu, select **Storage > Management**.
2. On the **System** page, click **Add System**.
3. Select the cloud provider in which the system resides.
4. Choose the type of Cloud Volumes ONTAP system to add.
5. Click the link to discover an existing system.
6. On the Region page, select a region. You can see the systems that are running in the selected region.

   > Note: Cloud Volumes ONTAP systems are represented as instances on this page. From the list, you can select only those instances that are registered with the current account.

7. On the Credentials page, enter the password for the Cloud Volumes ONTAP admin user, and then select **Go**.

## Result

The Console adds the Cloud Volumes ONTAP systems to the **Systems** page.
