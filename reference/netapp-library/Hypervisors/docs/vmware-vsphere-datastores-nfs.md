# NFS
Source: https://docs.netapp.com/us-en/ontap-apps-dbs/vmware/vmware-vsphere-datastores-nfs.html
Fetched: 2026-07-07

ONTAP is, among many other things, an enterprise-class scale-out NAS array. ONTAP empowers VMware vSphere with concurrent access to NFS-connected datastores from many ESXi hosts, far exceeding the limits imposed on VMFS file systems. Using NFS with vSphere provides ease-of-use and storage-efficiency-visibility benefits (see the datastore overview page).

## Best practices

- **Use ONTAP tools for VMware vSphere** (the most important best practice):
  - Provision datastores with the plug-in — it automatically simplifies export-policy management.
  - When creating datastores for VMware clusters, select the cluster rather than a single ESX server so the datastore auto-mounts to all cluster hosts.
  - Use the plug-in's mount function to apply existing datastores to new servers.
  - When not using ONTAP tools, use a single export policy for all servers, or per cluster where additional access control is needed.
- Use a single LIF per SVM per ONTAP cluster node. The older recommendation of one LIF per datastore is no longer necessary — direct access (LIF and datastore on the same node) is best, but indirect access has minimal (microsecond) performance impact.
- If using fpolicy, exclude `.lck` files — used by vSphere for locking when a VM is powered on.
- All currently supported vSphere versions support NFS v3 and v4.1. Official nconnect support was added in vSphere 8.0 U2 (NFS v3) and U3 (NFS v4.1). NFS v4.1 also supports session trunking, Kerberos authentication, and Kerberos with integrity. Session trunking requires ONTAP 9.14.1 or later.

> **Tip:** Max nconnect value in vSphere 8 is 4 (default 1); can be raised per-host via advanced settings (rarely needed). Use 4 for higher performance than a single TCP connection allows. ESXi has a 256 NFS-connection limit, and each nconnect connection counts toward it (e.g., two datastores with nconnect=4 = 8 total connections). Test nconnect performance impact before production rollout.

- NFSv3 uses client-side locking; NFSv4.1 uses server-side locking. A volume can be exported through both protocols, but a given ESXi datastore mount uses only one protocol version — other hosts can mount the same datastore via a different version, but **never mix NFS versions across hosts accessing the same datastore**. Specify the protocol version explicitly at mount time; use host profiles to check compliance.
  - No automatic NFSv3-to-v4.1 conversion — create a new v4.1 datastore and Storage vMotion VMs over.
  - See the NFS v4.1 Interoperability table in the NetApp IMT for required ESXi patch levels.
- If not using vSphere CSI for Kubernetes, set `newSyncInterval` per VMware KB 386364.
- NFS export policy rules control vSphere host access — one policy can cover multiple volumes/datastores. ESXi uses `sys` (UNIX) security style and requires the root mount option (ONTAP: `superuser`) to run VMs; when superuser is used, no need to specify anon user ID. Export policy rules with differing `-anon`/`-allow-suid` values can cause SVM discovery problems with ONTAP tools. Client match should be a comma-separated list (no spaces) of vmkernel port IPs.

  Sample datastore volume export policy rule:
  - Access Protocol: nfs (includes nfs3 and nfs4)
  - Client Match: 192.168.42.21,192.168.42.22
  - RO Access Rule: any
  - RW Access Rule: any
  - Anonymous UID: 65534
  - Superuser: any
  - Honor SetUID Bits in SETATTR: true
  - Allow Creation of Devices: true

- If using the NetApp NFS Plug-In for VMware VAAI, set the export policy rule protocol to `nfs` (covers both v3 and v4 even if the datastore itself is created as NFS v3) — NFSv4 is required for VAAI copy offload to function.
- NFS datastore volumes are junctioned from the SVM root volume, so ESXi needs read-only access to the root volume (and any intermediate volumes in the junction path) to navigate and mount datastores.

  Sample root volume export policy rule (with VAAI plug-in):
  - Access Protocol: nfs
  - Client Match: 192.168.42.21,192.168.42.22
  - RO Access Rule: sys
  - RW Access Rule: never (best security for root volume)
  - Superuser: sys (also required for root volume with VAAI)

- Although ONTAP supports a flexible junctioned volume namespace, this has no value for vSphere — each VM gets a directory at the datastore root regardless of storage namespace hierarchy. Best practice: mount datastore volumes' junctions at the SVM root volume (how ONTAP tools provisions them). This avoids nested-junction dependency — taking one volume offline/destroying it doesn't affect paths to others.
- A 4K block size is fine for NTFS partitions on NFS datastores.

## NFS version feature support

| vSphere Feature | NFSv3 | NFSv4.1 |
| --- | --- | --- |
| vMotion and Storage vMotion | Yes | Yes |
| High availability | Yes | Yes |
| Fault tolerance | Yes | Yes |
| DRS | Yes | Yes |
| Host profiles | Yes | Yes |
| Storage DRS | Yes | No |
| Storage I/O control | Yes | No |
| SRM | Yes | No |
| Virtual volumes | Yes | No |
| Hardware acceleration (VAAI) | Yes | Yes |
| Kerberos authentication | No | Yes (enhanced in vSphere 6.5+ for AES, krb5i) |
| Multipathing support | No | Yes (requires ONTAP 9.14.1) |

*Page last updated: 03/18/2026*
