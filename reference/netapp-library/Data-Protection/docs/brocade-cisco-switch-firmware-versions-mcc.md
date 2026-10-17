# What versions of Brocade/Cisco switch firmware can be used in a MetroCluster?
Source: https://kb.netapp.com/Advice_and_Troubleshooting/Data_Protection_and_Security/MetroCluster/What_versions_of_Brocade_Cisco_switch_firmware_can_be_used_in_a_MetroCluster
Fetched: 2026-07-07

## Applies to

- ONTAP 8.2
- ONTAP 9
- MetroCluster
- Brocade
- Cisco
- Interoperability

## Answer

- NetApp tests firmware releases in MetroCluster to ensure the highest reliability and performance.
- Only firmware releases that are listed in the Interoperability Matrix Tool (IMT) or Hardware Universe (HWU) have undergone this qualification and are supported.
- For more information on reviewing a list of all the supported firmware versions, see the IMT and [HWU](https://hwu.netapp.com/).
- NetApp recommends using the latest qualified firmware for the ONTAP release.

For more information on upgrading your firmware to a supported version, see the following KB articles/documents:

**ONTAP 9:**
- [Upgrading or downgrading the firmware on a Brocade FC switch](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/task_upgrade_or_downgrad_the_firmware_on_a_brocade_fc_switch_mcc.html)
- [Upgrading or downgrading the firmware on a Cisco FC switch](https://docs.netapp.com/us-en/ontap-metrocluster/maintain/task_upgrade_or_downgrad_the_firmware_on_a_cisco_fc_switch_mcc.html)
- [Upgrading firmware on MetroCluster IP switches](https://docs.netapp.com/ontap-9/topic/com.netapp.doc.hw-metrocluster-service/GUID-BB4B86BA-6CDF-4281-AD85-BB2DB8569AFA.html)

**Data ONTAP 8.2 and earlier:**
- How to upgrade Brocade switch firmware in a fabric-attached MetroCluster (7-mode)?
- [How to upgrade Cisco switch firmware in a fabric-attached MetroCluster (7-mode)?](https://kb.netapp.com/on-prem/ontap/mc/MC-KBs/How_to_upgrade_Cisco_switch_firmware_in_a_fabric_attached_MetroCluster_7mode)

## Additional Information

NetApp provides no representations or warranties regarding the accuracy or reliability or serviceability of any information or recommendations provided in this publication or with respect to any results that may be obtained by the use of the information or observance of any recommendations provided herein. The information in this document is distributed AS IS and the use of this information or the implementation of any recommendations or techniques herein is a customer's responsibility and depends on the customer's ability to evaluate and integrate them into the customer's operational environment.

Related: [What should I do if my targeted MetroCluster IP switch firmware isn't in the IMT/HWU?](https://kb.netapp.com/on-prem/ontap/mc/MC-KBs/What_should_I_do_if_my_targeted_MetroCluster_IP_switch_firmware_isn_t_in_the_IMT_HWU); [When updating a MetroCluster to a newer ONTAP version, do the RCF files have to be updated?](https://kb.netapp.com/on-prem/ontap/mc/MC-KBs/When_updating_a_MetroCluster_to_a_newer_ONTAP_version_do_the_RCF_files_have_to_be_updated)
