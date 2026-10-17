# Configure SRA on the VMware Live Site Recovery appliance using ONTAP tools
Source: https://docs.netapp.com/us-en/ontap-tools-vmware-vsphere-10/protect/configure-on-srm-appliance.html
Fetched: 2026-07-07

After deploying the VMware Live Site Recovery appliance, configure the Storage Replication Adapter (SRA) to enable disaster recovery management.

Configuring SRA on the VMware Live Site Recovery appliance saves the ONTAP tools for VMware vSphere credentials within the appliance, enabling communication between VMware Live Site Recovery and SRA.

## Before you begin

- Download the `.tar.gz` file from the NetApp Support Site (product: otv10, Downloads tab).
- Enable SRA services in ONTAP tools Manager (see "Enable services").
- Add vCenter Servers to the ONTAP tools for VMware vSphere appliance (see "Add vCenter Servers").
- Add storage backends to ONTAP tools for VMware vSphere (see "Add storage backends").

> **Note:** If you applied the vCenter certificate patch from ONTAP tools, update the vCenter configuration in the VMware Live Site Recovery appliance using the `:5480` port. See "Reconfigure the Site Recovery Manager Appliance" (Broadcom/VMware docs).

## Steps

1. On the VMware Live Site Recovery appliance screen, select **Storage Replication Adapter** > **New Adapter**.
2. Upload the `.tar.gz` file to VMware Live Site Recovery.
3. Log in to the VMware Live Site Recovery appliance as administrator via an SSH client (e.g., PuTTY).
4. Switch to root: `su root`
5. Go to the log directory: `cd /var/log/vmware/srm`
6. Get the Docker ID used by SRA: `docker ps -l`
7. Log in to the container: `docker exec -it -u srm <container id> sh`
8. Configure VMware Live Site Recovery with the ONTAP tools IP and password:
   ```
   perl command.pl -I --otv-ip <OTV_IP>:8443 --otv-username <Application username> --otv-password <Application password> --vcenter-guid <VCENTER_GUID>
   ```
   - Provide the password in single quotes so special characters are treated as part of the password, not delimiters.
   - Set the application (VASA Provider/SRA) username/password in ONTAP tools Manager when first enabling these services; use those credentials to register SRA with VMware Live Site Recovery.
   - Find the vCenter GUID on the vCenter Server page in ONTAP tools Manager after adding the vCenter instance (see "Add vCenter Servers").
9. Rescan the adapters to confirm updated details appear on the VMware Live Site Recovery Storage Replication Adapters page.

**Result:** A confirmation message indicates storage credentials have been saved. SRA can now communicate with the SRA server using the specified IP address, port, and credentials.

*(Product: ONTAP tools for VMware vSphere 10, version 10.5; also applies to 10.4/10.3/10.2/10.1/10.0 with version-specific URLs. Page last updated: 03/27/2026)*
