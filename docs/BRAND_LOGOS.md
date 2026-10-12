# Brand logos

v0.6.0-beta.1 adds provider-independent brand resolution without bundling
third-party logo artwork. The implementation is original code and maps the
station's existing `brand` attribute to a canonical local filename.

## Rights boundary

The referenced Tankerkönig cards are MIT-licensed for their code. That does not
prove that their logo image files are freely reusable or that a trademark owner
has granted redistribution rights. This repository therefore ships no fuel
station brand artwork. Users are responsible for the rights to files placed in
`/config/www/fuel-logos/`.

## Supported aliases

| Brand values | Local filename |
| --- | --- |
| Aral | `aral.png` |
| Shell | `shell.png` |
| Esso | `esso.png` |
| JET | `jet.png` |
| Total, TotalEnergies | `total.png` |
| HEM | `hem.png` |
| AVIA, AVIA Express | `avia.png` |
| ORLEN, ORLEN Express | `orlen.png` |
| OMV | `omv.png` |
| Q1, Q 1 | `q1.png` |
| Raiffeisen | `raiffeisen.png` |

Matching is based only on `brand`, with case, accents, punctuation, and repeated
whitespace normalized. The station name is never used to infer a brand.

## Safe local paths and fallback

The default is `/local/fuel-logos/`. A custom path may use `/local/...` or
`/hacsfiles/...`. External URLs, query strings, backslashes, control characters,
and `..` are rejected. The generated filename is always a canonical alias plus
`.png`; provider input cannot become a path component. Unknown brands, missing
files, and image-load errors use the gas-pump icon. Logos are rendered in the
station list and both highlight-card types with constrained dimensions,
`object-fit: contain`, and alt text.

No automatic download or CDN is used. Existing cards remain unchanged because
`show_brand_logos` defaults to `false`.
