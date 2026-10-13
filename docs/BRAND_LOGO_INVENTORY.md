# Reference logo inventory and rights review

This document records the final individual review of the 62 named station
brands represented by the reference project's `src/gasstation_logos` PNG
filenames. `404.png` is a generic fallback and is deliberately excluded from
the 62-brand count. No reference PNG is included in Mobile Fuel Stations.

The reference project is MIT-licensed for its code, but it does not provide a
per-image licence or a complete source manifest for these PNGs. Therefore the
reference filenames are identification evidence only, not redistribution
permission. The six existing local SVGs have separate provenance and hashes in
[`BRAND_LOGOS.md`](../BRAND_LOGOS.md).

## Decision key and legal boundary

- **A** — documented basis for a possible future local inclusion; still
  requires the normal repository review, current-variant check, hash, and
  trademark review before publication.
- **B** — a concrete candidate/source exists, but consent or an additional
  rights/currentness record is still required. Do not publish yet.
- **C** — no suitable current original file and rights basis was found.
- **D** — a concrete identity or usage problem makes inclusion not recommended
  as a station-brand asset.

This is a preliminary documentation and engineering assessment, not legal
advice. Section 23 MarkenG concerns identifying or referring to another
party's goods/services under its conditions; it does not itself grant a right
to reproduce a particular image. Reproduction and public availability are
separate rights under §§ 16 and 19a UrhG. The [official § 23 MarkenG text](https://www.gesetze-im-internet.de/markeng/__23.html),
[§ 16 UrhG](https://www.gesetze-im-internet.de/urhg/__16.html), and
[§ 19a UrhG](https://www.gesetze-im-internet.de/urhg/__19a.html) are the legal
references used for this separation.

`PD-textlogo` on Wikimedia Commons is recorded as evidence about the uploader's
copyright assessment for a simple text/geometric motif, not as a binding legal
opinion or a trademark licence. A public download page, an official logo
download, or an MIT code licence is likewise not by itself a GitHub/HACS
redistribution grant.

## Complete 62-brand matrix

`SHA-256: n/a` means that no candidate file was downloaded into the
repository. Hashes for the four files inspected temporarily during this audit
are recorded so that a later implementation can pin an exact revision; the
files were not added to the worktree.

| Brand | Original file / source and revision | Rights evidence and SHA-256 | Copyright / trademark assessment | Result and reason |
| --- | --- | --- | --- | --- |
| Access | `access.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Protectability and mark ownership unresolved; factual identification would still need § 23 review | **C** — obtain a current official asset and rights record |
| Agip / Eni | `agip-eni.png`; official Eni source not pinned | No repository redistribution grant; SHA-256: n/a | Logo likely protected as a mark; current Agip/Eni variant must be identified | **B** — request/record permission or a defensible current source |
| Allguth | `allguth.png`; [official press page](https://www.allguth.de/presse/) | Official media source found, no open redistribution terms; SHA-256: n/a | Copyright and trademark remain separate; no GitHub/HACS grant found | **B** — obtain permission or a licence statement |
| Aral | `frontend/logos/aral.svg`; [source record](../BRAND_LOGOS.md) | Existing separately reviewed source; SHA-256: `c144c9cf303e15d1addc4ca45736c99508cfb68aabef07f09feb80bf0f21b76c` | Simple-geometry/CC0 source assessment recorded; Aral mark remains protected | **A** — already bundled; no new PNG needed |
| Avia Xpress | `avia-xpress.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Variant/network identity not sufficiently pinned | **C** — identify the current Xpress asset and rights |
| Avia | `avia.png`; official/brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Mark and current national variant require confirmation | **B** — obtain a current original and rights record |
| BayWa | `baywa.png`; [official download center](https://www.baywa.com/downloadcenter) | Official source exists, no open redistribution terms; SHA-256: n/a | Corporate mark may be protected; station-use context needs confirmation | **B** — obtain permission or explicit redistribution terms |
| Bell Oil | `bell-oil.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Ownership/current station identity unresolved | **C** — locate a current official source |
| bft | `bft.png`; [official downloads](https://www.bft.de/service-beratung/downloads) | Official logo download exists, no GitHub/HACS terms; SHA-256: n/a | Mark likely protected; identification use does not settle image redistribution | **B** — obtain a written/open redistribution basis |
| Calpam | `calpam.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current owner and artwork unresolved | **C** — locate a current original and rights record |
| citi oil SB-Tankstelle | `citi-oil-sb-tankstelle.png`; composite reference filename only | No concrete brand-file rights evidence; SHA-256: n/a | Composite/operator description is not a verified general station brand | **D** — do not add as a standalone brand asset |
| CLASSIC | `classic.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Name is potentially ambiguous across markets; mark variant requires confirmation | **B** — identify the relevant station network and obtain rights evidence |
| E-Center | `e-center.png`; retail brand candidate, exact station asset not pinned | No redistribution evidence; SHA-256: n/a | Retail sub-brand requires confirmation as a fuel-station identity | **B** — verify station-brand identity and source |
| ED | `ed.png`; short-name candidate, exact provider source not pinned | No redistribution evidence; SHA-256: n/a | Very short/ambiguous designation; exact mark requires confirmation | **B** — require exact provider mapping and rights evidence |
| EDEKA | `edeka.png`; retail brand candidate, exact station asset not pinned | No redistribution evidence; SHA-256: n/a | Retail mark; station use and current artwork need confirmation | **B** — verify the actual station operator/source |
| ELAN | `elan.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current national/logo variant requires confirmation | **B** — locate a current original and rights record |
| Esso | [`Esso_textlogo.svg`](https://commons.wikimedia.org/wiki/File:Esso_textlogo.svg), Commons oldid 1142159314 | Commons marks it PD-textlogo and trademarked; source is goodlogo/ExxonMobil, not an explicit redistribution licence; SHA-256: `980c40440046cdaa32707a70a3129dfa9fb96dd3061798c8801edc386281f286` | Simple-text assessment is not a binding copyright decision; file is a historical 2013 upload and the Esso mark remains protected | **B** — obtain a current asset/permission and confirm the intended variant |
| Feneberg | `feneberg.png`; retail/station candidate, exact file not pinned | No redistribution evidence; SHA-256: n/a | Retail/station identity and current artwork require confirmation | **B** — locate a current original and rights record |
| Fläming Tank | `flaeming-tank.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Local/operator identity unresolved | **C** — obtain the operator's current asset and permission |
| Globus | [`icons/globus.svg`](https://github.com/simple-icons/simple-icons/blob/dc7b10662a0a2cfdfc9305e2a2b06c023c30724a/data/simple-icons.json), Simple Icons `develop` `dc7b10662a0a2cfdfc9305e2a2b06c023c30724a` | [Simple Icons CC0 licence](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md); exact temporary file SHA-256: `861ed94bfe537b5ab03312c06706aa9b3cdecf1dc10b9d5e8d9aa6bbf1449b42` | CC0 is a documented copyright basis for the repository asset; Globus trademark/identification limits remain | **A** — strongest new candidate, subject to pinning this revision and trademark review |
| Greenline | `greenline.png`; [official/legacy brand page](https://alt.greenline.de/auftritt.html) | Brand source describes the logo, no redistribution terms; SHA-256: n/a | Currentness and copyright basis unresolved | **B** — obtain permission or a clear open licence |
| Grüne | `gruene.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Generic/ambiguous name; no verified station brand | **C** — identify the exact operator |
| HEM | `hem.png`; [official press kit](https://www.hem-tankstelle.de/ueber-hem/pressekit) | Official logo download exists, no open redistribution terms; SHA-256: n/a | Mark likely protected; official availability is not a licence | **B** — obtain explicit GitHub/HACS permission or licence |
| Hessol | `hessol.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current logo/owner unresolved | **C** — locate a current original and rights record |
| Hornbach | `hornbach.png`; no station-brand source | No relevant station-logo rights basis; SHA-256: n/a | Hardware/retail mark, not a verified fuel-station network mark | **D** — do not use as a station-brand asset |
| Hoyer | `hoyer.png`; Commons category concerns the Hoyer logistics/fuel company, not a pinned station asset | Category presence is not a file licence; SHA-256: n/a | Identity collision with other Hoyer businesses and current station variant unresolved | **D** — do not add without exact operator identity and permission |
| Jantzon Tankstelle | `jantzon-tankstelle.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Local operator identity unresolved | **C** — obtain a current operator asset and rights record |
| JET | `frontend/logos/jet.svg`; [source record](../BRAND_LOGOS.md) | Existing separately reviewed source; SHA-256: `83259f9ef037ad0449e2539eef9ff25c2b4eda222e01c87657de7bbb5b0e3d1f` | CC0/source assessment recorded; JET trademark remains protected | **A** — already bundled; no new PNG needed |
| Joiss | `joiss.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current operator and artwork unresolved | **C** — locate a current original and rights record |
| K+K Klaas & Kock | `kk-klaas--kock.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Retail/operator mark and station variant unresolved | **C** — verify exact station use and source |
| Minera Automatenstation | `minera-automatenstation.png`; operator candidate, exact station asset not pinned | No redistribution evidence; SHA-256: n/a | Descriptive/operator-specific variant requires confirmation | **B** — identify current operator asset and rights evidence |
| Minera | `minera.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current owner and country variant require confirmation | **B** — locate a current original and rights record |
| MOL | `mol.png`; brand candidate known, exact regional file not pinned | No redistribution evidence; SHA-256: n/a | Current regional artwork requires confirmation | **B** — obtain a current official asset and rights record |
| Mr. Wash Autoservice AG | `mr-wash-autoservice-ag.png`; service/station candidate, exact file not pinned | No redistribution evidence; SHA-256: n/a | Service/retail mark; station-logo identity requires confirmation | **B** — verify whether a fuel-station mark is intended |
| MTB | `mtb.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Ambiguous abbreviation and ownership | **C** — require exact provider mapping |
| Mundorf Tank | `mundorf-tank.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Local/operator identity unresolved | **C** — obtain a current operator asset and rights record |
| Nordoel | `nordoel.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current artwork/rights require confirmation | **B** — locate a current original and rights record |
| OIL! | [`Logo OIL!.svg`](https://commons.wikimedia.org/wiki/Category:OIL!_Tankstellen) or `OIL! Logo.svg` in the category | Commons category lists files but does not supply a per-file licence in the category; SHA-256: n/a | Current candidate and simple-logo status must be checked on the exact file page; trademark remains | **B** — inspect one exact file page and obtain/record a defensible rights basis |
| Oktan | `oktan.png`; [official press page](https://oktan.de/presse) | Official source found, no open redistribution terms; SHA-256: n/a | Mark likely protected; no repository licence found | **B** — obtain permission or a clear licence |
| OMV | `frontend/logos/omv.svg`; [source record](../BRAND_LOGOS.md) | Existing separately reviewed source; SHA-256: `b5d8b7f4f844698bdf0e35dae13416558c6c49cc92d326f16a210d1633615051` | Simple-geometry/PD assessment recorded; OMV trademark remains protected | **A** — already bundled; no new PNG needed |
| ORLEN | `frontend/logos/orlen.svg`; [source record](../BRAND_LOGOS.md) | Existing separately reviewed source; SHA-256: `467eb4cec9e954944d6506282e839a174ba36bbeef39775373776d08d2abe812` | Simple-geometry/PD assessment recorded; wordmark age and trademark risk documented | **A** — already bundled; no new PNG needed |
| PIN | `pin.png`; short-name candidate, exact network source not pinned | No redistribution evidence; SHA-256: n/a | Very short/ambiguous mark; exact network requires confirmation | **B** — require exact provider mapping and rights evidence |
| Q1 | [`Q1_logo.svg`](https://commons.wikimedia.org/wiki/File:Q1_logo.svg), Commons oldid 1261951876 | Commons PD-textlogo claim and historical `Bild-LogoSH` permission note; not a current repository redistribution grant; SHA-256: `3d7892ff80078e530b2ed792b8f6dd97ff584e397d118f735d52cc577fe177de` | Simple-geometry assessment is not binding; page is old/author is unresolved and trademark warning remains | **B** — obtain current confirmation/permission before publication |
| Raiffeisen | `raiffeisen.png`; no single current station-brand source | No redistribution evidence; SHA-256: n/a | “Raiffeisen” covers many regional entities and marks | **C** — identify the exact station network first |
| RAN | `ran.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current owner/market and artwork unresolved | **C** — locate a current original and rights record |
| Roth Energie | `roth-energie.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current logo/owner requires confirmation | **B** — locate a current original and rights record |
| SB-Tankstelle | `sb.png`; generic reference designation | No concrete brand-file rights evidence; SHA-256: n/a | Generic abbreviation/description, not a uniquely identified mark | **D** — keep neutral fallback and readable provider name |
| Schillhorn Tankstelle | `schillhorn-tankstelle.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Local operator identity unresolved | **C** — obtain a current operator asset and rights record |
| Schindele | `schindele.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current operator identity/artwork unresolved | **C** — locate a current original and rights record |
| SCORE | `score.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current logo variant requires confirmation | **B** — obtain a current original and rights record |
| Shell | `frontend/logos/shell.svg`; [source record](../BRAND_LOGOS.md) | Existing separately reviewed source; SHA-256: `d3a4b69b3437e4e94ac7a974c2d3b9780a57cdbf82ff57e2f2558fb38d03d7cf` | CC0/source assessment recorded; Shell trademark remains protected | **A** — already bundled; no new PNG needed |
| Spreves | `spreves.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Current operator identity/artwork unresolved | **C** — locate a current original and rights record |
| Sprint | `sprint.png`; no suitable current original file found | No redistribution evidence; SHA-256: n/a | Name is used by multiple businesses; station variant unresolved | **C** — identify the exact network first |
| star | [`Star_Tankstelle_Logo_2020.svg`](https://commons.wikimedia.org/wiki/File:Star_Tankstelle_Logo_2020.svg), Commons oldid 1262365621 | Commons PD-textlogo claim; source is ADAC Motorwelt with colors from star.de and author ORLEN Deutschland GmbH; SHA-256: `fca4335fc87022421461792b5fffc260d0f990eced5a9547792aa6858c84046b` | Concrete 2020 station variant, but PD-textlogo is not a binding legal guarantee and star remains a trademark | **B** — currentness/permission record still required |
| Supermarkt-Tankstelle | `supermarkt-tankstelle.png`; generic reference designation | No concrete brand-file rights evidence; SHA-256: n/a | Descriptive term, not a single brand owner | **D** — do not add as a brand asset |
| SVG | `svg.png`; ambiguous filename/abbreviation | No concrete brand-file rights evidence; SHA-256: n/a | Not a verified station brand and unsafe as a generic alias | **D** — do not treat as a brand |
| team | `team.png`; brand candidate known, exact file not pinned | No redistribution evidence; SHA-256: n/a | Current station-brand variant requires confirmation | **B** — locate a current original and rights record |
| Total | `frontend/logos/total.svg`; [source record](../BRAND_LOGOS.md) | Existing asset also serves the TotalEnergies alias; SHA-256: `4bf2adc55ed00194bfdf3aab6e9d85f691cc5b76dd483a52aa40a1b92a24a4be` | Current TotalEnergies wordmark source assessment recorded; trademark remains protected | **A** — already bundled; no duplicate asset |
| TotalEnergies | `frontend/logos/total.svg`; [source record](../BRAND_LOGOS.md) | Same existing local asset as Total; SHA-256: `4bf2adc55ed00194bfdf3aab6e9d85f691cc5b76dd483a52aa40a1b92a24a4be` | Current TotalEnergies wordmark source assessment recorded; trademark remains protected | **A** — already bundled; no duplicate asset |
| Trigema | `trigema.png`; no station-brand source | No relevant station-logo rights basis; SHA-256: n/a | Textile/retail mark, not a verified fuel-station network mark | **D** — do not use as a station-brand asset |
| V-Markt | `v-markt.png`; retail/station candidate, exact asset not pinned | No redistribution evidence; SHA-256: n/a | Retail/station identity and current artwork require confirmation | **B** — verify the actual station operator/source |
| Westfalen | [`WestfalenAG Logo.png`](https://commons.wikimedia.org/wiki/Category:Westfalen_AG) listed in the Commons category | Category lists the file but does not establish its individual licence; SHA-256: n/a | Exact file page, current station variant, and trademark scope still require review | **B** — inspect the exact file page and obtain/record a defensible rights basis |

**Count:** A = 8, B = 29, C = 18, D = 7; total = 62 named brands. The
`404.png` reference fallback is not part of this count.

## Concrete file review

The four candidate files examined temporarily were well-formed static SVGs.
The scan found no `<script>`, `<foreignObject>`, `<iframe>`, `<embed>`,
`<image>`, CSS import, or external resource reference. XML namespace and
metadata URLs in Q1/star/Esso are declarations or provenance metadata, not
runtime fetches. This is a technical result only; it does not resolve rights.

| Candidate | Exact revision | Local technical result | Publication decision |
| --- | --- | --- | --- |
| Q1 | Commons oldid `1261951876`; 800×550, 4 KB | Static SVG; SHA-256 `3d7892ff80078e530b2ed792b8f6dd97ff584e397d118f735d52cc577fe177de` | **B** — currentness and rights record still needed |
| star | Commons oldid `1262365621`; 400×315, 19 KB | Static SVG; SHA-256 `fca4335fc87022421461792b5fffc260d0f990eced5a9547792aa6858c84046b` | **B** — candidate is identifiable, not yet cleared |
| Esso | Commons oldid `1142159314`; 220×156, 5 KB | Static SVG; SHA-256 `980c40440046cdaa32707a70a3129dfa9fb96dd3061798c8801edc386281f286` | **B** — historical file/source and trademark need resolution |
| OIL! | Category lists two SVG candidates, but no exact file selected | Not downloaded; no hash | **B** — inspect one exact file page first |
| Westfalen | Category lists `WestfalenAG Logo.png` | Not downloaded; no hash | **B** — inspect exact file page/licence first |
| Globus | Simple Icons `develop` commit `dc7b10662a0a2cfdfc9305e2a2b06c023c30724a`; [file](https://github.com/simple-icons/simple-icons/blob/dc7b10662a0a2cfdfc9305e2a2b06c023c30724a/icons/globus.svg) | Static one-path SVG; SHA-256 `861ed94bfe537b5ab03312c06706aa9b3cdecf1dc10b9d5e8d9aa6bbf1449b42` | **A candidate** — CC0 basis is documented, but pin this revision and retain trademark review |

## Publication plan

1. **Already publishable scope:** retain the six existing SVGs only. The
   existing assets are not changed by this review; `Total` and `TotalEnergies`
   intentionally share `total.svg`.
2. **Next asset PR candidate:** Globus is the only new A candidate. A separate
   PR would pin the exact Simple Icons revision, add the local SVG only after
   a final review, record the source and SHA-256, run the existing SVG safety
   tests, and add alias/fallback tests. This report does not add it.
3. **B candidates:** request a short written statement permitting
   redistribution in the public GitHub repository and HACS package, or find a
   concrete licence attached to the exact file. For Commons candidates, cite
   the exact file page and revision, not only a category or search result.
4. **C candidates:** identify the exact station network/operator and obtain a
   current original asset plus rights record. Until then, keep the neutral
   pump icon and readable brand name.
5. **D candidates:** do not add an image. Keep the neutral fallback and use the
   provider/station name for factual identification. Reconsider only if a
   distinct station-brand identity is established.
6. No external runtime logo URLs are proposed. User-provided local logo
   overrides remain governed by the existing safe-path rules.

No image file was added, no runtime code was changed, and no release or PR was
created as part of this review.
