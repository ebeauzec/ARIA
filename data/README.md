# data/

Locally generated reference data (firmware baselines, advisory database, interop matrix, hardware documentation, demo data, caches). ARIA builds these files on first run or sync from your own Active IQ account and public sources. They are not part of the repository (see `.gitignore`).

`reference_library.js` (optional) supplies `window.ARIA_REF`; without it ARIA runs with empty reference tables.

The reference updater keeps its state here too: `library_update_state.json`, `library_update_report.json`, `library_update_queue.json` (the review queue shown in Settings) and `library_refreshed/` (a copy of each page it read). The page list it reads ships in `tools/library_sources.json`, outside this folder.
