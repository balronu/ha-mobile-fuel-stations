# Bundled station-brand logos

## Factual trademark identification

Mobile Fuel Stations is an independent open-source project and has no
commercial relationship with the displayed station brands.

Brand names and marks are shown solely to identify the relevant station and
to make fuel-price information understandable. Factual identification may be
permitted under the applicable conditions of § 23(1)(3) and § 23(2) MarkenG,
but this wording is not a legal opinion or a blanket permission.

All brands and designations belong to their respective owners. Copyright and
redistribution rights for each concrete image file are assessed separately
and documented below. A trademark disclaimer does not replace a missing image
license.

Stable v0.7.0 bundles 60 normalized PNG assets from the supplied archive. They
are installed with the integration and served locally from
`/mobile_fuel_stations/logos/`; no logo request is made to a CDN at runtime.

The archive files were matched to the exact
[reference directory](https://github.com/timmaurice/lovelace-tankerkoenig-card/tree/main/src/gasstation_logos)
in the upstream Tankerkönig card repository. That repository is MIT-licensed
as a code repository, but provides no separate per-image license or trademark
permission. For this branch, the repository owner explicitly authorized use of
the supplied archive. That authorization is the documented redistribution
basis for these stable assets; it is not a trademark license, endorsement, or
affiliation claim. Residual rights and trademark risk remain.

The package is an independent, free Home Assistant integration. It is not
endorsed by, affiliated with, or sponsored by any displayed station brand.
The rights assessment below separates copyright/licensing from trademark
rights. Public-domain or CC0 treatment does not grant permission to imply
endorsement or partnership.

| Key | Brand | File | Source | Rights assessment | Attribution | SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| `aral` | Aral | `frontend/logos/aral.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `b835b987fb336cbf4c0f84152768ea4e587b313b60a0840c8e69bdcdbfd053cc` |
| `jet` | JET | `frontend/logos/jet.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `e43dd03577d4545e567750837a47ca1a23274d396ba2bb60cea9d3400af541b5` |
| `shell` | Shell | `frontend/logos/shell.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `d42eb4185143e11f73100c91d4f18f22caa1402150ffb4db31586f2f7e1f9ca1` |
| `omv` | OMV | `frontend/logos/omv.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `e2af0ffdea92d304d9a44c9d4a7d1b7ddb5b4f7a5b7ab3efeb193b2024586a16` |
| `orlen` | ORLEN | `frontend/logos/orlen.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `2c683bd01e7ac799f6970bfced43f34d47204e8d27ac2e497f8c0b1541edfccd` |
| `total` | Total / TotalEnergies | `frontend/logos/total.png` | Supplied `gasstation_logos.zip`, matched to the upstream Tankerkönig reference directory | Archive has no per-image license; explicit branch-level authorization is the redistribution basis, with residual trademark risk. | Source archive and upstream reference retained for audit. | `fd3f6ba4420830aab54ff2c959c0f82ccee2b1420a2ec4130275cf5feb9652fa` |

## Technical safety

Every bundled PNG is decoded and checked during the test suite for a valid
image header, dimensions, alpha handling, and safe local packaging. The
original image pixels are not edited; files that were technically JPEGs with a
`.png` name were decoded and re-encoded as PNG before publication. No external
URLs or runtime image requests are used.

## Fallback and overrides

The bundled set covers the normalized archive brands as local PNGs. The excluded generic `404.png`/`svg.png` files, unknown
brands, and failed local assets use the neutral pump fallback. Users may still
configure their own local `logo_path`; explicit user logos take priority
over bundled files. `show_brand_logos: false` always disables logo rendering.
