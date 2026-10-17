# Autonomous Ransomware Protection for NFS and VMFS
Source: https://docs.netapp.com/us-en/netapp-solutions-virtualization/vmware/vmw-arp-nfs-vmfs.html
Fetched: 2026-07-07

NetApp ONTAP's Autonomous Ransomware Protection (ARP) uses machine learning to secure NFS and VMFS datastores in VMware environments, providing early threat detection, tamper-proof snapshots, and rapid recovery.

## Overview

ONTAP storage provides built-in security features that proactively safeguard data. If a breach occurs, ONTAP delivers real-time alerts and rapid recovery options to reduce downtime and limit data loss.

## Use case — Protect VMware VMs and their files

Early ransomware detection in VMware environments is critical to stopping spread and minimizing downtime. Key ONTAP features: Snapshot technology (point-in-time recovery), Autonomous Ransomware Protection (ARP, ML-based), multi-admin verify, and tamper-proof snapshots. Securing vSphere/guest VMs also requires network segmentation, EDR/XDR/SIEM, timely patching, hardening guidelines, and enterprise anti-malware inside guest VMs.

## How ONTAP helps

This document focuses on ARP enhancements introduced in ONTAP 9.17.1. ARP can be enabled on NAS or SAN volumes supporting VMware datastores. It uses built-in ML to monitor workload patterns and data entropy, automatically detecting ransomware activity signs. Configure ARP per volume via CLI or System Manager.

## ARP feature evolution

- **ONTAP 9.10.1**: ARP available for existing or new volumes.
- **ONTAP 9.16.1**: ARP can be enabled via System Manager or CLI; protection is active immediately, no learning period required.
- **ONTAP 9.17.1**: ARP supports SAN volumes. When enabled on a SAN volume, ARP/AI continuously monitors data during an evaluation period to determine workload suitability and set the optimal encryption threshold for detection.

ARP is built into ONTAP for integrated control with other ONTAP features. It processes data in real time as written/read, creates locked snapshots at regular intervals alongside scheduled ones, and recycles snapshots when no anomalies are found. If suspicious activity is detected, it preserves the pre-attack snapshot longer for reliable recovery.

> **Note:** ARP support is included with the ONTAP ONE license.

## Configuring ARP on NAS volumes and simulating an attack

When ARP is enabled on a NAS volume (System Manager or CLI), protection is active immediately — no learning period. In the documented test, a script modified files / changed file extensions to simulate an attack on a VM residing on an NFS volume mounted as a vCenter datastore. ARP detected the abnormal activity, and recovery used the ARP periodic snapshot generated just before the incident.

See "ARP for NFS storage" for detailed NFS datastore guidance.

## Configuring ARP on SAN volumes and simulating an attack

When enabled on a SAN volume, ARP begins with an evaluation phase (similar to NAS learning mode) before transitioning to active detection. It runs a 2–4 week evaluation period with a 75% threshold to baseline encryption behavior. Monitor progress via `security anti-ransomware volume show`, checking **Block device detection status**; a status of **Active_suitable_workload** confirms observed entropy levels are suitable for ongoing monitoring. ARP then auto-adjusts its adaptive threshold. The snapshot creation interval can be changed from the default 4h to 1h (use caution).

Since ONTAP 9.17.1, ARP snapshots are generated at regular intervals for both NAS and SAN volumes.

In the SAN test, files were encrypted within a VM on an iSCSI-based datastore (~7000 files affected). Within 10 minutes, ARP detected abnormal activity based on high entropy and generated a threat alert.

See "SAN environments and mode types" (ONTAP anti-ransomware docs) for details.

## Recovering a VM after a ransomware attack

Once an attack is confirmed, restore data using an ARP snapshot (or another volume snapshot) via System Manager > Volume Snapshots. See "Restore data from ARP snapshot after a ransomware attack" (ONTAP anti-ransomware docs) for detailed guidance.

## ONTAP as a defense layer for VMware and beyond

ML-based ARP detection adds a powerful defense layer in VMware environments, identifying threats early and mitigating damage before escalation. The same principles extend to any NAS or SAN-based application for a multi-layered security architecture.

*Page last updated: 08/22/2025*
