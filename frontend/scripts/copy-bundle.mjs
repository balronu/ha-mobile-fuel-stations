import { copyFile, mkdir, readdir } from "node:fs/promises";

await mkdir("../custom_components/mobile_fuel_stations/frontend", { recursive: true });
await copyFile(
  "dist/mobile-fuel-stations-card.js",
  "../custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js",
);

const logoSource = "logos";
const logoTarget = "../custom_components/mobile_fuel_stations/frontend/logos";
await mkdir(logoTarget, { recursive: true });
for (const filename of await readdir(logoSource)) {
  if (filename.endsWith(".svg")) {
    await copyFile(`${logoSource}/${filename}`, `${logoTarget}/${filename}`);
  }
}
