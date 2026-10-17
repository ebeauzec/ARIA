# Varonis Fpolicy Best Practice and Recommendations
Source: https://kb.netapp.com/on-prem/ontap/da/NAS/NAS-KBs/Varonis_Fpolicy_Best_Practice_and_Recommendations
Fetched: 2026-07-07

Views: 11,897 | Visibility: Public | Votes: 8 | Category: ontap-9 | Specialty: nas
Last Published: 2022-05-25 | Last Modified: 2026-03-24

## Applies to

- CIFS
- NFS
- Varonis
- FPolicy

## Answer

### What are some Best Practices and Recommendations pertaining to Varonis Fpolicy Deployments?

- Varonis has some published best practices (requires Varonis login):
  - Fpolicy-Impacts-NetApp-Performance-Latency (Varonis KB): http://help.varonis.com/s/article/Fpolicy-Impacts-NetApp-Performance-Latency
  - NetApp CM Monitoring Results in NetApp Client Latency (Varonis KB): https://help.varonis.com/s/article/NetApp-CM-Monitoring-Results-in-NetApp-Client-Latency
- This guide is critical in ensuring that you are reviewing both the Varonis and NetApp side Best Practices.
- Review the Varonis KBs above for a more complete list of recommendations.

### Varonis Specific Recommendations

These recommendations are to be done in conjunction per Varonis guidelines and may require the customer reach out to Varonis for further details/clarifications.

- **Per Varonis guidelines, ensure Varonis version is up to date (consider version 8.6.22 and above).**
  - Varonis has deployed many enhancements regarding performance, efficiency and logging in their latest releases. Many of these enhancements have helped to match the performance improvements made by NetApp. See NetApp KB: "What is new in ONTAP 9.8 Shared Memory Implementation for FPolicy?"
  - For more information, review Varonis KB: "NetApp CM Monitoring Results in NetApp Client Latency."
  - Reach out to Varonis to ensure you are on the best release available.
- Other Varonis specific Best Practices:
  - Fpolicy-Impacts-NetApp-Performance-Latency
  - NetApp CM Monitoring Results in NetApp Client Latency

### NetApp Specific Recommendations

- **Upgrade to the appropriate versions of ONTAP that have fixes for known fpolicy related issues.**
  - Bug 1438207 — FPolicy might stop sending screen requests to the external engine if it enters a throttling state. (mysupport.netapp.com/site/bugs-online/product/ONTAP/BURT/1438207)

- **For Varonis External Engines, set send-buffer-size to 7895160.**
  - Varonis best practice is to set to maximum value: "The FPolicy Send-Buffer size is set to 7895160."
  ```
  ::*> vserver fpolicy policy external-engine modify -vserver <vserver> -engine-name <engine-name> -send-buffer-size 7895160
  ```
  - See also: "How to calculate send buffer for ONTAP 9 FPolicy" and "Write EAGAIN errors found in EMS and Fpolicy.log" (NetApp KBs).

- **To lessen the potential impact of latency, with Varonis guidance, set abort timeout lower, for example: 5s.**
  - If there is a large amount of latency between the Collector and the SVM, it can cause a delay in the TCP acknowledgements, and potential impact to latency in very rare occasions. To decrease end-user latency in cases where there are connection issues or CPU starvation on the collector, it is recommended to lower the "Timeout for Aborting a Request" from 40 to 5 seconds.
  ```
  ::*> vserver fpolicy policy external-engine modify -vserver <vserver> -engine-name <engine-name> -reqs-abort-timeout 5s
  ```
  - Reference: `vserver fpolicy policy external-engine show` CLI doc (docs.netapp.com/us-en/ontap-cli/vserver-fpolicy-policy-external-engine-show.html).
  - (Review Varonis KBs: Fpolicy-Impacts-NetApp-Performance-Latency and NetApp CM Monitoring Results in NetApp Client Latency.)

- **To lessen the potential impact of latency, with Varonis guidance, set fpolicy event filters.**
  - **Fpolicy Event filters:** During normal activity, fpolicy can be expected to cause latency. In order to minimize this, we can filter the fpolicy to not send events that we do not monitor. It is recommended that "first-read" and "first-write" are both filtered.
  ```
  ::> vserver fpolicy policy event create -vserver <Vserver Name> -event-name fp_event_varonis_cifs -file-operations create,create_dir,delete,delete_dir,open,read,write,rename,rename_dir,setattr -protocol cifs -filters first-read,first-write,open-with-delete-intent
  ```

### General Recommendations

- **Per TR-4429 Varonis DatAdvantage Best Practices** (https://www.netapp.com/media/17168-tr4429.pdf) — Review the TR for more Best Practices, including:

  To avoid performance issues, deactivate FPolicy during the following scenarios (note: activation of an FPolicy can increase the usage of resources on those stores and affect the performance of applications that use them):
  - When performing large data migrations from one NetApp storage system to another (large write or modification of files)
  - When upgrading your release of ONTAP to a newer version
  - When performing a Varonis upgrade (both IDU and probes or collectors)

  After performing any of these actions, you can safely activate FPolicy.

  Note: Manage VM datastores or SQL Server datastores with FPolicy with caution, because such stores are not accessed by humans and do not host human-generated data.

## Additional Information

- Varonis published best practices (requires Varonis login):
  - Fpolicy-Impacts-NetApp-Performance-Latency: http://help.varonis.com/s/article/Fpolicy-Impacts-NetApp-Performance-Latency
  - NetApp CM Monitoring Results in NetApp Client Latency: https://help.varonis.com/s/article/NetApp-CM-Monitoring-Results-in-NetApp-Client-Latency
- NetApp KB: "Poor CIFS and NFS Performance due to Varonis FPolicy Low Memory"
- NetApp KB: "Writes fail, error 0x8007054F: An internal error occurred on CIFS shares due to Varonis Fpolicy TCP Zero Windows Conditions"

### Related articles
- Varonis Fpolicy Best Practice and Recommendations (this article)
- Veritas Fpolicy Best Practice and Recommendations
- Komprise Fpolicy Best Practice and Recommendations
- Cloud Secure Fpolicy Best Practice and Recommendations
- Netwrix/Stealthbits Fpolicy Best Practice and Recommendations
- What are the FPolicy partner solutions for ONTAP?

---
NetApp provides no representations or warranties regarding the accuracy or reliability or serviceability of any information or recommendations provided in this publication or with respect to any results that may be obtained by the use of the information or observance of any recommendations provided herein. The information in this document is distributed AS IS and the use of this information or the implementation of any recommendations or techniques herein is a customer's responsibility and depends on the customer's ability to evaluate and integrate them into the customer's operational environment. This document and the information contained herein may be used solely in connection with the NetApp products discussed in this document.
