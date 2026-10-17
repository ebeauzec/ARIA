# StorageGRID architecture and network topology
Source: https://docs.netapp.com/us-en/storagegrid/primer/storagegrid-architecture-and-network-topology.html
Fetched: 2026-07-07

Last updated: 01/14/2026 (StorageGRID 12.0; also available for 11.9, 11.8, 11.7, 11.6, 11.5)

A StorageGRID system consists of multiple types of grid nodes at one or more data center sites. See [grid node types](https://docs.netapp.com/us-en/storagegrid/primer/nodes-and-services.html) and [Networking guidelines](https://docs.netapp.com/us-en/storagegrid/network/index.html) for more detail.

## Deployment topologies

A StorageGRID system can be deployed to a single data center site or to multiple data center sites. The maximum number of sites per deployment is 16.

### Single site

Infrastructure and operations are centralized in a single-site deployment.

### Multiple sites

Different types and numbers of StorageGRID resources can be installed at each site (e.g., more storage at one data center than another). Sites are often geographically distributed across different failure domains (e.g., an earthquake fault line or floodplain). Data sharing and disaster recovery are achieved via automated distribution of data to other sites. Multiple logical sites can also exist within a single data center to allow distributed replication and erasure coding for increased availability and resiliency.

### Grid node redundancy

You can optionally include more than one Admin Node or Gateway Node for redundancy (single site or across multiple sites). However, each StorageGRID system can only have one primary Admin Node.

## System architecture

S3 clients store and retrieve objects in StorageGRID. Other clients send email notifications, access the StorageGRID management interface, or optionally access the audit share.

S3 clients can connect to a Gateway Node or an Admin Node to use the load-balancing interface to Storage Nodes, or connect directly to Storage Nodes using HTTPS.

Objects can be stored within StorageGRID on software- or hardware-based Storage Nodes, or in Cloud Storage Pools, which consist of external S3 buckets or Azure Blob storage containers.
