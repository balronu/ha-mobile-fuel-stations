import { readFile, writeFile } from "node:fs/promises";

const path = "dist/mobile-fuel-stations-card.js";
const source = await readFile(path, "utf8");
// Keep generated template-literal whitespace semantically intact while making
// the checked-in minified artifact pass git diff --check.
const cleaned = source.replace(/[ \t]+(?=\n)/g, (value) =>
  [...value].map((character) => (character === " " ? "\\x20" : "\\t")).join(""),
);
await writeFile(path, cleaned);
