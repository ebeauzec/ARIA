# Deployment steps
Source: https://docs.netapp.com/us-en/netapp-solutions-dataops/xcp/xcp-bp-deployment-steps.html
Fetched: 2026-07-07

This section covers deployment steps for NetApp XCP for data transfer.

## Test bed details

| Solution components | Details |
|---|---|
| XCP version 1.7 | One Linux server (RHEL 7.9 or RHEL 8); one Windows server (Windows Server 2019 standard) |
| NetApp AFF storage array HA pair for the source volume | AFF8080, NetApp ONTAP 9, NFS protocol |
| NetApp AFF storage array HA pair for destination volume | AFF A800, ONTAP 9, NFS protocol |
| Fujitsu PRIMERGY RX2540 server | 48 CPUs, Intel Xeon, 256GB physical memory, 10GbE dual port (each) |
| Networking | 10GbE |

## Deployment steps - NAS

To deploy NetApp XCP for data transfer, first install and activate the XCP software on the destination location. Review details in the NetApp XCP User Guide (https://mysupport.netapp.com/documentation/productlibrary/index.html?productID=63064).

1. Meet the prerequisites detailed in "Prerequisites for XCP" (https://docs.netapp.com/us-en/netapp-solutions-dataops/xcp/xcp-bp-netapp-xcp-overview.html#prerequisites-for-xcp).
2. Download the XCP software from the NetApp XCP (Downloads) page (https://mysupport.netapp.com/site/products/all/details/netapp-xcp/downloads-tab).
3. Copy the downloaded XCP tar files to the XCP server:
```
# scp Documents/OneDrive\ -\ NetApp\ Inc/XCP/software/1.6.1/NETAPP_XCP_1.6.1.tgz root@<host>:/usr/src
```
4. Untar the tarfile:
```
[root@mastr-53 src]# tar -zxvf NETAPP_XCP_1.6.1.tgz
```
5. Download the license from https://xcp.netapp.com/license/xcp.xwic and copy to the XCP server.
6. Activate the license:
```
[root@mastr-53 linux]# ./xcp activate
[root@mastr-53 src]# cp license /opt/NetApp/xFiles/xcp/license
[root@mastr-53 src]# cd /usr/src/xcp/linux/
[root@mastr-53 linux]# ./xcp activate
```
7. Find the source NFS port and destination NFS server. The default port is 2049:
```
[root@mastr-53 ~]# rpcinfo -p 10.63.150.213
[root@mastr-53 ~]# rpcinfo -p 10.63.150.63
```
8. Check the NFS connection (both source and destination) using telnet to the NFS server port:
```
[root@mastr-53 ~]# telnet 10.63.150.127 2049
[root@mastr-53 ~]# telnet 10.63.150.63 2049
```
9. Configure the catalog:
   a. Create an NFS volume and export NFS for the XCP catalog (or leverage the OS NFS export):
   ```
   A800-Node1-2::> volume create -vserver Hadoop_SVM -volume xcpcatalog -aggregate aggr_Hadoop_1 -size 50GB -state online -junction-path /xcpcatalog -policy default -unix-permissions ---rwxr-xr-x -type RW -snapshot-policy default -foreground true
   A800-Node1-2::> volume mount -vserver Hadoop_SVM -volume xcpcatalog_vol -junction-path /xcpcatalog
   ```
   b. Check the NFS export:
   ```
   [root@mastr-53 ~]# showmount -e 10.63.150.63 | grep xcpca
   /xcpcatalog (everyone)
   ```
   c. Update `xcp.ini`:
   ```
   [root@mastr-53 ~]# cat /opt/NetApp/xFiles/xcp/xcp.ini
   # Sample xcp config
   [xcp]
   catalog = 10.63.150.64:/xcpcatalog
   ```
10. Find the source NAS exports using `xcp show` (look for `== NFS Exports ==` and `== Attributes of NFS Exports ==`):
```
[root@mastr-53 linux]# ./xcp show 10.63.150.127
```
11. (Optional) Scan the source NAS data:
```
[root@mastr-53 linux]# ./xcp scan -newid xcpscantest4 -stats 10.63.150.127:/xcpsrc_vol
```
    Scanning helps understand data layout and find potential migration issues. Scan time is proportional to file count and directory depth. Skip this step if you are familiar with your NAS data.
12. Check the report created by `xcp scan`, searching mainly for unreadable folders/files.
13. (Optional) Change inode counts based on the number of files to migrate, for both catalog and destination volumes:
```
A800-Node1-2::> volume show -volume xcpcatalog -fields files,files-used
A800-Node1-2::> volume show -volume xcpdest -fields files,files-used
A800-Node1-2::> volume modify -volume xcpcatalog -vserver A800-Node1_vs1 -files 2000000
```
14. Scan the destination volume:
```
[root@mastr-53 linux]# ./xcp scan -stats 10.63.150.63:/xcpdest
```
15. Check source and destination volume space:
```
[root@mastr-53 ~]# df -h /xcpsrc_vol
[root@mastr-53 ~]# df -h /xcpdest/
```
16. Copy the data from source to destination using `xcp copy` and check the summary:
```
[root@mastr-53 linux]# ./xcp copy -newid create_Sep091599198212 10.63.150.127:/xcpsrc_vol 10.63.150.63:/xcpdest
Stats       : 9.07M scanned, 9.07M copied, 118 linked, 9.07M indexed, 173 giants
Speed       : 1.57 TiB in (412 MiB/s), 1.50 TiB out (392 MiB/s)
Total Time  : 1h6m.
STATUS      : PASSED
```
    Note: By default, XCP creates seven parallel processes to copy data. This can be tuned.
    Note: NetApp recommends the source volume be read-only. `xcp copy` might fail because XCP does not support a live source that is continuously changed by an application.
    For Linux, XCP requires an Index ID because XCP Linux performs cataloging.
17. (Optional) Check inodes on the destination NetApp volume:
```
A800-Node1-2::> volume show -volume xcpdest -fields files,files-used
```
18. Perform the incremental update using `xcp sync`:
```
[root@mastr-53 linux]# ./xcp sync -id create_Sep091599198212
Stats       : 9.07M reviewed, 9.07M checked at source, no changes, 9.07M reindexed
Speed       : 1.73 GiB in (8.40 MiB/s), 1.98 GiB out (9.59 MiB/s)
Total Time  : 3m31s.
STATUS      : PASSED
```
    For Windows, XCP needs both source and destination paths.
19. Validate data transfer using `xcp verify`:
```
Xcp command : xcp verify 10.63.150.127:/xcpsrc_vol 10.63.150.63:/xcpdest
Stats       : 9.07M scanned, 9.07M indexed, 173 giants, 100% found (6.01M have data), 6.01M compared, 100% verified (data, attrs, mods)
Speed       : 3.13 TiB in (509 MiB/s), 11.1 GiB out (1.76 MiB/s)
Total Time  : 1h47m.
STATUS      : PASSED
```

Note: Windows customers copying data with ACLs should use `xcp copy -acl -fallbackuser<username> -fallbackgroup<username or groupname> <source> <destination>`. For SMB data accessible by both NFS and SMB, target must be an NTFS volume — copy via XCP NFS from Linux, then run XCP SMB sync with `-acl -nodata` from Windows to copy ACLs.

## Deployment steps - HDFS/MapRFS data migration

XCP supports Hadoop Filesystem Data Transfer to NAS, migrating data from HDFS/MapRFS to NFS and vice versa.

### Prerequisites

Perform this procedure as a non-root user (typically `hdfs`, `mapr`, or a user with HDFS/MapRFS permissions). Set these environment variables (CLI or `.bashrc`):

- `NHDFS_LIBHDFS_PATH` — points to `libhdfs.so` (HDFS APIs)
- `NHDFS_LIBJVM_PATH` — points to `libjvm.so` (shared JVM library in jre location)
- `CLASSPATH` — points to all jar files (`hadoop classpath --glob`)
- `LD_LIBRARY_PATH` — points to the Hadoop native library folder

Example (Cloudera cluster):
```
export CLASSPATH=$(hadoop classpath --glob)
export LD_LIBRARY_PATH=/usr/java/jdk1.8.0_181-cloudera/jre/lib/amd64/server/
export HADOOP_HOME=/opt/cloudera/parcels/CDH-6.3.4-1.cdh6.3.4.p0.6751098/
export NHDFS_LIBJVM_PATH=/usr/java/jdk1.8.0_181-cloudera/jre/lib/amd64/server/libjvm.so
export NHDFS_LIBHDFS_PATH=$HADOOP_HOME/lib64/libhdfs.so
```

This release supports XCP scan, copy, and verify operations and data migration from HDFS to NFS across single or multiple worker nodes. In the 1.8 release, both root and non-root users can perform data migration.

### Deployment steps - non-root user migrates HDFS/MapRFS data to NetApp NFS

1. Follow steps 1-9 from the NAS deployment section above.
2. Example: migrate data from HDFS to NFS.
   a. Create a folder and files in HDFS using `hadoop fs -copyFromLocal`.
   b. Check permissions in the HDFS folder (`hadoop fs -ls`).
   c. Create a folder in NFS and check permissions (`mkdir`, `ls -l`).
   d. Copy files from HDFS to NFS using XCP and check permissions:
   ```
   [root@n138 ~]# su - tester -c '/usr/src/hdfs_nightly/xcp/linux/xcp copy -chown hdfs:///tmp/testerfolder_src/util-linux-2.23.2/mohankarthikhdfs_src/ 10.63.150.126:/xcpsrc_vol/mohankarthiknfs_dest'
   Stats       : 3 scanned, 2 copied, 3 indexed
   Speed       : 3.44 KiB in (650/s), 80.2 KiB out (14.8 KiB/s)
   Total Time  : 5s.
   STATUS      : PASSED
   ```
