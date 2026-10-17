# Set up MetroCluster Tiebreaker or ONTAP Mediator for a MetroCluster IP configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/task_sw_config_configure_mediator.html
Fetched: 2026-07-07

You can download and install on a third site either the MetroCluster Tiebreaker software, or, beginning with ONTAP 9.7, the ONTAP Mediator.

## Before you begin

You must have a Linux host available that has network connectivity to both clusters in the MetroCluster configuration. The specific requirements are in the MetroCluster Tiebreaker or ONTAP Mediator documentation.

If you are connecting to an existing Tiebreaker or ONTAP Mediator instance, you need the username, password, and IP address of the Tiebreaker or Mediator.

If you must install a new instance of the ONTAP Mediator, follow the directions in [Configure ONTAP Mediator for unplanned automatic switchover](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_mediator_requirements.html).

If you must install a new instance of the Tiebreaker software, follow the [directions to install and configure the software](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_overview_of_the_tiebreaker_software.html).

## About this task

You cannot use both the MetroCluster Tiebreaker software and the ONTAP Mediator with the same MetroCluster configuration. See [Considerations for using ONTAP Mediator or MetroCluster Tiebreaker](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_considerations_mediator.html).

## Step

1. Configure ONTAP Mediator or the Tiebreaker software:
   - If you are using an existing instance of the ONTAP Mediator, add ONTAP Mediator to ONTAP:
     ```
     metrocluster configuration-settings mediator add -mediator-address ip-address-of-mediator-host
     ```
   - If you are using the Tiebreaker software, refer to the [Tiebreaker documentation](https://docs.netapp.com/us-en/ontap-metrocluster/tiebreaker/concept_overview_of_the_tiebreaker_software.html).
