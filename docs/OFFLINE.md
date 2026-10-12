# Working without Active IQ (offline and dark-site use)

Some customers do not send AutoSupport to NetApp's cloud, so Active IQ has nothing to show for them. ARIA can still build a picture of such a system from an
AutoSupport bundle that the customer exports and hands over. No connection to Active IQ or to the internet is needed for the import itself, and no AI is involved.

## How to use it

1. Get an AutoSupport bundle from the customer (a `.7z`, `.tgz`, `.zip`, `.xml.gz` or `.xml` file).
2. In ARIA, open the Import / Export menu and choose **Import ASUP Bundle**.
3. The system appears with the others. Each import records which parts of the system the bundle covered, and the import list shows it.

## What the importer reads

`tools/asup_parser.py` reads these parts of a bundle when they are present: cluster information, ONTAP version, aggregate status and space (`aggr-status`, `aggr-info`, `df`),
hardware configuration (`sysconfig`), SnapMirror status, AutoSupport settings, HA / storage failover state, licenses (`licenses.xml`, including demo and expired licenses) and
storage shelves. A bundle that lacks a part simply leaves that part out; the import says what it found.

## What it does not give you

- Active IQ's own analysis: its risk engine, health score, support cases, contract data and recommendations come from Active IQ's cloud. A bundle does not carry them, so
  imported systems do not have them. ARIA's own checks that need only configuration facts (for example firmware and release currency against NetApp's published baselines) can
  still apply where the bundle holds the inputs.
- Anything the customer left out of the bundle, or that the bundle's AutoSupport level does not collect.

Treat an imported system as a configuration snapshot at the date of the bundle, not as a live view. Import a newer bundle to refresh it.

## When to prefer it

- The customer cannot or will not enable AutoSupport to NetApp.
- A site is isolated (secure, air-gapped or regulated) and the bundle is carried out by hand.
- Active IQ is unreachable for a while and a snapshot is still needed for a review.
