from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).parents[1]
ASSET_DIR = ROOT / "frontend" / "logos"
DEPLOYED_ASSET_DIR = ROOT / "custom_components" / "mobile_fuel_stations" / "frontend" / "logos"
EXPECTED = {
    "aral.svg": "c144c9cf303e15d1addc4ca45736c99508cfb68aabef07f09feb80bf0f21b76c",
    "jet.svg": "83259f9ef037ad0449e2539eef9ff25c2b4eda222e01c87657de7bbb5b0e3d1f",
    "omv.svg": "b5d8b7f4f844698bdf0e35dae13416558c6c49cc92d326f16a210d1633615051",
    "orlen.svg": "467eb4cec9e954944d6506282e839a174ba36bbeef39775373776d08d2abe812",
    "shell.svg": "d3a4b69b3437e4e94ac7a974c2d3b9780a57cdbf82ff57e2f2558fb38d03d7cf",
    "total.svg": "4bf2adc55ed00194bfdf3aab6e9d85f691cc5b76dd483a52aa40a1b92a24a4be",
}
FORBIDDEN = re.compile(
    r"<(?:script|foreignObject|iframe|object|embed|image|link|animate|set|mpath)\b"
    r"|url\(\s*(?:https?:|//)"
    r"|(?:xlink:)?href=[\"']\s*(?:https?:|//)",
    re.IGNORECASE,
)


def test_bundled_logo_inventory_is_pinned_and_parseable():
    assert {path.name for path in ASSET_DIR.glob("*.svg")} == set(EXPECTED)
    assert {path.name for path in DEPLOYED_ASSET_DIR.glob("*.svg")} == set(EXPECTED)
    for name, digest in EXPECTED.items():
        payload = (ASSET_DIR / name).read_bytes()
        assert (DEPLOYED_ASSET_DIR / name).read_bytes() == payload
        ET.fromstring(payload)
        assert sha256(payload).hexdigest() == digest
        assert FORBIDDEN.search(payload.decode("utf-8")) is None
