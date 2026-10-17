# Learn about Trident
Source: https://docs.netapp.com/us-en/trident/trident-get-started/intro.html
Fetched: 2026-07-07

Trident is a fully-supported open source project maintained by NetApp. It has been designed to help you meet your containerized application's persistence demands using industry-standard interfaces, such as the Container Storage Interface (CSI).

## What is Trident?

Netapp Trident enables consumption and management of storage resources across all popular NetApp storage platforms, in the public cloud or on premises, including on-premises ONTAP clusters (AFF, FAS, and ASA), ONTAP Select, Cloud Volumes ONTAP, Element software (NetApp HCI, SolidFire), Azure NetApp Files, Amazon FSx for NetApp ONTAP, and Google Cloud NetApp Volumes.

Trident is a Container Storage Interface (CSI) compliant dynamic storage orchestrator that natively integrates with [Kubernetes](https://kubernetes.io/). Trident runs as a single Controller Pod plus a Node Pod on each worker node in the cluster. Refer to [Trident architecture](https://docs.netapp.com/us-en/trident/trident-get-started/architecture.html) for details.

Trident also provides direct integration with the Docker ecosystem for NetApp storage platforms. The NetApp Docker Volume Plugin (nDVP) supports the provisioning and management of storage resources from the storage platform to Docker hosts. Refer to [Deploy Trident for Docker](https://docs.netapp.com/us-en/trident/trident-docker/deploy-docker.html) for details.

> Note: If this is your first time using Kubernetes, you should familiarize yourself with the [Kubernetes concepts and tools](https://kubernetes.io/docs/home/).

## Supported Kubernetes platforms

Trident is supported on a range of Kubernetes distributions and platforms.

Supported platforms include:
- Upstream Kubernetes
- Red Hat OpenShift
- SUSE Harvester 1.7.0 (ONTAP iSCSI)

## Kubernetes integration with NetApp products

The NetApp portfolio of storage products integrates with many aspects of a Kubernetes cluster, providing advanced data management capabilities, which enhance the functionality, capability, performance, and availability of the Kubernetes deployment.

**Amazon FSx for NetApp ONTAP** — [Amazon FSx for NetApp ONTAP](https://www.netapp.com/aws/fsx-ontap/) is a fully managed AWS service that lets you launch and run file systems powered by the NetApp ONTAP storage operating system.

**Azure NetApp Files** — [Azure NetApp Files](https://www.netapp.com/azure/azure-netapp-files/) is an enterprise-grade Azure file share service, powered by NetApp. You can run your most demanding file-based workloads in Azure natively, with the performance and rich data management you expect from NetApp.

**Cloud Volumes ONTAP** — [Cloud Volumes ONTAP](https://www.netapp.com/cloud-services/cloud-volumes-ontap/) is a software-only storage appliance that runs the ONTAP data management software in the cloud.

**Google Cloud NetApp Volumes** — [Google Cloud NetApp Volumes](https://bluexp.netapp.com/google-cloud-netapp-volumes) is a fully managed file storage service in Google Cloud that provides high-performance, enterprise-grade file storage.

**Element software** — [Element](https://www.netapp.com/data-management/element-software/) enables the storage administrator to consolidate workloads by guaranteeing performance and enabling a simplified and streamlined storage footprint.

**NetApp HCI** — [NetApp HCI](https://docs.netapp.com/us-en/hci/docs/concept_hci_product_overview.html) simplifies the management and scale of the datacenter by automating routine tasks and enabling infrastructure administrators to focus on more important functions. Trident can provision and manage storage devices for containerized applications directly against the underlying NetApp HCI storage platform.

**NetApp ONTAP** — [NetApp ONTAP](https://docs.netapp.com/us-en/ontap/index.html) is the NetApp multiprotocol, unified storage operating system that provides advanced data management capabilities for any application. ONTAP systems have all-flash, hybrid, or all-HDD configurations and offer many different deployment models: on-premises FAS, AFA, and ASA clusters, ONTAP Select, and Cloud Volumes ONTAP. Trident supports these ONTAP deployment models.
