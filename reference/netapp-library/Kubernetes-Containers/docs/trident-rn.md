# What's new (Trident Release Notes)
Source: https://docs.netapp.com/us-en/trident/trident-rn.html
Fetched: 2026-07-07

Release Notes provide information about new features, enhancements, and bug fixes in the latest version of NetApp Trident.

> Warning: The `tridentctl` binary for Linux that is provided in the installer zip file is the tested and supported version. Be aware that the `macos` binary provided in the `/extras` part of the zip file is not tested or supported.

## What's new in 26.02.1

Learn what's new in NetApp Trident and Trident Protect, including enhancements, fixes, and deprecations.

### Trident

#### Fixes
- **Kubernetes**:
  - Fixed Google Cloud NetApp Volumes (GCNV) SAN behavior to support Flex Unified ZONAL pools for block (iSCSI) workloads. Both zonal and regional configurations are now supported.
  - Fixed Google Cloud NetApp Volumes (GCNV) NAS UNIFIED pool handling by improving volume creation, validation, naming, and fallback volume lookup operations when `InternalID` is absent.
  - Fixed an issue where iSCSI device resize operations could fail when available paths and portals did not match.
  - Fixed an intermittent issue where `blkid` incorrectly identified the filesystem type for LUKS devices, preventing new volume creation.
  - Fixed an issue where LUKS publish and stage operations at scale could block the Trident controller. Users are now expected to track LUKS passphrases associated with volumes.
  - Fixed an issue where iSCSI multipath partitions could appear as ghost devices, preventing CSI `NodeUnstage` operations from succeeding.
  - Fixed an NVMe/TCP namespace race condition during concurrent volume creation (Issue #1089).
  - Fixed concurrent clone snapshot operations when snapshots were executed within the same second.
  - Fixed an issue preventing KubeVirt VMs using `dataVolumes` from failing over with Trident Automated Workload Failover.
  - Fixed an error that occurred when deleting an invalid `TridentMirrorRelationship` custom resource while using the Trident concurrent core.
  - Fixed indentation in the `tridentactionmirrorupdates` Kubernetes CRD YAML definition (Issue #1120).
  - Fixed the REST qtree asynchronous delete API call (Issue #1121).
  - Fixed `ControllerPublish` to use the volume configuration filesystem type instead of an incorrect default filesystem type.
  - Fixed controller startup logging to correctly report concurrent driver status.
  - Fixed handling of suspended backends in concurrent Trident.
  - Enhanced AWS ARN handling to support special regions.

### Trident Protect

#### Fixes
Updated Trident Protect dependencies to resolve security vulnerabilities:
- gRPC-Go: CVE-2026-33186
- Go x/crypto SSH: CVE-2024-45337
- OpenTelemetry-Go: CVE-2026-24051
- Go runtime: CVE-2025-22871
- Additional dependencies: CVE-2025-23109

## What's new in 26.02

Learn what's new in NetApp Trident and Trident Protect, including enhancements, fixes, and deprecations.

### Trident

#### Enhancements
- **Kubernetes**:
  - Added general availability (GA) support for concurrency for ONTAP-NAS (NFS only), ONTAP-SAN (iSCSI, FCP, NVMe), and Google Cloud NetApp Volumes (GCNV) drivers, graduating this functionality from Tech Preview. See [Controller scalability](https://docs.netapp.com/us-en/trident/trident-use/controller-scalability.html).
  - Added support for volume autogrow in Trident based on custom, user-defined Trident AutoGrow policies. See [Automatic volume expansion](https://docs.netapp.com/us-en/trident/trident-use/automatic-volume-expansion.html).
  - Enhanced Trident node concurrency to improve the scalability of node operations for NVMe volumes. See [NVMe volumes](https://docs.netapp.com/us-en/trident/trident-use/trident-nvme-rwx-subsystem-limits.html).
  - Added support for GCNV NAS volume auto-tiering through PVC annotations (`tieringPolicy`, `tieringMinimumCoolingDays`), including pool selection and clone inheritance. See [Configure auto-tiering for Google Cloud NetApp Volumes](https://docs.netapp.com/us-en/trident/trident-use/gcnv-auto-tiering.html).
  - Added support for GCNV SAN block (iSCSI) volumes using the `google-cloud-netapp-volumes-san` driver, including provisioning, per-node host group mapping for LUN access, and clone-from-volume operations. See [Google Cloud NetApp Volumes block configuration](https://docs.netapp.com/us-en/trident/trident-use/gcnv-block.html).
  - Added support for automatic backend configuration for Amazon FSx for NetApp ONTAP. When you create a StorageClass that includes the required parameters, Trident automatically creates the corresponding backend and VolumeSnapshotClass, if needed. See [Amazon FSx for NetApp ONTAP backend configuration](https://docs.netapp.com/us-en/trident/trident-use/trident-fsx-auto-backend-configuration.html#add-additional-fsxn-file-systems).
  - Added support for different Microsoft Azure clouds, such as Azure Government and Azure China, and custom cloud configuration for Azure NetApp Files backends. See [Azure NetApp Files backend configuration](https://docs.netapp.com/us-en/trident/trident-use/anf.html).
  - Added support for Kubernetes 1.35. See [Requirements](https://docs.netapp.com/us-en/trident/trident-get-started/requirements.html).

#### Experimental Enhancements
> Note: Not for use in production environments.
- **[Tech Preview]**: Added support for concurrency for ONTAP-NAS-Economy and ONTAP-SAN-Economy drivers.

#### Known issues
> Warning: There is a known issue with the `csi-snapshotter` sidecar. In all Kubernetes versions, VolumeGroupSnapshots `v1beta1` prevents VolumeSnapshots from reaching the `ReadyToUse` state.

Two workarounds are available:
1. Delete the VolumeGroupSnapshots CRDs to disable VolumeGroupSnapshots, and then reinstall Trident.
2. Install VolumeGroupSnapshots `v1beta2` and `snapshot-controller` version 8.4.0 or later, and then reinstall Trident. VolumeGroupSnapshots do not function on Kubernetes versions earlier than v1.34.

#### Fixes
- **Kubernetes**:
  - Fixed an issue where unpublishing a read-only clone removed export policy rules from the source volume in ONTAP-NAS, ONTAP-NAS-Economy, and Google Cloud NetApp Volumes drivers (Issue #1086).
  - Switched kubectl images to lightweight Alpine-based variants to prevent pull failures following Bitnami's public image deprecation (Issue #1080).
  - Fixed preserving annotation of existing deployment during Trident upgrade (Issue #1004).
  - Allow clone across different storage classes if both storage classes are pointing to the same backend (Issue #1104).
  - Fixed node prep failures caused by timeouts in cloud environments with network latencies. Increased timeout values for cloud-based installations.
  - Fixed an issue in LUN creation that caused the filesystem type attribute to remain unset when the process entered a retry state.
  - Fixed REST API volume lookup to ignore volume state, preventing false negatives during volume queries.
  - Improved Trident controller efficiency for ontap-nas-economy driver when used at scale.
  - Set internalID during LUN import in ontap-san-economy driver.
  - Increased Azure Resource Graph query limits to handle more subnets.
  - Improved CSI and ONTAP clone split timeouts to avoid race conditions with some backup applications (Issue #1098, Issue #1100).
  - Fixed suppression of LUKS error messages (Issue #1069).
  - Fixed handling of stale LUKS mappers for both iSCSI and NVMe protocols. Enhanced cleanup logic prevents mount failures from orphaned device mappers.
- Fixed scale limitations for RWX NVMe volumes.
- Updated the OpenTelemetry-Go package to fix CVE-2026-24051.

### Trident Protect

#### Enhancements
- Trident Protect now automatically disables protection schedules and cancels in-progress operations before an in-place restore, and re-enables them after the restore completes. See [Restore applications using Trident Protect](https://docs.netapp.com/us-en/trident/trident-protect/trident-protect-restore-apps.html).
- Added the `runImmediately` field to the schedule CR and `--run-immediately` CLI flag to trigger an immediate backup or snapshot upon schedule creation. See [Create a data protection schedule](https://docs.netapp.com/us-en/trident/trident-protect/trident-protect-protect-apps.html#create-a-data-protection-schedule).
- Added support for specifying a custom name for the restored application using the `destinationApplicationName` field in the restore CR or the `--destination-app-name` CLI flag. See [Restore applications using Trident Protect](https://docs.netapp.com/us-en/trident/trident-protect/trident-protect-restore-apps.html).

#### Fixes
- Fixed restore failures caused by pods being created before their required service accounts were available.
- Fixed `Roles` and `RoleBindings` being skipped during application restores.
- Fixed the originating cluster name not being displayed in `tridentctl-protect get appvaultcontent` output despite being correctly configured.
- Fixed Kopia restore errors that were ignored due to missing `pipefail` handling.
- Fixed snapshot and backup failures caused by resource filters that excluded persistent volumes.
- Fixed incorrect PVC restoration in multi-namespace applications with identically named PVCs across namespaces, which could result in data loss.

## What's new in 25.10

### Trident

#### Enhancements
- **Kubernetes**:
  - Added support for CSI Volume Group Snapshots with v1beta1 Volume Group Snapshot Kubernetes APIs for ONTAP-NAS NFS and ONTAP-SAN-Economy drivers, in addition to ONTAP-SAN (iSCSI and FC). See [Work with volume group snapshots](https://docs.netapp.com/us-en/trident/trident-use/vol-group-snapshots.html).
  - Added support for automated workload failover with force volume detach for the ONTAP-NAS and ONTAP-NAS-Economy (excluding SMB in both the NAS drivers), and the ONTAP-SAN and ONTAP-SAN-Economy drivers. See [Automating the failover of stateful applications with Trident](https://docs.netapp.com/us-en/trident/trident-reco/force-detach.html).
  - Enhanced Trident node concurrency for higher scalability on node operations for FCP volumes.
  - Added ONTAP AFX support for the ONTAP NAS driver. See [ONTAP NAS configuration options and examples](https://docs.netapp.com/us-en/trident/trident-use/ontap-nas-examples.html).
  - Added support for configuring CPU and memory resource requests and limits for Trident containers via TridentOrchestrator CR and Helm chart values (Issues #1000, #927, #853, #592, #110).
  - Added FC support for ASAr2 personality. See [ONTAP SAN configuration options and examples](https://docs.netapp.com/us-en/trident/trident-use/ontap-san-examples.html).
  - Added an option to serve Prometheus metrics with HTTPS, instead of HTTP. See [Monitor Trident](https://docs.netapp.com/us-en/trident/trident-use/monitor-trident.html).
  - Added an option `--no-rename` when importing a volume to retain the original name but let Trident manage the volume's lifecycle. See [Import volumes](https://docs.netapp.com/us-en/trident/trident-use/vol-import.html).
  - Trident deployment now runs at the system-cluster-critical priority class.
- Added an option for Trident controller to use host networking via helm, operator, and tridentctl (Issue #858).
- Added manual QoS support to the ANF driver, making it production-ready in Trident 25.10; this experimental enhancement was introduced in Trident 25.06.

#### Experimental Enhancements
> Note: Not for use in production environments.
- **[Tech preview]**: Added support for concurrency for ONTAP-NAS (NFS only) and ONTAP-SAN (NVMe for unified ONTAP 9), in addition to the existing Tech preview for the ONTAP-SAN driver (iSCSI and FCP protocols in unified ONTAP 9).

#### Fixes
- **Kubernetes**:
  - Fixed the CSI node-driver-registrar container name inconsistency by standardizing Linux DaemonSet to node-driver-registrar to match Windows DaemonSet and container image naming.
  - Fixed an issue where export policies for legacy qtrees were not properly upgraded.
- **OpenShift**:
  - Fixed Trident node pod not starting on Windows nodes in OpenShift due to SCC having allowHostDirVolumePlugin set to false (Issue #950).
- Fixed Kubernetes API QPS not being set via Helm (Issue #975).
- Fixed inability to mount a Persistent Volume Claim (PVC) based on a snapshot of an NVMe based XFS filesystem PVC on the same Kubernetes node.
- Fixed UUID change issue after host/Docker restart in NDVP mode by adding unique/shared subsystem names per backend (e.g., netappdvp_subsystem).
- Fixed mount errors for iSCSI volumes during Trident upgrade from versions prior to 23.10 to 24.10 and above, resolving "invalid SANType" issue.
- Fixed issue where Trident backend state was not transitioning to online/offline without restarting the Trident controller.
- Fixed intermittent race condition causing slow PVC resize.
- Fixed snapshots not being cleaned up on volume clone failures.
- Fixed failure to unstage volume when its device path was changed by the kernel.
- Fixed failure to unstage volume due to LUKS device already closed.
- Fixed issue where slow storage operations were leading to ContextDeadline errors.
- Trident Operator will wait for configurable k8s-timeout to check Trident version.

### Trident Protect

NetApp Trident Protect provides advanced application data management capabilities that enhance the functionality and availability of stateful Kubernetes applications backed by NetApp ONTAP storage systems and the NetApp Trident CSI storage provisioner.

#### Enhancements
- Added annotations to control snapshot CR timeouts for schedule and backup CRs: `protect.trident.netapp.io/snapshot-completion-timeout`, `protect.trident.netapp.io/volume-snapshots-ready-to-use-timeout`, `protect.trident.netapp.io/volume-snapshots-created-timeout`. See [Supported backup and schedule annotations](https://docs.netapp.com/us-en/trident/trident-protect/trident-protect-protect-apps.html).
- Added an annotation to the schedule CR to configure PVC bind timeout, which will be used by the backup CR: `protect.trident.netapp.io/pvc-bind-timeout-sec`.
- Improved `tridentctl-protect` backup and snapshot listings with a new field to indicate execution hook failures.

## Changes in 25.06.2

### Trident
#### Fixes
- **Kubernetes**: Fixed critical issue where incorrect iSCSI devices were discovered when detaching volumes from Kubernetes nodes.

## Changes in 25.06.1

### Trident
> Important: For customers using SolidFire, do not upgrade to 25.06.1 due to a known issue when unpublishing volumes. 25.06.2 will be released soon to address this issue.

#### Fixes
- **Kubernetes**:
  - Fixed an issue where NQNs were not checked before being unmapped from subsystems.
  - Fixed an issue where multiple attempts to close a LUKS device led to failures in detaching volumes.
  - Fixed iSCSI volume unstage when the device path has changed since its creation.
  - Block cloning of volumes across storage classes.
- **OpenShift**: Fixed an issue where iSCSI node prep failed with OCP 4.19.
- Increased the timeout when cloning a volume using SolidFire backends (Issue #1008).

## Changes in 25.06

### Trident

#### Enhancements
- **Kubernetes**:
  - Added support for CSI Volume Group Snapshots with `v1beta1` Volume Group Snapshot Kubernetes APIs for ONTAP-SAN iSCSI driver. See [Work with volume group snapshots](https://docs.netapp.com/us-en/trident/trident-use/vol-group-snapshots.html). (Note: VolumeGroupSnapshot is a beta feature in Kubernetes with beta APIs. Kubernetes 1.32 is the minimum version required for VolumeGroupSnapshot.)
  - Added support for ONTAP ASA r2 for NVMe/TCP in addition to iSCSI. See [ONTAP SAN configuration options and examples](https://docs.netapp.com/us-en/trident/trident-use/ontap-san-examples.html).
  - Added secure SMB support for ONTAP-NAS and ONTAP-NAS-Economy volumes. Active Directory users and groups may now be used with SMB volumes for enhanced security. See [Enable secure SMB](https://docs.netapp.com/us-en/trident/trident-use/ontap-nas-prep.html#enable-secure-smb).
  - Enhanced Trident node concurrency for higher scalability on node operations for iSCSI volumes.
  - Added `--allow-discards` when opening LUKS volumes to allow discard/TRIM commands for space reclamation.
  - Enhanced performance when formatting LUKS-encrypted volumes.
  - Enhanced LUKS cleanup for failed but partially formatted LUKS devices.
  - Enhanced Trident node idempotency for NVMe volume attach and detach.
  - Added `internalID` field to the Trident volume config for ONTAP-SAN-Economy driver.
  - Added support for volume replication with SnapMirror for NVMe backends. See [Replicate volumes using SnapMirror](https://docs.netapp.com/us-en/trident/trident-use/vol-volume-replicate.html).

#### Experimental Enhancements
> Note: Not for use in production environments.
- [Tech Preview] Enabled concurrent Trident controller operations via the `--enable-concurrency` feature flag. This allows controller operations to run in parallel, improving performance for busy or large environments. (Note: This feature is experimental and currently supports limited parallel workflows with the ONTAP-SAN driver — iSCSI and FCP protocols.)
- [Tech Preview] Added manual QOS support with the ANF driver.

#### Fixes
- **Kubernetes**:
  - Fixed an issue with CSI NodeExpandVolume where multipath devices could be left with incongruent sizes when underlying SCSI disk(s) are unavailable.
  - Fixed failure to clean up duplicate export policies for ONTAP-NAS and ONTAP-NAS-Economy drivers.
  - Fixed GCNV volumes defaulting to NFSv3 when `nfsMountOptions` is unset; now both NFSv3 and NFSv4 protocols are supported. If `nfsMountOptions` is not provided, the host's default NFS version (NFSv3 or NFSv4) is used.
  - Fixed deployment issue when installing Trident using Kustomize (Issue #831).
  - Fixed missing export policies for PVCs created from snapshots (Issue #1016).
  - Fixed issue where the ANF volume sizes are not automatically aligned to 1 GiB increments.
  - Fixed issue when using NFSv3 with Bottlerocket.
- Fixed issue with ONTAP-NAS-Economy volumes expanding up to 300 TB despite resize failures.
- Fixed issue where clone split operations were being done synchronously when using ONTAP REST API.

#### Deprecations
- **Kubernetes**: Updated minimum supported Kubernetes to v1.27.

### Trident Protect

#### Enhancements
- Improved restore times, providing the option to do more frequent full backups.
- Improved granularity of application definition and selective restore with Group-Version-Kind (GVK) filtering.
- Efficient resync and reverse replication when using AppMirrorRelationship (AMR) with NetApp SnapMirror, to avoid full PVC replication.
- Added ability to use EKS Pod Identity to create AppVault buckets, removing the need to specify a secret with the bucket credentials for EKS clusters.
- Added the ability to skip restoring labels and annotations in the restore namespace, if needed.
- AppMirrorRelationship (AMR) will now check for source PVC expansion and perform the appropriate expansion on the destination PVC as needed.

#### Fixes
- Fixed bug where snapshot annotation values from previous snapshots were being applied to newer snapshots. All snapshot annotations are applied correctly now.
- Defined a secret for data mover encryption (Kopia / Restic) by default, if not defined.
- Added improved validation and error messages for S3 appvault creation.
- AppMirrorRelationship (AMR) now only replicates PVs in the Bound state, to avoid failed attempts.
- Fixed issue where errors were displayed when getting AppVaultContent on an AppVault with large number of backups.
- KubeVirt VMSnapshots are excluded from restore and failover operations to avoid failures.
- Fixed issue with Kopia where snapshots were being removed prematurely due to Kopia default retention schedule overriding what was set by the user in the schedule.

## Changes in 25.02.1

### Trident
#### Fixes
- **Kubernetes**:
  - Fixed an issue in the trident-operator where sidecar image names and versions were incorrectly populated when using a non-default image registry (Issue #983).
  - Fixed the issue where multipath sessions fail to recover during an ONTAP failover giveback (Issue #961).

## Changes in 25.02

Beginning with Trident 25.02, the What's New summary provides details about enhancements, fixes, and deprecations for both Trident and Trident Protect releases.

### Trident

#### Enhancements
- **Kubernetes**:
  - Added support for ONTAP ASA r2 for iSCSI.
  - Added support for force detach for ONTAP-NAS volumes during Non-Graceful Node Shutdown scenarios. New ONTAP-NAS volumes will now utilize per-volume export policies managed by Trident. Provided an upgrade path for existing volumes to transition to the new export policy model on unpublish without affecting active workloads.
  - Added cloneFromSnapshot annotation.
  - Added support for cross namespace volume cloning.
  - Enhanced iSCSI self-healing scan remediations to initiate rescans by exact host, channel, target and LUN ID.
  - Added support for Kubernetes 1.32.
- **OpenShift**:
  - Added support for automatic iSCSI node preparation for RHCOS on ROSA clusters.
  - Added support for OpenShift Virtualization for ONTAP drivers.
- Added Fibre Channel support on ONTAP-SAN driver.
- Added NVMe LUKS support.
- Switched to scratch image for all base images.
- Added iSCSI connection state discovery and logging when iSCSI sessions should be logged in but are not (Issue #961).
- Added support for SMB volumes with google-cloud-netapp-volumes driver.
- Added support to allow ONTAP volumes to skip recovery queue on deletion.
- Added support to override default images using SHAs instead of tags.
- Added image-pull-secrets flag to tridentctl installer.

#### Fixes
- **Kubernetes**:
  - Fixed missing node IP addresses from automatic export policies (Issue #965).
  - Fixed automatic export policies switching to per volume policy prematurely for ONTAP-NAS-Economy.
  - Fixed backend config credentials to support all available AWS ARN partitions (Issue #913).
  - Added option to disable the auto configurator reconciliation in the Trident operator (Issue #924).
  - Added securityContext for csi-resizer container (Issue #976).

### Trident Protect

NetApp Trident Protect provides advanced application data management capabilities that enhance the functionality and availability of stateful Kubernetes applications backed by NetApp ONTAP storage systems and the NetApp Trident CSI storage provisioner.

#### Enhancements
- Added backup and restore support for KubeVirt / OpenShift Virtualization VMs for both volumeMode: File and volumeMode: Block (raw device) storage. Compatible with all Trident drivers, enhancing existing protection features when replicating storage using NetApp SnapMirror with Trident Protect.
- Added the capability to control freeze behavior at application level for KubeVirt environments.
- Added support for configuring AutoSupport proxy connections.
- Added the ability to define a secret for data mover encryption (Kopia / Restic).
- Added the ability to manually run an execution hook.
- Added the ability to configure security context constraints (SCCs) during Trident Protect installation.
- Added support for configuring nodeSelector during Trident Protect installation.
- Added support for HTTP / HTTPS egress proxy for AppVault objects.
- Extended ResourceFilter to enable exclusion of cluster-scoped resources.
- Added support for the AWS session token in S3 AppVault credentials.
- Added support for resource collection after pre-snapshot execution hooks.

#### Fixes
- Improved the management of temporary volumes to skip the ONTAP volume recovery queue.
- SCC annotations are now restored to original values.
- Improved restore efficiency with support for parallel operations.
- Enhanced support for execution hook timeouts for larger applications.

## Changes in 24.10.1

### Enhancements
- **Kubernetes**: Added support for Kubernetes 1.32.
- Added iSCSI connection state discovery and logging when iSCSI sessions should be logged in but are not (Issue #961).

### Fixes
- Fixed missing node IP addresses from automatic export policies (Issue #965).
- Fixed automatic export policies switching to per volume policy prematurely for ONTAP-NAS-Economy.
- Updated Trident and Trident-ASUP dependencies to address CVE-2024-45337 and CVE-2024-45310.
- Removed logouts for intermittently unhealthy non-CHAP portals during iSCSI self-healing (Issue #961).

## Changes in 24.10

### Enhancements
- Google Cloud NetApp Volumes driver is now generally available for NFS volumes and supports zone-aware provisioning.
- GCP Workload Identity will be used as Cloud Identity for Google Cloud NetApp Volumes with GKE.
- Added `formatOptions` configuration parameter to ONTAP-SAN and ONTAP-SAN-Economy drivers to allow users to specify LUN format options.
- Reduced Azure NetApp Files minimum volume size to 50 GiB.
- Added `denyNewVolumePools` configuration parameter to restrict ONTAP-NAS-Economy and ONTAP-SAN-Economy drivers to preexisting Flexvol pools.
- Added detection for the addition, removal, or renaming of aggregates from the SVM across all ONTAP drivers.
- Added 18 MiB overhead to LUKS LUNs to ensure reported PVC size is usable.
- Improved ONTAP-SAN and ONTAP-SAN-Economy node stage and unstage error handling to allow unstage to remove devices after a failed stage.
- Added a custom role generator allowing customers to create a minimalistic role for Trident in ONTAP.
- Added additional logging for troubleshooting `lsscsi` (Issue #792).

#### Kubernetes
- Added new Trident features for Kubernetes-native workflows: Data protection, Data migration, Disaster recovery, Application mobility. See [Learn about Trident Protect](https://docs.netapp.com/us-en/trident/trident-protect/learn-about-trident-protect.html).
- Added a new flag `--k8s-api-qps` to installers to set the QPS value used by Trident to communicate with the Kubernetes API server.
- Added `--node-prep` flag to installers for automatic management of storage protocol dependencies on Kubernetes cluster nodes. Tested and verified compatibility with Amazon Linux 2023 iSCSI storage protocol.
- Added support for force detach for ONTAP-NAS-Economy volumes during Non-Graceful Node Shutdown scenarios.
- New ONTAP-NAS-Economy NFS volumes will use per-qtree export policies when using `autoExportPolicy` backend option.
- Added support for Kubernetes 1.31.

#### Experimental Enhancements
- Added tech preview for Fibre Channel support on ONTAP-SAN driver.

### Fixes
- **Kubernetes**:
  - Fixed Rancher admission webhook preventing Trident Helm installations (Issue #839).
  - Fixed Affinity key in helm chart values (Issue #898).
  - Fixed tridentControllerPluginNodeSelector/tridentNodePluginNodeSelector won't work with "true" value (Issue #899).
  - Deleted ephemeral snapshots created during cloning (Issue #901).
- Added support for Windows Server 2019.
- Fixed `go mod tidy` in Trident repo (Issue #767).

### Deprecations
- **Kubernetes**: Updated minimum supported Kubernetes to 1.25. Removed support for POD Security Policy.

### Product rebranding
Beginning with the 24.10 release, Astra Trident is rebranded to Trident (NetApp Trident). This rebranding does not affect any features, platforms supported, or interoperability for Trident.

## Changes in 24.06

### Enhancements
- **IMPORTANT**: The `limitVolumeSize` parameter now limits qtree/LUN sizes in the ONTAP economy drivers. Use the new `limitVolumePoolSize` parameter to control Flexvol sizes in those drivers (Issue #341).
- Added ability for iSCSI self-healing to initiate SCSI scans by exact LUN ID if deprecated igroups are in use (Issue #883).
- Added support for volume clone and resize operations to be allowed even when the backend is in suspended mode.
- Added ability for user-configured log settings for the Trident controller to be propagated to Trident node pods.
- Added support in Trident to use REST by default instead of ONTAPI (ZAPI) for ONTAP versions 9.15.1 and later.
- Added support for custom volume names and metadata on the ONTAP storage backends for new persistent volumes.
- Enhanced the `azure-netapp-files` (ANF) driver to automatically enable the snapshot directory by default when the NFS mount options are set to use NFS version 4.x.
- Added Bottlerocket support for NFS volumes.
- Added technical preview support for Google Cloud NetApp Volumes.

#### Kubernetes
- Added support for Kubernetes 1.30.
- Added ability for Trident DaemonSet to clean zombie mounts and residual tracking files at startup (Issue #883).
- Added PVC annotation `trident.netapp.io/luksEncryption` for dynamically importing LUKS volumes (Issue #849).
- Added topology awareness to ANF driver.
- Added support for Windows Server 2022 nodes.

### Fixes
- Fixed Trident installation failures due to stale transactions.
- Fixed tridentctl to ignore warning messages from Kubernetes (Issue #892).
- Changed Trident controller `SecurityContextConstraint` priority to `0` (Issue #887).
- ONTAP drivers now accept volume sizes below 20 MiB (Issue #885).
- Fixed Trident to prevent shrinking of FlexVol volumes during resize operation for the ONTAP-SAN driver.
- Fixed ANF volume import failure with NFS v4.1.

## Changes in 24.02

### Enhancements
- Added support for Cloud Identity: AKS with ANF uses Azure Workload Identity; EKS with FSxN uses AWS IAM role.
- Added support to install Trident as an add-on on EKS cluster from EKS console.
- Added ability to configure and disable iSCSI self-healing (Issue #864).
- Added Amazon FSx personality to ONTAP drivers to enable integration with AWS IAM and SecretsManager, and to enable Trident to delete FSx volumes with backups (Issue #453).

#### Kubernetes
- Added support for Kubernetes 1.29.

### Fixes
- Fixed ACP warning messages, when ACP is not enabled (Issue #866).
- Added a 10-second delay before performing a clone split during snapshot delete for ONTAP drivers, when a clone is associated with the snapshot.

### Deprecations
- Removed in-toto attestations framework from multi-platform image manifests.

## Changes in 23.10

### Fixes
- Fixed volume expansion if a new requested size is smaller than the total volume size for ontap-nas and ontap-nas-flexgroup storage drivers (Issue #834).
- Fixed volume size to display only usable size of the volume during import for ontap-nas and ontap-nas-flexgroup storage drivers (Issue #722).
- Fixed FlexVol name conversion for ONTAP-NAS-Economy.
- Fixed Trident initialization issue on a windows node when node is rebooted.

### Enhancements
#### Kubernetes
Added support for Kubernetes 1.28.

#### Trident
- Added support for using Azure Managed Identities (AMI) with azure-netapp-files storage driver.
- Added support for NVMe over TCP for the ONTAP-SAN driver.
- Added ability to pause the provisioning of a volume when backend is set to suspended state by user (Issue #558).

## Changes in 23.07.1
**Kubernetes:** Fixed daemonset deletion to support zero-downtime upgrades (Issue #740).

## Changes in 23.07

### Fixes
#### Kubernetes
- Fixed Trident upgrade to disregard old pods stuck in terminating state (Issue #740).
- Added toleration to "transient-trident-version-pod" definition (Issue #795).

#### Trident
- Fixed ONTAPI (ZAPI) requests to ensure LUN serial numbers are queried when getting LUN attributes to identify and fix ghost iSCSI devices during Node Staging operations.
- Fixed error handling in storage driver code (Issue #816).
- Fixed quota resize when using ONTAP drivers with use-rest=true.
- Fixed LUN clone creation in ontap-san-economy.
- Revert publish info field from `rawDevicePath` to `devicePath`; added logic to populate and recover (in some cases) `devicePath` field.

### Enhancements
#### Kubernetes
- Added support for importing pre-provisioned snapshots.
- Minimized deployment and daemonset linux permissions (Issue #817).

#### Trident
- No longer reporting the state field for "online" volumes and snapshots.
- Updates the backend state if the ONTAP backend is offline (Issues #801, #543).
- LUN Serial Number is always retrieved and published during the ControllerVolumePublish workflow.
- Added additional logic to verify iSCSI multipath device serial number and size.
- Additional verification for iSCSI volumes to ensure correct multipath device is unstaged.

#### Experimental Enhancement
Added tech preview support for NVMe over TCP for the ONTAP-SAN driver.

### Deprecations
#### Kubernetes
- Removed support for v1beta1 snapshots.
- Removed support for pre-CSI volumes and storage classes.
- Updated minimum supported Kubernetes to 1.22.

## Changes in 23.04

> Important: Force volume detach for ONTAP-SAN-* volumes is supported only with Kubernetes versions with the Non-Graceful Node Shutdown feature gate enabled. Force detach must be enabled at install time using the `--enable-force-detach` Trident installer flag.

### Fixes
- Fixed Trident Operator to use IPv6 localhost for installation when specified in spec.
- Fixed Trident Operator cluster role permissions to be in sync with the bundle permissions (Issue #799).
- Fixed issue with attaching raw block volume on multiple nodes in RWX mode.
- Fixed FlexGroup cloning support and volume import for SMB volumes.
- Fixed issue where Trident controller could not shut down immediately (Issue #811).
- Added fix to list all igroup names associated with a specified LUN provisioned with ontap-san-* drivers.
- Added a fix to allow external processes to run to completion.
- Fixed compilation error for s390 architecture (Issue #537).
- Fixed incorrect logging level during volume mount operations (Issue #781).
- Fixed potential type assertion error (Issue #802).

### Enhancements
- Kubernetes:
  - Added support for Kubernetes 1.27.
  - Added support for importing LUKS volumes.
  - Added support for ReadWriteOncePod PVC access mode.
  - Added support for force detach for ONTAP-SAN-* volumes during Non-Graceful Node Shutdown scenarios.
  - All ONTAP-SAN-* volumes will now use per-node igroups. LUNs will only be mapped to igroups while actively published to those nodes to improve security posture (Issue #758).
  - Improved Trident security by cleaning up unused Trident-managed igroups from ONTAP-SAN-* backends.
- Added support for SMB volumes with Amazon FSx to the ontap-nas-economy and ontap-nas-flexgroup storage drivers.
- Added support for SMB shares with the ontap-nas, ontap-nas-economy and ontap-nas-flexgroup storage drivers.
- Added support for arm64 nodes (Issue #732).
- Improved Trident shutdown procedure by deactivating API servers first (Issue #811).
- Added cross-platform build support for Windows and arm64 hosts to Makefile.

### Deprecations
**Kubernetes:** Backend-scoped igroups will no longer be created when configuring ontap-san and ontap-san-economy drivers (Issue #758).

## Changes in 23.01.1

### Fixes
- Fixed Trident Operator to use IPv6 localhost for installation when specified in spec.
- Fixed Trident Operator cluster role permissions to be in sync with the bundle permissions (Issue #799).
- Added a fix to allow external processes to run to completion.
- Fixed issue with attaching raw block volume on multiple nodes in RWX mode.
- Fixed FlexGroup cloning support and volume import for SMB volumes.

## Changes in 23.01

> Important: Kubernetes 1.27 is now supported in Trident. Please upgrade Trident prior to upgrading Kubernetes.

### Fixes
- Kubernetes: Added options to exclude Pod Security Policy creation to fix Trident installations via Helm (Issues #783, #794).

### Enhancements
Kubernetes:
- Added support for Kubernetes 1.26.
- Improved overall Trident RBAC resource utilization (Issue #757).
- Added automation to detect and fix broken or stale iSCSI sessions on host nodes.
- Added support for expanding LUKS encrypted volumes.
- Added credential rotation support for LUKS encrypted volumes.

Trident:
- Added support for SMB volumes with Amazon FSx for NetApp ONTAP to the ontap-nas storage driver.
- Added support for NTFS permissions when using SMB volumes.
- Added support for storage pools for GCP volumes with CVS service level.
- Added support for optional use of flexgroupAggregateList when creating FlexGroups with the ontap-nas-flexgroup storage driver.
- Improved performance for the ontap-nas-economy storage driver when managing multiple FlexVol volumes.
- Enabled dataLIF updates for all ONTAP NAS storage drivers.
- Updated the Trident Deployment and DaemonSet naming convention to reflect the host node OS.

### Deprecations
- Kubernetes: Updated minimum supported Kubernetes to 1.21.
- DataLIFs should no longer be specified when configuring `ontap-san` or `ontap-san-economy` drivers.

## Changes in 22.10

> Warning: Critical information about Trident 22.10 — Kubernetes 1.25 is now supported in Trident. You must upgrade Trident to 22.10 prior to upgrading to Kubernetes 1.25. Trident now strictly enforces the use of multipathing configuration in SAN environments, with a recommended value of `find_multipaths: no` in multipath.conf file. Use of non-multipathing configuration or use of `find_multipaths: yes` or `find_multipaths: smart` value in multipath.conf file will result in mount failures.

### Fixes
- Fixed issue specific to ONTAP backend created using `credentials` field failing to come online during 22.07.0 upgrade (Issue #759).
- **Docker:** Fixed an issue causing the Docker volume plugin to fail to start in some environments (Issue #548, Issue #760).
- Fixed SLM issue specific to ONTAP SAN backends to ensure only subset of dataLIFs belonging to reporting nodes are published.
- Fixed performance issue where unnecessary scans for iSCSI LUNs happened when attaching a volume.
- Removed granular retries within the Trident iSCSI workflow to fail fast and reduce external retry intervals.
- Fixed issue where an error was returned when flushing an iSCSI device when the corresponding multipath device was already flushed.

### Enhancements
- Kubernetes:
  - Added support for Kubernetes 1.25.
  - Added a separate ServiceAccount, ClusterRole, and ClusterRoleBinding for the Trident Deployment and DaemonSet.
  - Added support for cross-namespace volume sharing.
- All Trident `ontap-*` storage drivers now work with the ONTAP REST API.
- Added new operator yaml (`bundle_post_1_25.yaml`) without a `PodSecurityPolicy` to support Kubernetes 1.25.
- Added support for LUKS-encrypted volumes for `ontap-san` and `ontap-san-economy` storage drivers.
- Added support for Windows Server 2019 nodes.
- Added support for SMB volumes on Windows nodes through the `azure-netapp-files` storage driver.
- Automatic MetroCluster switchover detection for ONTAP drivers is now generally available.

### Deprecations
- **Kubernetes:** Updated minimum supported Kubernetes to 1.20.
- Removed Astra Data Store (ADS) driver.
- Removed support for `yes` and `smart` options for `find_multipaths` when configuring worker node multipathing for iSCSI.

## Changes in 22.07

### Fixes
**Kubernetes**
- Fixed issue to handle boolean and number values for node selector when configuring Trident with Helm or the Trident Operator (Issue #700).
- Fixed issue in handling errors from non-CHAP path, so that kubelet will retry if it fails (Issue #736).

### Enhancements
- Transition from k8s.gcr.io to registry.k8s.io as default registry for CSI images.
- ONTAP-SAN volumes will now use per-node igroups and only map LUNs to igroups while actively published to those nodes to improve security posture.
- Included a ResourceQuota with Trident installations to ensure Trident DaemonSet is scheduled when PriorityClass consumption is limited by default.
- Added support for Network Features to Azure NetApp Files driver (Issue #717).
- Added tech preview automatic MetroCluster switchover detection to ONTAP drivers (Issue #228).

### Deprecations
- **Kubernetes:** Updated minimum supported Kubernetes to 1.19.
- Backend config no longer allows multiple authentication types in single config.

### Removals
- AWS CVS driver (deprecated since 22.04) has been removed.
- Kubernetes: Removed unnecessary SYS_ADMIN capability from node pods. Reduced nodeprep down to simple host info and active service discovery.

### Documentation
A new Pod Security Standards (PSS) section has been added detailing permissions enabled by Trident on installation.

## Changes in 22.04

> Important: If you are upgrading from any previous Trident release and use Azure NetApp Files, the `location` config parameter is now a mandatory, singleton field.

### Fixes
- Improved parsing of iSCSI initiator names (Issue #681).
- Fixed issue where CSI storage class parameters weren't allowed (Issue #598).
- Fixed duplicate key declaration in Trident CRD (Issue #671).
- Fixed inaccurate CSI Snapshot logs (Issue #629).
- Fixed issue with unpublishing volumes on deleted nodes (Issue #691).
- Added handling of filesystem inconsistencies on block devices (Issue #656).
- Fixed issue pulling auto-support images when setting the `imageRegistry` flag during installation (Issue #715).
- Fixed issue where Azure NetApp Files driver failed to clone a volume with multiple export rules.

### Enhancements
- Inbound connections to Trident's secure endpoints now require a minimum of TLS 1.3 (Issue #698).
- Trident now adds HSTS headers to responses from its secure endpoints.
- Trident now attempts to enable the Azure NetApp Files unix permissions feature automatically.
- **Kubernetes**: Trident daemonset now runs at system-node-critical priority class (Issue #694).

### Removals
E-Series driver (disabled since 20.07) has been removed.

## Changes in 22.01.1

### Fixes
- Fixed issue with unpublishing volumes on deleted nodes (Issue #691).
- Fixed panic when accessing nil fields for aggregate space in ONTAP API responses.

## Changes in 22.01.0

### Fixes
- **Kubernetes:** Increase node registration backoff retry time for large clusters.
- Fixed issue where azure-netapp-files driver could be confused by multiple resources with the same name.
- ONTAP SAN IPv6 DataLIFs now work if specified with brackets.
- Fixed issue where attempting to import an already imported volume returns EOF leaving PVC in pending state (Issue #489).
- Fixed issue when Trident performance slows down when > 32 snapshots are created on a SolidFire volume.
- Replaced SHA-1 with SHA-256 in SSL certificate creation.
- Fixed Azure NetApp Files driver to allow duplicate resource names and limit operations to a single location.

### Enhancements
- Kubernetes: Added support for Kubernetes 1.23. Added scheduling options for Trident pods when installed via Trident Operator or Helm (Issue #651).
- Allow cross-region volumes in GCP driver (Issue #633).
- Added support for 'unixPermissions' option to Azure NetApp Files volumes (Issue #666).

### Deprecations
Trident REST interface can listen and serve only at 127.0.0.1 or [::1] addresses.

## Changes in 21.10.1

> Warning: The v21.10.0 release has an issue that can put the Trident controller into a CrashLoopBackOff state when a node is removed and then added back to the Kubernetes cluster. This issue is fixed in v21.10.1 (GitHub issue 669).

### Fixes
- Fixed potential race condition when importing a volume on a GCP CVS backend resulting in failure to import.
- Fixed an issue that can put the Trident controller into a CrashLoopBackOff state when a node is removed and then added back to the Kubernetes cluster (GitHub issue 669).
- Fixed issue where SVMs were no longer discovered if no SVM name was specified (GitHub issue 612).

## Changes in 21.10.0

### Fixes
- Fixed issue where clones of XFS volumes could not be mounted on the same node as the source volume (GitHub issue 514).
- Fixed issue where Trident logged a fatal error on shutdown (GitHub issue 597).
- Kubernetes-related fixes:
  - Return a volume's used space as the minimum restoreSize when creating snapshots with `ontap-nas` and `ontap-nas-flexgroup` drivers (GitHub issue 645).
  - Fixed issue where `Failed to expand filesystem` error was logged after volume resize (GitHub issue 560).
  - Fixed issue where a pod could get stuck in `Terminating` state (GitHub issue 572).
  - Fixed the case where an `ontap-san-economy` FlexVol might be full of snapshot LUNs (GitHub issue 533).
  - Fixed custom YAML installer issue with different image (GitHub issue 613).
  - Fixed snapshot size calculation (GitHub issue 611).
  - Fixed issue where all Trident installers could identify plain Kubernetes as OpenShift (GitHub issue 639).
  - Fixed the Trident operator to stop reconciliation if the Kubernetes API server is unreachable (GitHub issue 599).

### Enhancements
- Added support for `unixPermissions` option to GCP-CVS Performance volumes.
- Added support for scale-optimized CVS volumes in GCP in the range 600 GiB to 1 TiB.
- Kubernetes-related enhancements:
  - Added support for Kubernetes 1.22.
  - Enabled the Trident operator and Helm chart to work with Kubernetes 1.22 (GitHub issue 628).
  - Added operator image to `tridentctl` images command (GitHub issue 570).

### Experimental enhancements
- Added support for volume replication in the `ontap-san` driver.
- Added tech preview REST support for the `ontap-nas-flexgroup`, `ontap-san`, and `ontap-nas-economy` drivers.

## Known issues

Known issues identify problems that might prevent you from using the product successfully.

- When upgrading a Kubernetes cluster from 1.24 to 1.25 or later that has Trident installed, you must update values.yaml to set `excludePodSecurityPolicy` to `true` or add `--set excludePodSecurityPolicy=true` to the `helm upgrade` command before you can upgrade the cluster.
- Trident now enforces a blank `fsType` (`fsType=""`) for volumes that do not have the `fsType` specified in their StorageClass. When working with Kubernetes 1.17 or later, Trident supports providing a blank `fsType` for NFS volumes. For iSCSI volumes, you are required to set the `fsType` on your StorageClass when enforcing an `fsGroup` using a Security Context.
- When using a backend across multiple Trident instances, each backend configuration file should have a different `storagePrefix` value for ONTAP backends or use a different `TenantName` for SolidFire backends. Trident cannot detect volumes that other instances of Trident have created. If `storagePrefix` or `TenantName` do not differ, there might be name collisions for volumes created on the same backend.
- When installing Trident (using `tridentctl` or the Trident Operator) and using `tridentctl` to manage Trident, you should ensure the `KUBECONFIG` environment variable is set.
- To perform online space reclamation for iSCSI PVs, the underlying OS on the worker node might require mount options to be passed to the volume. This is true for RHEL/RHCOS instances, which require the `discard` mount option; ensure that the discard mountOption is included in your StorageClass to support online block discard.
- If you have more than one instance of Trident per Kubernetes cluster, Trident cannot communicate with other instances and cannot discover other volumes that they have created, which leads to unexpected and incorrect behavior. There should be only one instance of Trident per Kubernetes cluster.
- If Trident-based `StorageClass` objects are deleted from Kubernetes while Trident is offline, Trident does not remove the corresponding storage classes from its database when it comes back online. You should delete these storage classes using `tridentctl` or the REST API.
- If a user deletes a PV provisioned by Trident before deleting the corresponding PVC, Trident does not automatically delete the backing volume. You should remove the volume via `tridentctl` or the REST API.
- ONTAP cannot concurrently provision more than one FlexGroup at a time unless the set of aggregates are unique to each provisioning request.
- When using Trident over IPv6, you should specify `managementLIF` and `dataLIF` in the backend definition within square brackets. For example, `[fd20:8b1e:b258:2000:f816:3eff:feec:0]`. (Note: You cannot specify `dataLIF` on an ONTAP SAN backend. Trident discovers all available iSCSI LIFs and uses them to establish the multipath session.)
- If using the `solidfire-san` driver with OpenShift 4.5, ensure that the underlying worker nodes use MD5 as the CHAP authentication algorithm. Secure FIPS-compliant CHAP algorithms SHA1, SHA-256, and SHA3-256 are available with Element 12.7.

## Find more information
- [Trident GitHub](https://github.com/NetApp/trident)
- [Trident blogs](https://netapp.io/persistent-storage-provisioner-for-kubernetes/)
