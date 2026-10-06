# data/

Locally generated reference data (firmware baselines, advisory database, interop matrix, hardware documentation, demo data, caches). ARIA builds these files on first run or sync from your own Active IQ account and public sources. They are not part of the repository (see `.gitignore`).

`reference_library.js` (optional) supplies `window.ARIA_REF`; without it ARIA runs with empty reference tables.
