# Learn about NetApp Copy and Sync
Source: https://docs.netapp.com/us-en/data-services-copy-sync/concept-cloud-sync.html
Fetched: 2026-07-07

NetApp Copy and Sync offers a simple, secure, and automated way to migrate your data to any target, in the cloud or on your premises. Whether it's a file-based NAS dataset (NFS or SMB), Amazon S3 object format, a NetApp StorageGRID appliance, or any other cloud provider object store, Copy and Sync can convert and move it for you.

## NetApp Console

NetApp Copy and Sync is accessible through the NetApp Console, which provides centralized management of NetApp storage and data services across on-premises and cloud environments at enterprise grade. The Console is required to access and use NetApp data services and enables managing many storage resources from one interface. Console administrators can control access to storage and services for all systems within the enterprise.

No license or subscription is needed to start using NetApp Console; charges are only incurred when you deploy Console agents in your cloud to ensure connectivity to your storage systems or NetApp data services. Some NetApp data services accessible from the Console are licensed or subscription-based.

## How NetApp Copy and Sync works

NetApp Copy and Sync is a SaaS platform consisting of a data broker group, a cloud-based interface available through the NetApp Console, and a source and target.

The NetApp data broker software syncs data from a source to a target (a *sync relationship*). You can run the data broker in AWS, Azure, Google Cloud Platform, or on your premises. A data broker group (one or more data brokers) needs an outbound internet connection over port 443 to communicate with Copy and Sync and contact other services/repositories.

After the initial copy, Copy and Sync syncs any changed data based on the schedule you set.

## Supported storage types

- Any NFS server
- Any SMB server
- Amazon EFS
- Amazon FSx for ONTAP
- Amazon S3
- Azure Blob
- Azure Data Lake Storage Gen2
- Azure NetApp Files
- Box (available as a preview)
- Cloud Volumes ONTAP
- Google Cloud Storage
- Google Drive
- IBM Cloud Object Storage
- On-premises ONTAP cluster
- ONTAP S3 Storage
- SFTP (using API only)
- StorageGRID

## Costs

Two types of costs are associated with using Copy and Sync: resource charges and service charges.

- Resource charges: compute and storage costs for running one or more data brokers in the cloud.
- Service charges: after the 14-day free trial ends, either subscribe from AWS or Azure (hourly or annually) or purchase licenses directly from NetApp.
