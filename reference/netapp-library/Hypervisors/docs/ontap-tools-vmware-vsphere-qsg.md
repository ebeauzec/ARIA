# ONTAP tools for VMware vSphere Quick Start
Source: https://docs.netapp.com/us-en/ontap-tools-vmware-vsphere/qsg.html
Fetched: 2026-07-07

ONTAP tools for VMware vSphere is a single vCenter Server plug-in that includes ONTAP tools, VASA Provider, and Storage Replication Adapter (SRA) extensions. It's recommended for all ONTAP vSphere environments — it configures ESXi host settings and provisions ONTAP storage using best practices. VASA Provider is required for vVols support; SRA works with VMware Site Recovery Manager.

## Preparing for installation

Deployed as a virtual appliance, reducing the effort of installing/registering each product separately with vCenter Server.

### Deployment requirements

Usable with a VMware vCenter Server Virtual Appliance (vCSA); must be deployed on a supported vSphere/ESXi system.

**Minimum space and host sizing:**

| System | Minimum requirements |
| --- | --- |
| Space | 2.1 GB (thin provisioned) / 54.0 GB (thick provisioned) |
| Host sizing | Recommended memory: 12 GB; Recommended CPUs: 2 |

**Licenses:**

| License | Description |
| --- | --- |
| SnapMirror | (Optional) Required for failover operations for SRA and VASA Provider if using vVols replication. |
| FlexClone | (Optional) Required for test failover operations (SRA) and for vVols operations of VASA Provider. |

**Default bidirectional TCP ports used by ONTAP tools:**

| Port | Description |
| --- | --- |
| 9083 | Used by both VASA Provider and SRA to communicate with vCenter Server (also for TCP/IP settings). Must be enabled on the firewall from ESXi hosts to the ONTAP tools appliance. Used to download the VP support bundle, access the Web-CLI UI, and control-path communication from VMware to VP. |
| 443 | Used for secure communications between vCenter Server/storage systems and any REST API automation client. Enabled by default. |
| 8143 | ONTAP tools secure communications port for client-server (REST API) architecture; used for exporting ONTAP tools server logs and hosting the register.html page; REST swagger exposed here. |
| 8443 | Used for the ONTAP tools for VMware vSphere plugin service. |

**Minimum storage/application version requirements:**

| Component | Version requirement |
| --- | --- |
| ONTAP | 9.7, 9.8P1, or later |
| VMware vSphere, vCenter Server, ESXi hosts, SRM, plug-ins, databases | See the Interoperability Matrix Tool (IMT) |

**ONTAP tools requirements checklist:**
- Configure and set up your vCenter Server environment.
- Download the `.ova` file.
- Have vCenter Server login credentials ready.
- Delete browser cache to avoid caching issues during deployment.
- Configure the default gateway used by the virtual appliance to respond to ICMP pings.
- Have a valid DNS hostname for the virtual appliance.

**Optional requirements for SRA:** if deploying for use with VMware Site Recovery Manager, download the `.tar.gz` file for SRA (if using the SRM appliance).

## Deploying ONTAP tools

1. Download the `.zip` file (binaries + signed certificates) from the NetApp Support Site to a vSphere Client system.
2. Extract the `.zip` and deploy the `.ova` file. **Deploy the `.ova` on both source and destination sites if deploying SRA.**
3. Log in to the vSphere Web Client: Home > Host and Clusters.
4. Right-click the required datacenter > Deploy OVF template.
   - Optional integrity check for vCenter 7.0u3e and later (verifies the OVA binary wasn't tampered with):
     - Download `OTV_INTER_ROOT_CERT_CHAIN.pem` from the NetApp Support Site.
     - Navigate to vCenter > Administration > Certificate Management.
     - Click "Add trusted root certificate" > Browse to the `.pem` file > Add.
     - A message reading "Entrust Code Signing - OVCS2 (Trusted certificate)" confirms integrity. If it instead shows "(Invalid certificate)", upgrade vCenter Server to 7.0U3E or later.
5. Enter the `.ova` file's URL, or browse to its folder, then click Next.
6. Enter the required details to complete the deployment.

> **Note:** To create containers without registering to vCenter Server, select the **Enable VMware Cloud Foundation (VCF)** checkbox in the Configure vCenter or Enable VCF section.

Monitor deployment progress in the Tasks tab. Checksum verifications run as part of deployment. If deployment fails:
1. Check `vpserver/logs/checksum.log` — "checksum verification failed" indicates which jar failed verification (log contains output of `sha256sum -c /opt/netapp/vpserver/conf/checksums`).
2. Check `vscserver/log/checksum.log` similarly (log contains output of `sha256sum -c /opt/netapp/vscerver/etc/checksums`).

## Deploying SRA on SRM

SRA can be deployed on a Windows SRM server or on the 8.2 SRM Appliance.

### Uploading and configuring SRA on the SRM Appliance

1. Download the `.tar.gz` file from the NetApp Support Site.
2. On the SRM Appliance screen: Storage Replication Adapter > New Adapter.
3. Upload the `.tar.gz` file to SRM.
4. Rescan the adapters to confirm details appear on the SRM Storage Replication Adapters page.
5. Log in to the SRM Appliance as administrator via PuTTY.
6. Switch to root: `su root`
7. Get the SRA docker container ID: `docker ps -l`
8. Enter the container: `docker exec -it -u srm <container id> sh`
9. Configure SRM with the ONTAP tools IP and password:
   `perl command.pl -I <otv-IP> administrator '<otv-password>'`
   (single quotes required around the password value). A success message confirms storage credentials were stored; SRA can then communicate with the ONTAP tools server via the given IP, port, and credentials.

### Updating SRA credentials

1. Delete the SRA config directory contents:
   ```
   cd /srm/sra/conf
   rm -rf *
   ```
2. Reconfigure with new credentials:
   ```
   cd /srm/sra/
   perl command.pl -I <otv-IP> administrator '<otv-password>'
   ```
   (single quotes required around the password value.)

## Enabling VASA Provider and SRA

1. Log in to the vSphere web client using the vCenter IP provided during OVA deployment.
2. On the shortcuts page, click **NetApp ONTAP tools** under Plug-ins.
3. In the left pane: Settings > Administrative Settings > Manage Capabilities — enable the required capabilities.
   > **Note:** VASA Provider is enabled by default. To use vVols datastore replication, use the **Enable vVols replication** toggle.
4. Enter the ONTAP tools for VMware vSphere IP address and administrator password, then click **Apply**.

*(Product version referenced: ONTAP tools for VMware vSphere 9.13)*
