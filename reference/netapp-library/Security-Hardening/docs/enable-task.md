# Enable ONTAP Autonomous Ransomware Protection on a volume
Source: https://docs.netapp.com/us-en/ontap/anti-ransomware/enable-task.html
Fetched: 2026-07-07

Beginning with ONTAP 9.10.1, you can enable Autonomous Ransomware Protection (ARP) on an existing volume or create a new volume with ARP enabled from the beginning.

## About this task

Follow the procedure matching your environment after ensuring prerequisites are met:
- NAS with FlexVol volumes
- NAS with FlexGroup volumes
- SAN volumes

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
- NAS workload with clients configured
- Active junction path for the volume

SAN-specific requirements:
- SVM with iSCSI, FC, or NVMe protocol enabled
- SAN workload with clients configured

General requirements:
- Correct license for your ONTAP version
- (Recommended) Multi-admin verification (MAV) enabled (9.13.1+)

## Enable ARP on NAS FlexVol volumes

### ONTAP 9.16.1 and later (ARP/AI, no learning period)

**System Manager**: Storage > Volumes > select volume > Security tab > switch Status from Disabled to Enabled. Verify status in the Anti-ransomware box.

**CLI**:
```
security anti-ransomware volume enable -volume <vol_name> -vserver <svm_name>
```
Create new volume with ARP enabled:
```
volume create -volume <vol_name> -vserver <svm_name> -aggregate <aggr_name> -size <nn> -anti-ransomware-state enabled -junction-path </path_name>
```
Verify:
```
security anti-ransomware volume show
```

### ONTAP 9.10.1 to 9.15.1 (requires learning mode / dry-run)

Recommended minimum 30 days in learning mode. Beginning with 9.13.1, ARP automates the optimal learning interval and switch (may occur before 30 days).

**System Manager**: Storage > Volumes > select volume > Security tab > switch Status to Enabled > select "Enabled in learning-mode".

Note: In existing volumes, learning/active modes only apply to newly written data — existing data is not scanned/analyzed.

**CLI**:
```
security anti-ransomware volume dry-run -volume <vol_name> -vserver <svm_name>
```
Create new volume with ARP enabled (dry-run):
```
volume create -volume <vol_name> -vserver <svm_name> -aggregate <aggr_name> -size <nn> -anti-ransomware-state dry-run -junction-path </path_name>
```
Disable automatic learning-to-active switching (9.13.1–9.15.1):
```
vserver modify <svm_name> -anti-ransomware-auto-switch-from-learning-to-enabled false
```
Verify:
```
security anti-ransomware volume show
```

## Enable ARP on NAS FlexGroup volumes

### ONTAP 9.18.1 and later (ARP/AI, no learning period)

**System Manager**: Storage > Volumes > select FlexGroup volume > Security tab > switch Status to Enabled. Verify in Anti-ransomware box.

**CLI**:
```
security anti-ransomware volume enable -volume <vol_name> -vserver <svm_name>
```
Create new FlexGroup volume with ARP enabled:
```
volume create -volume <vol_name> -vserver <svm_name> -aggr-list <aggregate name> -aggr-list-multiplier <integer> -size <nn> -anti-ransomware-state enabled -junction-path </path_name>
```
Verify:
```
security anti-ransomware volume show
```

### ONTAP 9.13.1 to 9.17.1 (learning mode)

Recommended minimum 30 days; ARP automates the optimal interval/switch.

**System Manager**: Storage > Volumes > select FlexGroup volume > Security tab > switch Status to Enabled > select "Enabled in learning-mode".

**CLI**:
```
security anti-ransomware volume dry-run -volume <vol_name> -vserver <svm_name>
```
Create new FlexGroup volume (dry-run):
```
volume create -volume <vol_name> -vserver <svm_name> -aggr-list <aggregate name> -aggr-list-multiplier <integer> -size <nn> -anti-ransomware-state dry-run -junction-path </path_name>
```
Disable automatic switching:
```
vserver modify <svm_name> -anti-ransomware-auto-switch-from-learning-to-enabled false
```
Verify:
```
security anti-ransomware volume show
```

## Enable ARP on SAN volumes

Beginning with ONTAP 9.17.1. ARP/AI is automatically enabled and immediately begins active monitoring during the evaluation period while determining workload suitability and setting the optimal encryption threshold.

**System Manager**: Storage > Volumes > select SAN volume > Security tab > switch Status to Enabled. ARP/AI automatically enters evaluation period. Verify state/evaluation status in Anti-ransomware box.

**CLI**:
```
security anti-ransomware volume enable -volume <vol_name> -vserver <svm_name>
```
Create new SAN volume with ARP enabled:
```
volume create -volume <vol_name> -vserver <svm_name> -aggregate <aggr_name> -size <nn> -anti-ransomware-state enabled
```
Verify state and evaluation status:
```
security anti-ransomware volume show
```
Check the `Block device detection status` field to monitor evaluation period progress.

## Related information

- Switch to active mode after a learning period: https://docs.netapp.com/us-en/ontap/anti-ransomware/switch-learning-to-active-mode.html

Last updated: 11/08/2025
</content>
