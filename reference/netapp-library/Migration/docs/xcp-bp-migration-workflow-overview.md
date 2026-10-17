# Migration workflow
Source: https://docs.netapp.com/us-en/netapp-solutions/xcp/xcp-bp-migration-workflow-overview.html
Fetched: 2026-07-07

Migration has different phases to follow for better planning and completion of the migration. To migrate data from third-party NAS storage or directly attached NAS exported storage using NetApp XCP, follow the migration guidelines provided in this section.

## On-premises

The migration workflow from any NAS to NetApp NAS includes the following steps:

1. Discover the NAS shares and data.
2. Scan the data and produce a report to find the layout of the data.
3. Create a baseline by running the XCP Copy command. For faster migrations, select more XCP instances and split the workload at the subfolder level to initiate parallel migration jobs.
4. For incremental updates, use XCP sync until the change rate is low for the cutover window.
5. Mark the source as read-only to perform a final sync by running the XCP sync command to complete the migration.
6. To verify that the data transferred correctly, compare the source and destination by running the `xcp verify` command.

## Cloud

For the cloud, you can follow a similar on-premises migration workflow if the connectivity between on-premises and the cloud is direct connect (AWS), ExpressRoute (Azure), or cloud interconnect (GCP).

If there is no direct internet connection between on-premises and the cloud, you must transfer the data from on-premises to the cloud through an offline data transport method such as truck (physical data transport appliance). Each cloud service provider has a different method with different terminology to move data to their data center.

You can use a similar architecture (data mover solution for on-premises to Azure without ExpressRoute) with the respective components from the various cloud service providers.

(Diagrams referenced in source: xcp-bp_image3.png [on-prem workflow], xcp-bp_image4.png [cloud workflow], xcp-bp_image5.png [Azure data mover] — not reproduced here.)
