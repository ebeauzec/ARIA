# Configure SRA with SRM in a Shared recovery site configuration
Source: https://docs.netapp.com/us-en/ontap-tools-vmware-vsphere/protect/configure_sra_with_srm_shared_site.html
Fetched: 2026-07-07

ONTAP tools for VMware vSphere supports VMware's SRM Shared Recovery Site Configuration. See VMware's "Site Recovery Manager in a Shared Recovery Site Configuration" documentation for background. In this configuration, the Site Recovery Manager Server instances on the recovery site connect to the same vCenter Server instances.

In a SRM Shared Recovery Site Configuration, each SRM server needs a dedicated SRA instance — there is a 1:1 relationship between SRM and SRA. Configure ONTAP tools for VMware vSphere (OTV) in VCF mode to act as a dedicated SRA instance for each SRM server. You can also deploy a non-SRA-enabled ONTAP tools appliance registered with vCenter for non-SRA tasks such as datastore provisioning.

Refer to the NetApp Knowledge Base article "How to configure SRA in a SRM Shared Recovery Site" for the detailed setup procedure.

*(Product: ONTAP tools for VMware vSphere 9.13)*
