# ONTAP and application and database technical reports
Source: https://docs.netapp.com/us-en/ontap-technical-reports/apps-dbs.html
Fetched: 2026-07-07

Last updated: 04/17/2025

ONTAP is the foundation for data management and data protection for many enterprise application and database technologies. The following technical reports provide guidance on NetApp recommended practices and implementation procedures for Microsoft SQL Server, MySQL, Oracle, PostgreSQL, SAP HANA and Epic.

## Microsoft SQL Server

SQL Server is the foundation of Microsoft's data platform, delivering mission-critical performance with in-memory technologies and faster insights on any data, whether on the premises or in the cloud.

[Best practice for Microsoft SQL Server with ONTAP](https://docs.netapp.com/us-en/ontap-apps-dbs/mssql/mssql-overview.html)
Learn how storage administrators and database administrators can successfully deploy Microsoft SQL Server on ONTAP storage.
Note: Replaces previously published *TR-4590: Best practice guide for Microsoft SQL Server with ONTAP*.

[TR-4976: Virtualized Microsoft SQL Server performance on NetApp AFF A-Series and C-Series systems](https://www.netapp.com/pdf.html?item=/media/88704-tr-4976-virtualized-microsoft-sql-server-performance-on-netapp-aff-a-series-and-c-series.pdf)
Microsoft SQL Server performance characteristics using NetApp AFF A-Series and C-Series systems, and guidance on selecting the right system based on workload.

[TR-4714: Best practices for Microsoft SQL Server using SnapCenter](https://www.netapp.com/pdf.html?item=/media/12400-tr4714.pdf)
How to successfully deploy Microsoft SQL Server on ONTAP storage using SnapCenter technology for data protection.

## MySQL

Describes configuration requirements and guidance on tuning and storage configuration for deploying MySQL on ONTAP.

[MySQL database on NetApp ONTAP best practices](https://docs.netapp.com/us-en/ontap-apps-dbs/mysql/mysql-overview.html)
MySQL and its variants, including MariaDB and Percona, are widely used for many enterprise applications, ranging from global social networking sites and massive ecommerce systems to SMB hosting systems containing thousands of database instances.
Note: Replaces previously published *TR-4722: MySQL database on NetApp ONTAP best practices*.

## Oracle

ONTAP is designed for Oracle databases. For decades, ONTAP has been optimized for the unique demands of relational database I/O, and multiple ONTAP features were created specifically to service the needs of Oracle databases, even at the request of Oracle Inc. itself.

[Oracle databases on ONTAP](https://docs.netapp.com/us-en/ontap-apps-dbs/oracle/oracle-overview.html)
Recommended practices that enable storage administrators and database administrators to successfully deploy Oracle on ONTAP storage.

[Oracle data protection with ONTAP](https://docs.netapp.com/us-en/ontap-apps-dbs/oracle/oracle-dp-overview.html)
Recommended practices for backup, recovery, replication, and disaster recovery for Oracle on ONTAP storage.

[Oracle disaster recovery with ONTAP](https://docs.netapp.com/us-en/ontap-apps-dbs/oracle/oracle-dr-overview.html)
Recommended practices, test procedures, and other considerations for operating Oracle databases on a MetroCluster and SnapMirror Business Continuity.

[Migration of Oracle databases to ONTAP storage systems](https://docs.netapp.com/us-en/ontap-apps-dbs/oracle/oracle-migration-overview.html)
Overall considerations for planning a migration strategy, the three different levels at which data movement takes place, and details of the various procedures available.

Note: The four Oracle links above replace previously published *TR-3633: Oracle databases on ONTAP*; *TR-4591: Oracle data protection: backup, recovery, replication*; *TR-4592: Oracle on MetroCluster*; and *TR-4534: Migration of Oracle databases to NetApp storage systems*.

[TR-4969: Oracle database performance on AFF A-Series and C-Series](https://www.netapp.com/pdf.html?item=/media/85630-tr-4969.pdf)
ONTAP is a powerful data-management platform with native capabilities including inline compression, nondisruptive hardware upgrades, and the ability to import a LUN from a foreign storage array. Up to 24 nodes can be clustered together, simultaneously serving data through NFS, SMB, iSCSI, FC, and NVMe protocols, with Snapshot technology as the basis for tens of thousands of online backups and fully operational database clones. Covers bare metal database performance on AFF A-Series and C-Series, including maximums and the practical differences between the two options.

[TR-4971: Virtualized Oracle database performance on AFF A-Series and C-Series](https://www.netapp.com/pdf.html?item=/media/85629-tr-4971.pdf)
Same platform capabilities as above, covering virtualized database performance using AFF A-Series and C-Series, including maximums and practical differences between the two options.

[TR-4695: Database storage tiering with FabricPool](https://www.netapp.com/pdf.html?item=/media/9138-tr4695.pdf)
Benefits and configuration options of FabricPool with various databases, including the Oracle RDBMS.

[TR-4899: Oracle database transparent application failover with SnapMirror active sync](https://www.netapp.com/pdf.html?item=/media/40384-tr-4899.pdf)
SnapMirror active sync (formerly SM-BC) and Oracle Real Application Cluster (RAC) can provide transparent application failover (TAF) and continuity in the face of site outages and true disasters. Configuration guidance and recommended practices for an AFF storage array with SnapMirror active sync as the storage component of Oracle RAC.

[TR-4876: Oracle Multitenancy with ONTAP solution and deployment best practices](https://www.netapp.com/pdf.html?item=/media/21901-tr-4876.pdf)
Recommended practices for provisioning, managing, and protecting Oracle Multitenant databases using ONTAP storage to maximize the benefits of both Oracle Multitenant databases and ONTAP software features.

## PostgreSQL

PostgreSQL variants include PostgreSQL, PostgreSQL Plus, and EDB Postgres Advanced Server (EPAS). PostgreSQL is typically deployed as the back-end database for multitier applications. NetApp ONTAP is an excellent choice for running PostgreSQL databases due to its reliability, high performance, and efficient data management capabilities.

[PostgreSQL database on ONTAP best practices](https://docs.netapp.com/us-en/ontap-apps-dbs/postgres/postgres-overview.html)
Supported by common middleware packages (PHP, Java, Python, Tcl/Tk, ODBC, JDBC) and historically a popular open-source database choice. Configuration requirements and guidance on tuning and storage configuration for deploying PostgreSQL on ONTAP.
Note: Replaces previously published *TR-4770: PostgreSQL database on ONTAP best practices*.

## SAP HANA

[SAP HANA database solutions on ONTAP](https://docs.netapp.com/us-en/netapp-solutions-sap/)
Best practices for configuring, managing, and automating SAP solutions — see the NetApp SAP Solutions page.

## Epic

[Epic on ONTAP best practices](https://docs.netapp.com/us-en/ontap-apps-dbs/epic/epic-overview.html)
Best practices for deploying Epic on premises and in the cloud while meeting configuration standards for proper deployment on ONTAP.
Note: Replaces previously published *TR-3923: NetApp best practices for Epic*.

## Downloadable reference

- [PDF of this doc site](https://docs.netapp.com/us-en/ontap-technical-reports/pdfs/fullsite-sidebar/NetApp_Technical_Reports.pdf)
