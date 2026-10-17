# NetApp Reference Library — Index

Curated index of NetApp technical reference material for PS/SA/SAM/TAM work. Sourced from public docs.netapp.com and netapp.com; NetApp Support Site (mysupport.netapp.com) content requires an authenticated session and is not included here — flag if you need a specific entitlement-gated TR/KB pulled via your logged-in browser session.

**Read [OPERATING-PROTOCOL.md](OPERATING-PROTOCOL.md) first.** It governs how everything below is used to answer a technical question: version-correct verification, explicit disruption/data-loss risk classification on every recommended command, and rollback/pre-condition steps for anything state-changing. No answer sourced from this library should ever recommend a destructive or disruptive action without that risk being stated up front.

Last compiled: 2026-10-16 (see CHANGELOG.md). Refreshed regularly — see `CHANGELOG.md` for update history.

## Governance

- [OPERATING-PROTOCOL.md](OPERATING-PROTOCOL.md) — technical-accuracy and change-safety rules for every category below

## Categories

- [ONTAP-Core](ONTAP-Core/README.md) — CLI command reference, cluster/SVM administration, core best-practice TRs, FlexClone/FlexCache/FlexGroup, cluster/SVM peering, REST API/Ansible/Terraform automation, upgrades (see [CLI-Version-History.md](ONTAP-Core/CLI-Version-History.md) for version-to-version feature/CLI-behavior changes, 9.8–9.19.1)
- [Data-Protection](Data-Protection/README.md) — SnapMirror, SnapVault, SnapCenter, SnapLock (WORM/compliance), SnapDiff v3/SnapMirror Cloud, MetroCluster (see [MetroCluster-Deep-Dive.md](Data-Protection/MetroCluster-Deep-Dive.md) for finest-detail configuration/switch/sizing reference)
- [Networking-Performance](Networking-Performance/README.md) — NFS/CIFS/SMB, QoS, Ethernet storage network design (TR-4182), sizing and performance
- [Cloud-BlueXP](Cloud-BlueXP/README.md) — Cloud Volumes ONTAP, BlueXP/NetApp Console, StorageGRID, plus hyperscaler-native Azure NetApp Files/Amazon FSx for ONTAP/Google Cloud NetApp Volumes/OCI NetApp Storage Service (announced)
- [Hypervisors](Hypervisors/README.md) — VMware vSphere (incl. VMware Cloud Foundation 9), Hyper-V, RHV/KVM/OpenShift Virtualization, Nutanix AHV, Proxmox VE (incl. Storage Manager for Proxmox)
- [OpenStack](OpenStack/README.md) — Cinder (block) and Manila (file) driver integration
- [Kubernetes-Containers](Kubernetes-Containers/README.md) — Astra Trident CSI driver, Astra Control
- [Backup-3rdParty](Backup-3rdParty/README.md) — Veeam, Commvault, Veritas NetBackup, Rubrik, Cohesity, HYCU
- [Host-Integration-Cabling](Host-Integration-Cabling/README.md) — Host Utilities Kits, ALUA/multipathing, physical cluster/HA/MetroCluster cabling diagrams
- [Security-Hardening](Security-Hardening/README.md) — security hardening baseline, ransomware protection, encryption, MAV, remediation workflow
- [Operations-Troubleshooting](Operations-Troubleshooting/README.md) — AutoSupport, Active IQ, performance troubleshooting, support tooling
- [DSPM](DSPM/README.md) — Data Security Posture Management: NetApp Data Classification (formerly BlueXP Classification) plus 3rd-party DSPM (Varonis, Netwrix, BigID, Securiti) and DSPM-in-backup-platform capability
- [Security-Advisories](Security-Advisories/README.md) — NetApp CVEs/security advisories and known-bug tracking; daily-refreshed [ADVISORY-LOG.md](Security-Advisories/ADVISORY-LOG.md)
- [Platforms-Hardware](Platforms-Hardware/README.md) — current AFF/ASA/AFX/E-Series/StorageGRID lineup, NetApp Novus (AI throughput architecture), legacy/EOA/EOS platforms, expansion shelves, NetApp Keystone (STaaS, incl. Keystone Sovereign) (see [Firmware-Versions.md](Platforms-Hardware/Firmware-Versions.md) for platform/SP/BMC/shelf/disk/expansion-card firmware history)
- [Migration](Migration/README.md) — homogeneous/heterogeneous, storage-based (volume move, SnapMirror, 7MTT, FLI, XCP, Copy and Sync) and application-based (Shift Toolkit, SnapCenter, Astra Control, Cinder) migration tools
- [Customer-Success-Engagement](Customer-Success-Engagement/README.md) — CSM/TAM/SAM roles and methodology, customer success planning, stakeholder mapping, sales pipeline/opportunity qualification (MEDDPICC), NetApp portfolio whitespace map; see [Engagement-Plan-Playbook.md](Customer-Success-Engagement/Engagement-Plan-Playbook.md) for the fillable step-by-step tool — hand it a customer scenario and it produces a phased, measurable engagement plan

## Usage notes

- Each category README lists the canonical docs.netapp.com landing page plus the current key TR numbers and guides. Version-specific CLI/command reference links roll forward automatically at docs.netapp.com — the `/us-en/ontap-cli/` path (no version suffix) always resolves to the latest GA release.
- TR numbers are stable identifiers — search `netapp.com` or `docs.netapp.com` for the TR number directly if a linked URL changes.
- This library is a curated index, not a full mirror. For anything security- or entitlement-gated (KBs on mysupport.netapp.com, Field Portal content, AutoSupport/ActiveIQ data), authenticated access is required.
- The [Customer-Success-Engagement](Customer-Success-Engagement/README.md) category is different in kind from the other 15: it indexes business methodology (customer success planning, TAM/SAM engagement, sales pipeline generation), not version-pinned technical documentation. The [OPERATING-PROTOCOL.md](OPERATING-PROTOCOL.md) disruption/rollback classification doesn't apply there, though the same citation discipline (verified fact vs. general practice) does.
