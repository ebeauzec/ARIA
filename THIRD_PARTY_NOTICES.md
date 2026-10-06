# Third-party notices

ARIA is proprietary software (see [LICENSE](LICENSE) and [LEGAL.md](LEGAL.md)). It includes or depends on the
open-source components below. Each remains under its own licence, which is not changed by ARIA's licence.
Full licence texts are in the upstream projects and, where a package ships them, in the `*.dist-info` folders
under `dist/ARIA/_internal/`.

## Browser libraries (vendored in the repository root)

| Component | Version | Licence | Source |
|---|---|---|---|
| Chart.js | 4.5.1 | MIT (copyright Chart.js Contributors) | https://www.chartjs.org |
| PptxGenJS (with the JSZip it bundles) | 4.0.1 | MIT; JSZip is MIT or GPL-3.0-or-later, used here under MIT | https://gitbrent.github.io/PptxGenJS/ , https://stuk.github.io/jszip/ |

## Windows application bundle (`dist/`, built with PyInstaller)

| Component | Version | Licence |
|---|---|---|
| Python runtime and standard library | 3.12 | Python Software Foundation License |
| PyInstaller bootloader | 6.21 | GPL-2.0-or-later with the PyInstaller bootloader exception (permits bundling in any application) |
| pywebview | 6.2.1 | BSD-3-Clause |
| pythonnet | 3.1.0 | MIT |
| clr-loader | 0.3.1 | MIT |
| proxy_tools | 0.1.0 | MIT |
| bottle | 0.13.4 | MIT |
| cryptography | 50.0.0 | Apache-2.0 or BSD-3-Clause |
| cffi | 2.1.0 | MIT-0 |
| pycparser | 3.0 | BSD-3-Clause |
| bcrypt | bundled | Apache-2.0 |
| pyreadline3 | 3.5.6 | BSD |
| pywin32 | 312 | PSF |
| typing_extensions | 4.16.0 | PSF-2.0 |
| setuptools | bundled | MIT |
| Microsoft Visual C++ runtime (`VCRUNTIME140*.dll`, `MSVCP140*.dll`) | 14.x | Microsoft Visual C++ Redistributable terms |

## Data and trademarks

* "NetApp", "Active IQ", "ONTAP", "StorageGRID", "SANtricity" and related names are trademarks of NetApp, Inc.
  ARIA is an independent tool and is not affiliated with, endorsed by or sponsored by NetApp, Inc.
* `data/` holds reference data compiled from public sources (NetApp documentation and security advisories, the
  CISA Known Exploited Vulnerabilities catalogue, and similar). Those sources keep their own terms; check them before
  redistributing the data outside your organisation.
* Customer data read through the Active IQ API stays on the machine that runs ARIA and is not part of this repository.

## API reference

The Active IQ GraphQL schema reference used to check `api_queries.json` is the public Apollo GraphOS Studio variant ActiveIQ-Graph-Prd-API (`current`). It is read only by `tools/validate_api_queries.py` when you run it; no copy of the schema is stored in this repository. Apollo, GraphQL and Active IQ are trademarks of their respective owners.

## Data sources

ARIA ships no third-party data. At run time it reads the user's own Active IQ account and public sources; the list is in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md). Each source's own terms of use apply to that use.
