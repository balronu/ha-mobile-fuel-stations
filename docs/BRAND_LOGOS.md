# Brand logos

## v0.6.0-beta.2 asset decision

Beta.2 bundles a small, pinned SVG set whose sources, hashes, technical checks,
and residual trademark risks are documented in the repository-level
[`BRAND_LOGOS.md`](../BRAND_LOGOS.md). No artwork was copied from the
Tankerkönig card projects.

Reviewed references:

- [timmaurice/lovelace-tankerkoenig-card](https://github.com/timmaurice/lovelace-tankerkoenig-card)
- [panbachi/tankerkoenig-card](https://github.com/panbachi/tankerkoenig-card)

Both repositories expose MIT code licenses, while the reviewed README/license
material does not identify a separate license or redistribution permission for
the brand image files. No image was copied from either repository.

v0.6.0-beta.2 provides provider-independent brand resolution with local
bundled assets. The implementation maps the station's existing `brand`
attribute to a canonical local filename.

## Rights boundary

The referenced Tankerkönig cards are MIT-licensed for their code. That does not
prove that their logo image files are freely reusable or that a trademark owner
has granted redistribution rights. The bundled set therefore uses separate
Simple Icons/Commons sources and records the remaining trademark risk instead
of claiming endorsement. Users remain responsible for the rights to custom
overrides placed in `/config/www/fuel-logos/`.

## Supported aliases

| Brand values | Local filename |
| --- | --- |
| Aral | `aral.svg` |
| Shell | `shell.svg` |
| JET | `jet.svg` |
| Total, TotalEnergies | `total.svg` |
| ORLEN, ORLEN Express | `orlen.svg` |
| OMV | `omv.svg` |

Matching uses `brand` first, with case, accents, punctuation, and repeated
whitespace normalized. If that does not resolve to a bundled asset, a complete
supported brand phrase in the station name may be used; unsupported or
ambiguous values remain on the fallback icon.

## Safe local paths and fallback

The bundled default is `/mobile_fuel_stations/logos/`. A custom path may use `/local/...` or
`/hacsfiles/...`. External URLs, query strings, backslashes, control characters,
and `..` are rejected. The generated filename is always a canonical alias plus
`.svg`; provider input cannot become a path component. Unknown brands, missing
files, and image-load errors use the gas-pump icon. Logos are rendered in the
station list and both highlight-card types with constrained dimensions,
`object-fit: contain`, and alt text.

No automatic download or CDN is used. New cards try the safe local logo path by
default; an explicit `show_brand_logos: false` keeps the gas-pump fallback.
