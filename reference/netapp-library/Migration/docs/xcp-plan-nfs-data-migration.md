# Plan NFS data migration
Source: https://docs.netapp.com/us-en/xcp/xcp-plan-nfs-data-migration.html
Fetched: 2026-07-07

Plan your NFS data migrations.

## show

The `show` command queries the RPC services and NFS exports of one or more storage servers. The command lists the available services and exports with the used and free capacity of each export, followed by the root attributes of each export.

Example:
```
xcp show <NFS file server IP/FQDN>
xcp show nfs_server01.netapp.com
```

Run `xcp help show` for more details.

## scan

The `scan` command recursively scans the entire source NFSv3 exported paths and prints the statistics of file structure at the end of the scan. NetApp recommends putting the source NFS export mounts in read-only mode during the scan operation.

Note: If a file or directory name contains non-UTF-8 characters, these characters are converted to the UTF-8 format and displayed when you run the `xcp scan` command. Depending on the translation from the source encoding to UTF-8, the characters might not display as expected.

Example:
```
xcp scan NFS [server:/export path | file:// ]
xcp scan nfs_server01.netapp.com:/export1
xcp scan file:///mnt/nfs-source
```

Run `xcp help scan` for more details.

Optionally, use File Analytics to view the results graphically.
