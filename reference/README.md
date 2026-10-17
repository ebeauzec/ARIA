# reference/

`netapp-library/` is the NetApp Reference Library that ships with ARIA: markdown digests and indexes of NetApp's publicly available documentation (ONTAP, StorageGRID, SANtricity, data protection, security hardening, hardware, integrations and more). Every page names its source URL and the date it was read. ARIA searches it from Settings > Data & Sync, uses the sources it lists as the pages its reference updater watches, and draws on it for remediation procedures and the reference tables.

* **No setup.** ARIA finds this copy by itself. A library the user points to (Settings > Data & Sync, or `ARIA_LIBRARY_PATH`) or one found in the usual cloud-storage folders is used instead when present, because something maintains it.
* **Do not edit these files by hand.** The copy is produced by `python tools/dev/sync_library.py`, which also leaves out the maintenance log, failed-fetch lists and e-mail addresses. Refresh it with that script and release.
* **Attribution.** The content summarises or reproduces NetApp product documentation published at docs.netapp.com, kb.netapp.com, security.netapp.com and netapp.com. It belongs to NetApp, which is not affiliated with ARIA; follow the source link on each page for the authoritative, current text. Use it as a reference, not as a substitute for the documentation for the release you run.
* **Contains no customer data.** The digests come from public pages; the sync script and the repository's sensitive-data guard check the copy before it can be committed.
