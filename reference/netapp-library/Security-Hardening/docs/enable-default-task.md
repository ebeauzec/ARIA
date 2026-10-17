# Enable ONTAP Autonomous Ransomware Protection by default in new volumes
Source: https://docs.netapp.com/us-en/ontap/anti-ransomware/enable-default-task.html
Fetched: 2026-07-07

Beginning with ONTAP 9.10.1, you can configure storage VMs (SVMs) so that new volumes are enabled by default with ARP, via System Manager or the ONTAP CLI.

Beginning with ONTAP 9.18.1, ARP is enabled by default on all new volumes at the cluster level for supported systems, after a 12-hour grace period following a cluster upgrade or new installation. If you disable automatic default enablement at the cluster level, you can still manually enable ARP by default on all new volumes at the SVM level.

For ONTAP 9.17.1 and earlier, SVM-level configuration is the only way to enable ARP by default on new volumes.

## About this task

By default, new volumes are created with ARP disabled. You need to enable ARP functionality and set it as default for new volumes in the SVM. Existing volumes without ARP will NOT automatically change when you change the SVM default — this only affects new volumes.

Transitional period after enabling ARP:

| Volume type | ONTAP version | Behavior after enablement |
| --- | --- | --- |
| NAS FlexGroup | 9.18.1+ | ARP/AI active immediately, no learning period |
| NAS FlexGroup | 9.13.1–9.17.1 | Learning mode for 30 days |
| NAS FlexVol | 9.16.1+ | ARP/AI active immediately, no learning period |
| NAS FlexVol | 9.10.1–9.15.1 | Learning mode for 30 days |
| SAN volumes | 9.17.1+ | ARP/AI active immediately; evaluation period to establish alert threshold |

## Before you begin

NAS-specific requirements:
- SVM with NFS or SMB (or both) enabled
- Active junction path for the volume

SAN-specific requirements:
- SVM with iSCSI, FC, or NVMe protocol enabled

General requirements:
- Correct license for your ONTAP version
- (Recommended) MAV enabled (9.13.1+)

## Steps

**System Manager**:
1. Select Storage or Cluster (per environment) > Storage VMs > select the storage VM.
2. Settings tab > Security > Anti-ransomware tile > select Edit (pencil icon).
3. Check the box to enable ARP. Check the additional box to enable ARP on all eligible volumes in the storage VM.
4. For ONTAP versions with a recommended learning period, select "Switch automatically from learning to active mode after sufficient learning" to let ARP auto-determine the optimal interval.

**CLI**:

Modify an existing SVM to enable ARP by default for new volumes (use `dry-run` if a learning period is required, otherwise `enabled`):
```
vserver modify -vserver <svm_name> -anti-ransomware-default-volume-state <dry-run|enabled>
```

Create a new SVM with ARP enabled by default:
```
vserver create -vserver <svm_name> -anti-ransomware-default-volume-state <dry-run|enabled>
```

Disable automatic learning-to-active transition (for ONTAP 9.13.1–9.15.1, when default state is dry-run with adaptive learning enabled):
```
vserver modify <svm_name> -anti-ransomware-auto-switch-from-learning-to-enabled false
```

Verify ARP state:
```
security anti-ransomware volume show
```

## Related information

- Switch to active mode after a learning period: https://docs.netapp.com/us-en/ontap/anti-ransomware/switch-learning-to-active-mode.html
- security anti-ransomware volume show (ONTAP CLI reference)

Last updated: 01/13/2026
</content>
