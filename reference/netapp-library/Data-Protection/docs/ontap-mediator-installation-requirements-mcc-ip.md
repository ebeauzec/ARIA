# ONTAP Mediator installation requirements for MetroCluster IP configurations
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_mediator_requirements.html
Fetched: 2026-07-07 · HTTPS multi-configuration sections re-fetched and corrected 2026-10-08 (live page dated 07/17/2026)

Your environment must meet certain requirements. The following requirements apply to one disaster recovery group (DR group). See [DR groups](https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/concept_parts_of_an_ip_mcc_configuration_mcc_ip.html#disaster-recovery-dr-groups).

- If you plan on updating your Linux version, do so before you install the most current version of ONTAP Mediator.
- The ONTAP Mediator and MetroCluster Tiebreaker software should not both be used with the same MetroCluster configuration.
- ONTAP Mediator must be installed on a Linux host at a separate location from the MetroCluster sites. The connectivity between the ONTAP Mediator and each site must be two separate failure domains.
- Automatic unplanned switchover is supported in ONTAP 9.7 and later.
- Beginning with ONTAP 9.19.1 and ONTAP Mediator 1.12, you can configure an ONTAP Mediator that uses HTTPS for communication instead of iSCSI. How many MetroCluster IP configurations one HTTPS Mediator instance can monitor depends on the Mediator version and host size (see "Use ONTAP Mediator to monitor multiple MetroCluster IP configurations" below). *(Corrected 2026-10-08: the 2026-07-07 snapshot said "only one" for HTTPS; the live page now gives up to 10 four-node / 5 eight-node from Mediator 1.12.1.)*
- Beginning with ONTAP 9.18.1 and ONTAP Mediator 1.11, a single ONTAP Mediator instance configured with iSCSI can manage up to ten MetroCluster configurations simultaneously. In ONTAP 9.17.1 and ONTAP Mediator 1.10 and earlier, an ONTAP Mediator configured with iSCSI can support up to five MetroCluster configurations simultaneously.
- Beginning with ONTAP 9.18.1, IPv6 is supported for ONTAP Mediator 1.11 or later in a MetroCluster IP configuration.

## Network requirements for using ONTAP Mediator in a MetroCluster configuration

- **Latency**: Maximum latency of less than 75ms (RTT). Jitter must be no more than 5ms.
- **MTU**: The MTU size must be at least 1400.
- **Packet loss**: For both ICMP and TCP traffic, packet loss must be less than 0.01%.
- **Bandwidth**: The link between ONTAP Mediator and one DR group must have at least 20Mbps of bandwidth.
- **Independent connectivity**: Independent connectivity between each site and the ONTAP Mediator is required. A failure in one site must not interrupt the IP connectivity between the other two unaffected sites.

## Host requirements for ONTAP Mediator in a MetroCluster configuration

- ONTAP Mediator must be installed at an external site that is physically separated from the two ONTAP clusters.
- ONTAP Mediator does not require more than the host operating system's minimum requirements for CPU and memory (RAM).
- In addition to the host operating system's minimum requirements, at least 30GB of additional usable disk space must be available. Each DR group requires up to 200MB of disk space.

## Select a communication protocol for ONTAP Mediator

By default, MetroCluster IP nodes access ONTAP Mediator mailbox LUNs using iSCSI sessions. ONTAP Mediator relies on the SCST package to provide iSCSI. iSCSI sessions are authenticated using the Challenge Handshake Authentication Protocol (CHAP) with an obfuscated, machine-generated pre-shared key, but are not fully encrypted.

Beginning with ONTAP 9.19.1 and ONTAP Mediator 1.12, you can configure an ONTAP Mediator instance that uses HTTPS for communication instead of iSCSI. HTTPS is a secure protocol that encrypts entire sessions using SSL/TLS, providing increased security compared with iSCSI. You can only configure an ONTAP Mediator that uses HTTPS using the CLI — System Manager is not supported.

You can install ONTAP Mediator with support for both iSCSI and HTTPS, or HTTPS only. You can configure ONTAP Mediator with iSCSI or HTTPS, not both. Using a mix of protocols in your deployment is not supported.

See [HTTPS and iSCSI installation options for ONTAP Mediator](https://docs.netapp.com/us-en/ontap/mediator/index.html#https-iscsi-installation).

## Use ONTAP Mediator to monitor multiple MetroCluster IP configurations

*(Section added 2026-10-08 from the live page, dated 07/17/2026. It replaces the 2026-07-07 caution that said one HTTPS instance could monitor only one configuration.)*

### ONTAP Mediator configured with HTTPS

> **Caution:** Attempting to add multiple HTTPS ONTAP Mediator instances beyond the limitations described in this section is not supported.

| ONTAP Mediator version | Host OS requirements | Four-node MetroCluster IP configurations | Eight-node MetroCluster IP configurations |
| --- | --- | --- | --- |
| 1.12 | N/A | 1 | 1 |
| 1.12.1 and later | Hosts with fewer than 8 CPU cores and at least 8GB of RAM | 1 | 1 |
| 1.12.1 and later | Hosts with at least 8 CPU cores and at least 16GB of RAM | 10 | 5 |

**MetroCluster IP + SnapMirror active sync on one instance**: beginning with ONTAP 9.19.1 and ONTAP Mediator 1.12, the same Mediator instance can monitor one four-node MetroCluster IP configuration and one SnapMirror active sync cluster peer relationship at the same time. Requirements: Mediator 1.12.1 or later on a host OS with a 2-core CPU, and the instance configured with HTTPS. Only one four-node MetroCluster IP configuration and one SnapMirror active sync peer relationship are supported this way.

### ONTAP Mediator configured with iSCSI

- Beginning with ONTAP 9.18.1 and ONTAP Mediator 1.11, one iSCSI Mediator instance can manage up to ten MetroCluster configurations at the same time.
- In ONTAP 9.17.1 and ONTAP Mediator 1.10 and earlier, one iSCSI Mediator instance can support up to five MetroCluster configurations at the same time.

## Guidelines for upgrading ONTAP Mediator in a MetroCluster configuration

If you are upgrading ONTAP Mediator you must meet the Linux version requirements and follow guidelines for the upgrade.

- ONTAP Mediator can be upgraded from an immediately prior version to the current version.
- All Mediator versions are supported on MetroCluster IP configurations running ONTAP 9.7 or later.

See [Install or upgrade ONTAP Mediator](https://docs.netapp.com/us-en/ontap/mediator/index.html).

## After the upgrade

After the Mediator and operating system upgrade is complete, you should issue the `storage iscsi-initiator show` command to confirm that the Mediator connections are up.
