#!/usr/bin/env python3
"""Generate the stdlib-only Natural Earth country runtime dataset.

Usage:
    python scripts/generate_country_data.py INPUT.zip OUTPUT.json

The input is the official Natural Earth Admin 0 - Countries 1:50m archive.
No GIS package is required; this generator reads the Polygon shapefile and its
DBF attributes directly.
"""

from __future__ import annotations

import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ISO_CODE = re.compile(r"^[A-Z]{2}$")
REJECTED_CODES = frozenset({"XK"})


def _dbf_records(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    count, header_len, record_len = struct.unpack_from("<4xIHH20x", data, 0)
    fields: list[tuple[str, int]] = []
    pos = 32
    while data[pos] != 0x0D:
        name = data[pos : pos + 11].split(b"\0", 1)[0].decode("ascii")
        fields.append((name, data[pos + 16]))
        pos += 32

    records: list[dict[str, str]] = []
    for row in range(count):
        start = header_len + row * record_len
        raw = data[start : start + record_len]
        if not raw or raw[:1] == b"*":
            continue
        values: dict[str, str] = {}
        offset = 1
        for name, width in fields:
            values[name] = raw[offset : offset + width].decode("utf-8", "replace").strip("\x00 ")
            offset += width
        records.append(values)
    return [name for name, _width in fields], records


def _shapefile_records(data: bytes) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    pos = 100
    while pos + 8 <= len(data):
        _number, length_words = struct.unpack_from(">2i", data, pos)
        body_start = pos + 8
        body_end = body_start + length_words * 2
        shape_type = struct.unpack_from("<i", data, body_start)[0]
        if shape_type != 5:
            raise ValueError(f"expected Polygon shape type 5, got {shape_type}")
        bbox = list(struct.unpack_from("<4d", data, body_start + 4))
        parts_count, points_count = struct.unpack_from("<2i", data, body_start + 36)
        parts_pos = body_start + 44
        starts = list(struct.unpack_from(f"<{parts_count}i", data, parts_pos))
        points_pos = parts_pos + parts_count * 4
        points = [struct.unpack_from("<2d", data, points_pos + i * 16) for i in range(points_count)]
        rings: list[list[list[float]]] = []
        for index, first in enumerate(starts):
            last = starts[index + 1] if index + 1 < len(starts) else points_count
            rings.append([[point[0], point[1]] for point in points[first:last]])
        records.append({"bbox": bbox, "rings": rings})
        pos = body_end
    return records


def _iso(attrs: dict[str, str]) -> str | None:
    value = attrs.get("ISO_A2", "")
    if value in ("", "-99"):
        value = attrs.get("ISO_A2_EH", "")
    value = value.upper()
    if not ISO_CODE.fullmatch(value) or value in REJECTED_CODES:
        return None
    return value


def generate(source_zip: Path) -> dict[str, object]:
    with zipfile.ZipFile(source_zip) as archive:
        names = archive.namelist()
        shp_name = next(name for name in names if name.endswith(".shp"))
        dbf_name = shp_name[:-4] + ".dbf"
        attrs = _dbf_records(archive.read(dbf_name))[1]
        shapes = _shapefile_records(archive.read(shp_name))
    if len(attrs) != len(shapes):
        raise ValueError(f"DBF/SHP record mismatch: {len(attrs)} != {len(shapes)}")

    countries: dict[str, dict[str, object]] = {}
    for attr, shape in zip(attrs, shapes, strict=True):
        # Full Europe plus Cyprus: Natural Earth classifies Cyprus as Asia.
        if attr.get("CONTINENT") != "Europe" and _iso(attr) != "CY":
            continue
        iso = _iso(attr)
        if iso is None:
            continue
        bbox = shape["bbox"]
        polygon = {"bbox": bbox, "rings": shape["rings"]}
        country = countries.setdefault(iso, {"iso": iso, "bbox": list(bbox), "polygons": []})
        country["polygons"].append(polygon)
        current = country["bbox"]
        current[0] = min(current[0], bbox[0])
        current[1] = min(current[1], bbox[1])
        current[2] = max(current[2], bbox[2])
        current[3] = max(current[3], bbox[3])

    result = {"source": "Natural Earth Admin 0 - Countries 1:50m v5.1.1", "countries": [countries[key] for key in sorted(countries)]}
    return result


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_country_data.py INPUT.zip OUTPUT.json")
    output = Path(sys.argv[2])
    payload = generate(Path(sys.argv[1]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"countries": len(payload["countries"]), "bytes": output.stat().st_size}))


if __name__ == "__main__":
    main()
