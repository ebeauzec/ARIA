# Introduction of NetApp Disaster Recovery using Amazon Elastic VMware Service and Amazon FSx for NetApp ONTAP
Source: https://docs.netapp.com/us-en/bluexp-disaster-recovery/reference/evs-deploy-guide-introduction.html
Fetched: 2026-07-07

Note: This URL now redirects to https://docs.netapp.com/us-en/data-services-disaster-recovery/reference/evs-deploy-guide-introduction.html

Last updated: 10/01/2025

Increasingly, customers have become more dependent on virtualized infrastructures for production compute workloads such as those based on VMware vSphere. As these virtual machines (VMs) have become more critical to their businesses, customers need to protect these VMs from the same types of disasters as their physical compute resources. Disaster recovery (DR) solutions currently offered are complex, expensive, and resource intensive. NetApp, the largest storage provider used for virtualized infrastructures, created the NetApp Disaster Recovery service to protect VMs the same way it protects ONTAP storage-hosted data of any type.

One of the primary challenges with any DR solution is managing the incremental cost of purchasing, configuring, and maintaining additional compute, network, and storage resources just to provide a DR replication and recovery infrastructure. One popular option for protecting critical on-premises virtual resources is to use cloud-hosted virtual resources as the DR replication and recovery infrastructure. Amazon is one example of such a solution that can provide cost-effective resources compatible with NetApp ONTAP hosted VM infrastructures.

Amazon introduced its Amazon Elastic VMware Service (Amazon EVS) that enables VMware Cloud Foundation within your virtual private cloud (VPC). Amazon EVS provides the resilience and performance of AWS along with familiar VMware software and tools, enabling Amazon EVS vCenters to be integrated as an extension of your on-premises virtualized infrastructure.

While Amazon EVS comes with included storage resources, using native storage can reduce its effectiveness for organizations with storage-heavy workloads. In these cases, teaming Amazon EVS with Amazon FSx for NetApp ONTAP storage (Amazon FSxN) can provide a more flexible storage solution. When you are using NetApp ONTAP storage solutions on-premises to host your VMware infrastructure, using Amazon EVS with FSx for ONTAP means you get best-in-class data interoperability and protection features between your on-premises and cloud-hosted infrastructures.

For information about Amazon FSx for NetApp ONTAP, see [Getting started with Amazon FSx for NetApp ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/getting-started.html).
