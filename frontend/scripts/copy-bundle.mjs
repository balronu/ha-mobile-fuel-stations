import { copyFile, mkdir } from "node:fs/promises";

await mkdir("../custom_components/mobile_fuel_stations/frontend", { recursive: true });
await copyFile(
  "dist/mobile-fuel-stations-card.js",
  "../custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js",
);
