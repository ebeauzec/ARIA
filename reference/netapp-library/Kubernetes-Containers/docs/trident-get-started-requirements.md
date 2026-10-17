# Requirements
Source: https://docs.netapp.com/us-en/trident/trident-get-started/requirements.html
Fetched: 2026-07-07

Before installing Trident you should review these general system requirements. Specific backends might have additional requirements.

## Critical information about Trident

**You must read the following critical information about Trident.**

- Kubernetes 1.35 is now supported in Trident. Upgrade Trident prior to upgrading Kubernetes.
- Trident strictly enforces the use of multipathing configuration in SAN environments, with a recommended value of `find_multipaths: no` in multipath.conf file. Use of non-multipathing configuration or use of `find_multipaths: yes` or `find_multipaths: smart` value in multipath.conf file will result in mount failures. Trident has recommended the use of `find_multipaths: no` since the 21.07 release.

## Supported frontends (orchestrators)

Trident supports multiple container engines and orchestrators, including the following:
- Anthos On-Prem (VMware) and Anthos on bare metal 1.16
- Kubernetes 1.27 - 1.35
- OpenShift 4.12, 4.14 - 4.21 (If you plan to use iSCSI node preparation with OpenShift 4.19, the minimum Trident version supported is 25.06.1.)
  - Note: Trident continues to support older OpenShift versions in alignment with the Red Hat Extended Update Support (EUS) release lifecycle, even if they rely on Kubernetes versions that are no longer officially supported upstream. While installing Trident in such cases, you can safely ignore any warning messages about the Kubernetes version.
- Rancher Kubernetes Engine 2 (RKE2) v1.28.x - 1.35.x

Trident also works with a host of other fully-managed and self-managed Kubernetes offerings, including Google Kubernetes Engine (GKE), Amazon Elastic Kubernetes Services (EKS), Azure Kubernetes Service (AKS), Mirantis Kubernetes Engine (MKE), and VMWare Tanzu Portfolio.

Trident and ONTAP can be used as a storage provider for [KubeVirt](https://kubevirt.io/).

> Warning: Before upgrading a Kubernetes cluster from 1.25 to 1.26 or later that has Trident installed, refer to [Upgrade a Helm installation](https://docs.netapp.com/us-en/trident/trident-managing-k8s/upgrade-operator.html#upgrade-a-helm-installation).

## Supported backends (storage)

To use Trident, you need one or more of the following supported backends:
- Amazon FSx for NetApp ONTAP
- Azure NetApp Files
- Cloud Volumes ONTAP
- Google Cloud NetApp Volumes
- NetApp All SAN Array (ASA)
- On-premises FAS, AFF, or ASA r2 (iSCSI, NVMe/TCP, and FC) running ONTAP versions under NetApp full or limited support. See Software Version Support.
- NetApp HCI/Element software 11 or above

## Trident support for KubeVirt and OpenShift Virtualization

Storage drivers supported — Trident supports the following ONTAP drivers for KubeVirt and OpenShift Virtualization:
- ontap-nas
- ontap-san (iSCSI, FCP, NVMe over TCP)
- ontap-san-economy (iSCSI Only)

Points to consider:
- Update storage class to have the `fsType` parameter (for example: `fsType: "ext4"`) in OpenShift Virtualization environment. If needed, set the volume mode to block explicitly using the `volumeMode=Block` parameter in the `dataVolumeTemplates` to notify CDI to create Block data volumes.
- *RWX access mode for block-storage drivers*: ontap-san (iSCSI, NVMe/TCP, FC) and ontap-san-economy (iSCSI) drivers are supported only with "volumeMode: Block" (raw device). For these drivers, the `fstype` parameter cannot be used because the volumes are provided in raw device mode.
- For live-migration workflow/s where RWX access mode is required, these combinations are supported:
  - NFS + `volumeMode=Filesystem`
  - iSCSI + `volumeMode=Block` (raw device)
  - NVMe/TCP + `volumeMode=Block` (raw device)
  - FC + `volumeMode=Block` (raw device)

## Feature requirements

The table below summarizes the features available with this release of Trident and the versions of Kubernetes it supports.

| Feature | Kubernetes version | Feature gates required? |
| --- | --- | --- |
| Trident | 1.27 - 1.35 | No |
| Volume Snapshots | 1.27 - 1.35 | No |
| PVC from Volume Snapshots | 1.27 - 1.35 | No |
| iSCSI PV resize | 1.27 - 1.35 | No |
| ONTAP Bidirectional CHAP | 1.27 - 1.35 | No |
| Dynamic Export Policies | 1.27 - 1.35 | No |
| Trident Operator | 1.27 - 1.35 | No |
| CSI Topology | 1.27 - 1.35 | No |

## Tested host operating systems

Though Trident does not officially support specific operating systems, the following are known to work:
- Red Hat Enterprise Linux CoreOS (RHCOS) versions supported by OpenShift Container Platform on AMD64 and ARM64
- Red Hat Enterprise Linux (RHEL) 8 or later on AMD64 and ARM64 (Note: NVMe/TCP requires RHEL 9 or later.)
- Ubuntu 22.04 LTS or later on AMD64 and ARM64
- Windows Server 2022
- SUSE Linux Enterprise Server (SLES) 15 or later

By default, Trident runs in a container and will, therefore, run on any Linux worker. However, those workers need to be able to mount the volumes that Trident provides using the standard NFS client or iSCSI initiator, depending on the backends you are using.

The `tridentctl` utility also runs on any of these distributions of Linux.

## Host configuration

All worker nodes in the Kubernetes cluster must be able to mount the volumes you have provisioned for your pods. To prepare the worker nodes, you must install NFS, iSCSI, or NVMe tools based on your driver selection. See [Prepare the worker node](https://docs.netapp.com/us-en/trident/trident-use/worker-node-prep.html).

## Storage system configuration

Trident might require changes to a storage system before a backend configuration can use it. See [Configure backends](https://docs.netapp.com/us-en/trident/trident-use/backends.html).

## Trident ports

Trident requires access to specific ports for communication. See [Trident ports](https://docs.netapp.com/us-en/trident/trident-reference/ports.html).

## Container images and corresponding Kubernetes versions

For air-gapped installations, the following list is a reference of container images needed to install Trident. Use the `tridentctl images` command to verify the list of needed container images.

### Container images required for Trident 26.02

| Kubernetes versions | Container image |
| --- | --- |
| v1.27.0, v1.28.0, v1.29.0, v1.30.0, v1.31.0, v1.32.0, v1.33.0, v1.34.0, v1.35.0 | docker.io/netapp/trident:26.02.0<br>docker.io/netapp/trident-autosupport:26.02<br>registry.k8s.io/sig-storage/csi-provisioner:v6.1.0<br>registry.k8s.io/sig-storage/csi-attacher:v4.10.0<br>registry.k8s.io/sig-storage/csi-resizer:v2.0.0<br>registry.k8s.io/sig-storage/csi-snapshotter:v8.5.0<br>registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0<br>docker.io/netapp/trident-operator:26.02.0 (optional) |
