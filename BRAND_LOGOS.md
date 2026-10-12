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

Beta.2 bundles only the six sanitized SVG assets listed below. They are
installed with the integration and served locally from
`/mobile_fuel_stations/logos/`; no logo request is made to a CDN at runtime.

The package is an independent, free Home Assistant integration. It is not
endorsed by, affiliated with, or sponsored by any displayed station brand.
The rights assessment below separates copyright/licensing from trademark
rights. Public-domain or CC0 treatment does not grant permission to imply
endorsement or partnership.

| Key | Brand | File | Source | Rights assessment | Attribution | SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| `aral` | Aral | `frontend/logos/aral.svg` | [Simple Icons source metadata](https://github.com/simple-icons/simple-icons/blob/dc7b10662a0a2cfdfc9305e2a2b06c023c30724a/data/simple-icons.json), [Commons file](https://commons.wikimedia.org/wiki/File:Aral_Logo.svg) | Simple Icons repository CC0; source Commons page claims public domain, with trademark warning. Current visual match is acceptable; legal trademark risk remains. | No CC0 attribution required; source retained for audit. | `c144c9cf303e15d1addc4ca45736c99508cfb68aabef07f09feb80bf0f21b76c` |
| `jet` | JET | `frontend/logos/jet.svg` | [Simple Icons source metadata](https://github.com/simple-icons/simple-icons/blob/dc7b10662a0a2cfdfc9305e2a2b06c023c30724a/data/simple-icons.json), [JET source reference](https://de.wikipedia.org/wiki/Datei:JET.svg) | Simple Icons repository CC0; source and trademark status are retained as residual-risk items. Included only for factual station identification. | No CC0 attribution required; source retained for audit. | `83259f9ef037ad0449e2539eef9ff25c2b4eda222e01c87657de7bbb5b0e3d1f` |
| `shell` | Shell | `frontend/logos/shell.svg` | [Simple Icons source metadata](https://github.com/simple-icons/simple-icons/blob/dc7b10662a0a2cfdfc9305e2a2b06c023c30724a/data/simple-icons.json), [Shell source reference](https://en.wikipedia.org/wiki/File:Shell_logo.svg) | Simple Icons repository CC0; Shell trademark remains protected. The asset is used only as a factual brand identifier and does not include endorsement language. | No CC0 attribution required; source retained for audit. | `d3a4b69b3437e4e94ac7a974c2d3b9780a57cdbf82ff57e2f2558fb38d03d7cf` |
| `omv` | OMV | `frontend/logos/omv.svg` | [Commons file OMV Logo 2024](https://commons.wikimedia.org/wiki/File:OMV_Logo_2024.svg) | Commons page claims public domain for simple logo geometry and identifies OMV AG as author/source; trademark warning remains. Current 2024 artwork. | No attribution required by the page's PD claim; source link retained. | `b5d8b7f4f844698bdf0e35dae13416558c6c49cc92d326f16a210d1633615051` |
| `orlen` | ORLEN | `frontend/logos/orlen.svg` | [Commons file ORLEN wordmark](https://commons.wikimedia.org/wiki/File:Orlen_wordmark_logo.svg) | Commons page claims public domain for simple geometry and identifies ORLEN SA as source; wordmark is older (2000) and trademark risk remains. Included as a conservative wordmark, not a claim of current corporate approval. | No attribution required by the page's PD claim; source link retained. | `467eb4cec9e954944d6506282e839a174ba36bbeef39775373776d08d2abe812` |
| `total` | TotalEnergies | `frontend/logos/total.svg` | [Commons file TotalEnergies wordmark 2021-present](https://commons.wikimedia.org/wiki/File:TotalEnergies_wordmark_(2021-present).svg) | Commons page claims public domain for simple geometry and identifies TotalEnergies SE as author/source; current wordmark is suitable, but trademark risk remains. | No attribution required by the page's PD claim; source link retained. | `4bf2adc55ed00194bfdf3aab6e9d85f691cc5b76dd483a52aa40a1b92a24a4be` |

## Technical safety

Every bundled file is parsed as XML during the test suite. The asset test
rejects scripts, foreign objects, frames, embeds, images, animations, external
URLs, and external SVG references. The files contain only static vector data
and local SVG fragments.

## Fallback and overrides

The bundled set is deliberately incomplete. Esso, HEM, AVIA, Q1, Raiffeisen,
OIL!, star, BFT, Westfalen and other unresolved provider values use the pump
fallback until a matching current asset and documented rights basis are found.
Users may still configure their own local `logo_path`; explicit user logos
take priority over bundled files. `show_brand_logos: false` always disables
logo rendering.
