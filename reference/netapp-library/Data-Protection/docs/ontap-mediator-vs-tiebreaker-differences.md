# Differences between ONTAP Mediator and MetroCluster Tiebreaker
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_considerations_mediator.html
Fetched: 2026-07-07

Beginning with ONTAP 9.7, you can use either the ONTAP Mediator-assisted automatic unplanned switchover (MAUSO) in the MetroCluster IP configuration or you can use the MetroCluster Tiebreaker software. It is not required to use MAUSO or Tiebreaker; however, if you choose not to use either, you must [perform a manual recovery](https://docs.netapp.com/us-en/ontap-metrocluster/disaster-recovery/concept_dr_workflow.html) if a disaster occurs.

The different MetroCluster configurations perform automatic switchover under different circumstances:

- **MetroCluster FC configurations using the AUSO capability (not present in MetroCluster IP configurations)** — AUSO is initiated if controllers fail but the storage (and bridges, if present) remain operational.
- **MetroCluster IP configurations using ONTAP Mediator (ONTAP 9.7 and later)** — MAUSO is initiated in the same circumstances as AUSO above, and also after a complete site failure (controllers, storage, and switches). See [How ONTAP Mediator supports automatic unplanned switchover](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept-ontap-mediator-supports-automatic-unplanned-switchover.html).
- **MetroCluster IP or FC configurations using the Tiebreaker software in active mode** — the Tiebreaker initiates unplanned switchover after a complete site failure. Before using the Tiebreaker software, review [MetroCluster Tiebreaker Software installation and configuration](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_overview_of_the_tiebreaker_software.html).

## Interoperability of ONTAP Mediator with other applications and appliances

You cannot use any third-party applications or appliances that can trigger a switchover in combination with ONTAP Mediator. In addition, monitoring a MetroCluster configuration with MetroCluster Tiebreaker software is not supported when using ONTAP Mediator.
