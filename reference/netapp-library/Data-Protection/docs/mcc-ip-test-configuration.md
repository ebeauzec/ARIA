# Test the ONTAP node switchover for your MetroCluster IP configuration
Source: https://docs.netapp.com/us-en/ontap-metrocluster/install-ip/task_test_the_mcc_configuration.html
Fetched: 2026-07-07

You can test failure scenarios to confirm the correct operation of the MetroCluster configuration.

## Verifying negotiated switchover

Tests the negotiated (planned) switchover to confirm uninterrupted data availability (except for SMB and Fibre Channel protocols). Takes about 30 minutes.

The `metrocluster switchover` command presents a warning prompt; responding `yes` switches over the partner site from the site the command is issued.

For MetroCluster IP configurations:
- ONTAP 9.4 and earlier: mirrored aggregates become degraded after negotiated switchover.
- ONTAP 9.5 and later: mirrored aggregates remain normal if remote storage is accessible; become degraded if remote storage access is lost.
- ONTAP 9.8 and later: unmirrored aggregates at the disaster site become unavailable if remote storage access is lost — this might cause a controller outage.

Steps:
1. Confirm all nodes are configured and normal: `metrocluster node show`
   ```
   cluster_A::>  metrocluster node show
       Cluster                        Configuration State    Mode
   ------------------------------ ---------------------- ------------------------
    Local: cluster_A               configured             normal
   Remote: cluster_B               configured             normal
   ```
2. Begin switchover: `metrocluster switchover`
   ```
   cluster_A::> metrocluster switchover
   Warning: negotiated switchover is about to start. It will stop all the data Vservers on cluster "cluster_B" and
   automatically re-start them on cluster "cluster_A". It will finally gracefully shutdown cluster "cluster_B".
   ```
3. Confirm local cluster is configured and in switchover mode: `metrocluster node show`
   ```
   cluster_A::>  metrocluster node show
       Cluster                        Configuration State    Mode
   ------------------------------ ---------------------- ------------------------
   Local: cluster_A                configured             switchover
   Remote: cluster_B               not-reachable          -
                 configured             normal
   ```
4. Confirm switchover succeeded: `metrocluster operation show`
   ```
   cluster_A::> metrocluster operation show
     Operation: switchover
         State: successful
    Start Time: 2/6/2016 13:28:50
      End Time: 2/6/2016 13:29:41
        Errors: -
   ```
5. Use `vserver show` and `network interface show` to verify DR SVMs and LIFs have come online.

## Verifying healing and manual switchback

Tests healing and manual switchback to verify data availability is not affected (except SMB and Solaris FC configurations) when switching back to the original data center. Takes about 30 minutes; expected result is services switched back to home nodes.

Note: healing steps are NOT required on ONTAP 9.5+ (automatic after negotiated switchover) or ONTAP 9.6+ (also automatic after unscheduled switchover).

Steps:
1. ONTAP 9.4 or earlier: heal the data aggregate: `metrocluster heal aggregates`
   ```
   cluster_A::> metrocluster heal aggregates
   [Job 936] Job succeeded: Heal Aggregates is successful.
   ```
2. ONTAP 9.4 or earlier (also required on MetroCluster FC configurations generally): heal the root aggregate: `metrocluster heal root-aggregates`
   ```
   cluster_A::> metrocluster heal root-aggregates
   [Job 937] Job succeeded: Heal Root Aggregates is successful.
   ```
3. Verify healing completed: `metrocluster node show`
   ```
   cluster_A::> metrocluster node show
   DR                               Configuration  DR
   Group Cluster Node               State          Mirroring Mode
   ----- ------- ------------------ -------------- --------- --------------------
   1     cluster_A
                 node_A_1         configured     enabled   heal roots completed
         cluster_B
                 node_B_2         unreachable    -         switched over
   42 entries were displayed.
   ```
   If automatic healing fails, issue `metrocluster heal` commands manually (as in pre-9.5 versions). Use `metrocluster operation show` and `metrocluster operation history show -instance` to monitor healing status and diagnose failures.
4. Verify all aggregates are mirrored: `storage aggregate show` — RAID Status should show "mirrored" for relevant aggregates (example output shows data_cluster and root_cluster as raid_dp, mirrored, normal, plus a "cluster_B Switched Over Aggregates" section).
5. Check switchback recovery status: `metrocluster node show`
   ```
   cluster_A::> metrocluster node show
   DR                               Configuration  DR
   Group Cluster Node               State          Mirroring Mode
   ----- ------- ------------------ -------------- --------- --------------------
   1     cluster_A
                node_A_1            configured     enabled   heal roots completed
         cluster_B
                node_B_2            configured     enabled   waiting for switchback
                                                             recovery
   2 entries were displayed.
   ```
6. Perform switchback: `metrocluster switchback`
   ```
   cluster_A::> metrocluster switchback
   [Job 938] Job succeeded: Switchback is successful.
   ```
7. Confirm node status: `metrocluster node show` — both nodes should show configuration state "configured", mode "normal".
8. Confirm operation status: `metrocluster operation show`
   ```
   cluster_A::> metrocluster operation show
     Operation: switchback
         State: successful
    Start Time: 2/6/2016 13:54:25
      End Time: 2/6/2016 13:56:15
        Errors: -
   ```

## Verifying operation after power line disruption

Tests MetroCluster's response to a PDU failure. Best practice: each PSU in a component connects to a separate power supply — if both PSUs share a PDU, an electrical disruption could take down the site or a whole shelf. Takes about 15 minutes. Requires turning off power to all left-hand PDUs, then all right-hand PDUs, on all racks containing MetroCluster components.

Expected results: errors are generated as PDUs are disconnected; no failover or loss of service occurs.

Steps:
1. Turn off power to left-hand PDUs on the racks containing MetroCluster components.
2. Monitor console: `system environment sensors show -state fault` and `storage shelf show -errors`
   ```
   cluster_A::> system environment sensors show -state fault
       Node Sensor 			State Value/Units Crit-Low Warn-Low Warn-Hi Crit-Hi
   ---- --------------------- ------ ----------- -------- -------- ------- -------
   node_A_1
   		PSU1 			fault
   							PSU_OFF
   		PSU1 Pwr In OK 	fault
   							FAULT
   node_A_2
   		PSU1 			fault
   							PSU_OFF
   		PSU1 Pwr In OK 	fault
   							FAULT
   4 entries were displayed.

       cluster_A::> storage shelf show -errors
       Shelf Name: 1.1
        Shelf UID: 50:0a:09:80:03:6c:44:d5
    Serial Number: SHFHU1443000059

       Error Type          Description
   ------------------  ---------------------------
   Power               Critical condition is detected in storage shelf power supply unit "1". The unit might fail.Reconnect PSU1
   ```
3. Turn power back on to the left-hand PDUs.
4. Confirm ONTAP clears the error condition.
5. Repeat with the right-hand PDUs.

## Verifying operation after loss of a single storage shelf

Tests failure of a single storage shelf to verify no single point of failure. Expected results: an error is reported by monitoring software; no failover or loss of service occurs; mirror resynchronization starts automatically once the hardware is restored.

Steps:
1. Check storage failover status: `storage failover show` — both nodes should show "Possible: true" and "Connected to <partner>".
2. Check aggregate status: `storage aggregate show` — note baseline RAID Status ("mirrored, normal") for mirrored and unmirrored aggregates before the test.
3. Verify data SVMs/volumes are online: `vserver show -type data`, `network interface show -fields is-home false`, `volume show !vol0,!MDV*` — confirm all running/online, no LIFs away from home.
4. Identify a Pool 1 shelf on the target node to power off (must contain drives in a mirrored data aggregate): `storage aggregate show -r -node node-name !*root` — e.g., shelf ID 31 selected, showing plex0 (pool0, local) and plex4 (pool1, remote) RAID groups.
5. Physically power off the selected shelf.
6. Recheck aggregate status: `storage aggregate show` and `storage aggregate show -r -node node_A_2 !*root` — the affected aggregate shows RAID Status "mirror degraded"; drives on the affected plex show status "failed" and the plex itself shows "offline, failed, inactive".
7. Verify data is still served and volumes remain online: `vserver show -type data`, `network interface show -fields is-home false`, `volume show !vol0,!MDV*` — SVMs continue running (now backed by the surviving node/aggregate), no LIFs displaced.
8. Physically power the shelf back on — resynchronization starts automatically.
9. Verify resynchronization started: `storage aggregate show` — affected aggregate shows RAID Status "resyncing".
10. Monitor until resynchronization completes: `storage aggregate show` — affected aggregate returns to RAID Status "normal".
