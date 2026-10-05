# Natural Earth country dataset

`countries_50m.json` is a generated, geometry-only runtime extract of:

- Natural Earth Admin 0 – Countries, 1:50m, version 5.1.1
- Official source: <https://www.naturalearthdata.com/downloads/50m-cultural-vectors/>
- Official archive: `https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip`
- Input archive SHA-256: `5fed433373581fa648920435f937d95f2d3c0200e067409c6478dcdf1b853139`

Natural Earth states that its vector and raster data are public domain. No
permission is required for use, modification, or redistribution. The project
asks users who cite the data to use:

> Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.

The generator keeps all features whose Natural Earth `CONTINENT` is `Europe`,
plus Cyprus (classified as Asia by Natural Earth), and discards features with
no accepted ISO alpha-2 code. `ISO_A2` is primary; `ISO_A2_EH` is the
controlled fallback for values such as France (`ISO_A2=-99`, `ISO_A2_EH=FR`).
`XK` is excluded because it is not an official ISO 3166-1 alpha-2 code.

The runtime file stores only ISO code, bounding boxes, and polygon rings. Its
coordinates are stored as longitude, latitude. Regenerate it with:

```text
python scripts/generate_country_data.py INPUT.zip custom_components/mobile_fuel_stations/data/countries_50m.json
```
