# Networking & Performance — NFS/CIFS, QoS, Sizing

## NAS protocols (NFS/CIFS/SMB)
- [ONTAP NAS technical reports index](https://docs.netapp.com/us-en/ontap-technical-reports/nas.html) — **re-checked 2026-08-24 via direct fetch**: index page now contributor-dated 07/23/2026 (advanced from 04/14/2025 last seen 2026-08-17 — a genuine revision, not just a re-render), page body did not return listable TR entries on this fetch. TR-4067 remains the primary NFS TR. The five previously-flagged-but-uncross-linked TRs are added below per the standing re-verification queue.
- **Re-checked 2026-09-07 via direct fetch**: still contributor-dated 07/23/2026, unchanged from the 08-24 check; page body again did not return listable TR entries on this fetch (same JS-rendering limitation as before). No new TR to add from this page this pass.
- **Re-checked 2026-09-14 via direct fetch**: still contributor-dated 07/23/2026, unchanged.
- TR-4067 — NFS in ONTAP: best practice and implementation guide
- TR-4962 — NFSv4.2 extended attributes in ONTAP (ONTAP 9.12.1+) — **added 2026-08-24**
- TR-4814 — S3 in ONTAP (now a docs.netapp.com concept hub rather than a static PDF) — **added 2026-08-24**
- TR-4523 — DNS load balancing in ONTAP — **added 2026-08-24**
- TR-4835 — LDAP fundamentals and best practices for multiprotocol NAS identity in ONTAP — **added 2026-08-24**
- TR-4616 — NFS Kerberos in ONTAP — **added 2026-08-24**
- TR-4887 — Multiprotocol NAS in ONTAP: overview and best practices ([PDF](https://www.netapp.com/media/27436-tr-4887.pdf))
- TR-4668 — Name services best practices guide for CIFS/SMB and NFS in ONTAP
- TR-4191 — Best practices guide for clustered Data ONTAP Windows File Services (SMB)
- TR-4740 — SMB 3.0 Multichannel: capabilities, recommended practices, performance results
- [Best practices for network configuration with NetApp storage systems (KB)](https://kb.netapp.com/Advice_and_Troubleshooting/Data_Storage_Software/ONTAP_OS/Best_Practices_for_Network_Configuration_with_NetApp_Storage_Systems)

## Routing
**New section, added 2026-09-07** — [ONTAP networking technical reports index](https://docs.netapp.com/us-en/ontap-technical-reports/networking.html) (direct-fetched; contributor-dated 07/23/2026), a category-index page not previously cross-linked in this file, groups TRs under "Routing" and "Name services" headings. Its Name services entries (TR-4523, TR-4668, TR-4835) are already carried under NAS protocols above; the Routing entry below was not previously indexed in this category.
- TR-4949 — BGP/VIP with ONTAP in the data center ([PDF](https://www.netapp.com/pdf.html?item=/media/79703-TR-4949.pdf)) — quick-deploy guide for a basic BGP configuration in ONTAP; relevant background for VIP LIF designs referenced elsewhere in this library (e.g., [Data-Protection](../Data-Protection/README.md)'s MetroCluster IP MD5-authenticated BGP peer groups, added ONTAP 9.16.1).
- **Re-checked 2026-09-14 via direct fetch**: [networking.html](https://docs.netapp.com/us-en/ontap-technical-reports/networking.html) still contributor-dated 07/23/2026, unchanged — Routing section still lists only TR-4949, Name services section still lists TR-4523/TR-4668/TR-4835 (already carried under NAS protocols above). No new entries.

## Ethernet storage network design
- TR-4182 — Ethernet Storage Design Considerations and Best Practices for Clustered ONTAP configurations ([PDF](https://www.netapp.com/media/16885-tr-4182.pdf)) — **added 2026-07-11**: common cluster/Ethernet network deployment scenarios, flow-control, VLAN, link-aggregation (IFGRP), and Spanning Tree Protocol recommendations; cross-check switch-side port configuration (Cisco/Juniper/Brocade/other) against whatever IFGRP mode is configured cluster-side, since a mismatch here is a common source of hard-to-diagnose network flapping.
- TR-3802 — Ethernet Storage Best Practices ([PDF](https://www.netapp.com/media/19748-tr-3802.pdf)) — older but still-referenced companion guide; cross-check both against the current platform's cabling guide in [Host-Integration-Cabling](../Host-Integration-Cabling/README.md) before finalizing a network design, since example configurations in these TRs can predate current-generation switch/platform combinations.

## SAN protocols
- TR-4080 — Best practices for modern SAN in ONTAP ([PDF](https://www.netapp.com/pdf.html?item=/media/10680-tr4080.pdf))
- TR-4684 — Implementing and configuring modern SANs with NVMe over Fabrics (NVMe-oF): FC-NVMe and NVMe/TCP design, implementation, configuration, and recommended practices ([PDF](https://www.netapp.com/pdf.html?item=/media/10681-tr4684.pdf)) — **added 2026-08-24**, confirmed current and listed on the SAN TR index
- TR-4968 — NetApp All-SAN Array data availability and integrity: data protection/integrity features and recommended practices for ASA network design ([PDF](https://www.netapp.com/pdf.html?item=/media/85671-tr-4968.pdf)) — **added 2026-08-24**, confirmed current and listed on the SAN TR index
- [ONTAP SAN technical reports index](https://docs.netapp.com/us-en/ontap-technical-reports/san.html) — **re-checked 2026-08-24 via direct fetch**: index page still contributor-dated 04/14/2025, unchanged. Also lists a NetApp Verified Architecture ("Modern SAN Cloud-Connected Flash Solution," jointly designed with VMware/Broadcom) not yet indexed here — not added this pass since it's an NVA rather than a TR, flagged for a future pass if NVA references come into scope.
- **Re-checked 2026-09-07 via direct fetch**: still contributor-dated 04/14/2025, unchanged, same four entries (TR-4080, TR-4684, TR-4968, and the NVA). A WebSearch summary this pass surfaced "TR-5009: Best Practices for NetApp ASA" (per its own PDF, dated July 2025) — **rejected for addition**: TR-5009 does not appear on this directly-fetched canonical SAN TR index page, so it is not confirmed as an indexed/current entry for this category; not added until it shows up on a canonical docs.netapp.com index page.
- **Re-checked 2026-09-14 via direct fetch**: still contributor-dated 04/14/2025, unchanged, same four entries. Re-tested the TR-5009 rejection: the PDF genuinely exists at two netapp.com/media URLs (`137426-tr-5009-best-practices-for-netapp-asa.pdf` and `138231-tr-5009-best-practices-for-netapp-asa.pdf`, authored by Sweksha Chaubey and Michael Peppers, PDF metadata dated July 2025, covering ASA A20–A1K network/compute/storage/VMware best practices) — but it still does not appear on this canonical `ontap-technical-reports/san.html` index page. Standing rejection reconfirmed: not added until NetApp indexes it here.

## QoS
- [Guarantee throughput with ONTAP QoS — concept](https://docs.netapp.com/us-en/ontap/performance-admin/guarantee-throughput-qos-task.html)
- [Set a throughput ceiling with QoS policy groups](https://docs.netapp.com/us-en/ontap/performance-admin/set-throughput-ceiling-qos-task.html)
- [Set a throughput floor with QoS policy groups](https://docs.netapp.com/us-en/ontap/performance-admin/set-throughput-floor-qos-task.html)
- [Set throughput with adaptive QoS policy groups](https://docs.netapp.com/us-en/ontap/performance-admin/adaptive-qos-policy-groups-task.html)
- [What is QoS in ONTAP? (KB)](https://kb.netapp.com/on-prem/ontap/Perf/Perf-KBs/What_is_Quality_of_Service_QoS_in_ONTAP)
- [qos statistics performance show — CLI reference](https://docs.netapp.com/us-en/ontap-cli/qos-statistics-workload-performance-show.html)
- Adaptive QoS scales the ceiling/floor with volume size to hold a fixed IOPS/TB (or /GB) ratio — resizing a volume automatically rescales the policy group.

## Sizing & performance analysis
- [Best-practice guidelines for ONTAP File System Analytics — TR-4867 (PDF)](https://www.netapp.com/media/20707-tr-4867.pdf)
- [ONTAP Technical Reports index](https://docs.netapp.com/us-en/ontap-technical-reports/) (filter by workload for sizing guidance specific to a given application)
