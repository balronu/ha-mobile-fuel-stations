from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import struct


ROOT = Path(__file__).parents[1]
ASSET_DIR = ROOT / "frontend" / "logos"
DEPLOYED_ASSET_DIR = ROOT / "custom_components" / "mobile_fuel_stations" / "frontend" / "logos"
EXPECTED_PNG = {
    "access.png", "agip-eni.png", "allguth.png", "aral.png", "avia-xpress.png", "avia.png",
    "baywa.png", "bell-oil.png", "bft.png", "calpam.png", "citi-oil-sb-tankstelle.png",
    "classic.png", "e-center.png", "ed.png", "edeka.png", "elan.png", "esso.png",
    "feneberg.png", "flaeming-tank.png", "globus.png", "greenline.png", "gruene.png",
    "gulf.png", "hem.png", "hessol.png", "hornbach.png", "hoyer.png", "jet.png", "joiss.png",
    "kk-klaas-kock.png", "minera.png", "mol.png", "mr-wash-autoservice-ag.png",
    "mtb.png", "mundorf-tank.png", "nordoel.png", "oil.png", "oktan.png", "omv.png", "orlen.png", "pin.png",
    "q1.png", "raiffeisen.png", "ran.png", "roth-energie.png", "sb.png",
    "schillhorn-tankstelle.png", "schindele.png", "score.png", "spreves.png",
    "sprint.png", "star.png", "supermarkt-tankstelle.png", "team.png", "tinq.png", "shell.png",
    "total.png", "trigema.png", "v-markt.png", "westfalen.png",
}
def test_stable_png_logo_inventory_is_normalized_and_deployed():
    assert {path.name for path in ASSET_DIR.glob("*.png")} == EXPECTED_PNG
    assert {path.name for path in DEPLOYED_ASSET_DIR.glob("*.png")} == EXPECTED_PNG
    for name in EXPECTED_PNG:
        payload = (ASSET_DIR / name).read_bytes()
        deployed = (DEPLOYED_ASSET_DIR / name).read_bytes()
        assert payload == deployed
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", payload[16:24])
        assert 1 <= width <= 512
        assert 1 <= height <= 512
        assert len(payload) > 32
