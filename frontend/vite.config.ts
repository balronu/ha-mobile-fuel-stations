import { defineConfig } from "vite";

export default defineConfig({
  build: {
    lib: {
      entry: "src/mobile-fuel-stations-card.ts",
      name: "MobileFuelStationsCard",
      formats: ["iife"],
      fileName: () => "mobile-fuel-stations-card.js",
    },
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
    minify: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
  },
});
