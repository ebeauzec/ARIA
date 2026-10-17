# Networking guidelines for StorageGRID
Source: https://docs.netapp.com/us-en/storagegrid/network/
Fetched: 2026-07-07

Last updated: 06/12/2026 (StorageGRID 12.0; also available for 11.9, 11.8, 11.7, 11.6, 11.5)

Use these guidelines to learn about StorageGRID architecture and networking topologies and to learn the requirements for network configuration and provisioning.

## About these instructions

These guidelines provide information to create the StorageGRID networking infrastructure before deploying and configuring StorageGRID nodes, ensuring communication can occur among all grid nodes and between the grid and external clients/services.

External clients and services need to connect to StorageGRID networks to perform functions such as:

- Store and retrieve object data
- Receive email notifications
- Access the StorageGRID management interface (Grid Manager and Tenant Manager)
- Access the audit share (optional)
- Provide services such as Network Time Protocol (NTP), Domain Name System (DNS), Key Management Server (KMS)

StorageGRID networking must be configured appropriately to handle traffic for these functions and more.

## Before you begin

Configuring StorageGRID networking requires a high level of experience with Ethernet switching, TCP/IP networking, subnets, network routing, and firewalls.

Before configuring networking, become familiar with StorageGRID architecture as described in [Learn about StorageGRID](https://docs.netapp.com/us-en/storagegrid/primer/index.html).

After determining which StorageGRID networks to use and how they'll be configured, install and configure StorageGRID nodes:

- **Install appliance nodes**: [Install appliance hardware](https://docs.netapp.com/us-en/storagegrid-appliances/installconfig/index.html)
- **Install software-based nodes**: [Install StorageGRID on software-based nodes](https://docs.netapp.com/us-en/storagegrid/swnodes/index.html)
- **Configure and administer StorageGRID software**: [Administer StorageGRID](https://docs.netapp.com/us-en/storagegrid/admin/index.html); [Release notes](https://library.netapp.com/ecm/ecm_download_file/ECMLP3351267) (requires NetApp account sign-in)
