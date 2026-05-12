// Copies the latest v0.3 graph artifacts into ./public so Vite serves them
// at /graph.json and /node-details.json.
//
// Run automatically by `predev` and `prebuild`; can also be invoked
// manually via `npm run sync`.
//
// Source of truth: <repo>/generated/v0.3/{graph,node-details}.json
// produced by `python -m scripts.v03.build_db`.

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "../../..");
const srcDir = resolve(repoRoot, "generated/v0.3");
const dstDir = resolve(__dirname, "../public");

const files = ["graph.json", "node-details.json"];

mkdirSync(dstDir, { recursive: true });

let missing = false;
for (const name of files) {
  const src = resolve(srcDir, name);
  const dst = resolve(dstDir, name);
  if (!existsSync(src)) {
    console.warn(
      `[sync] WARN: ${src} not found. ` +
        `Run \`python -m scripts.v03.build_db\` from the repo root.`,
    );
    missing = true;
    continue;
  }
  copyFileSync(src, dst);
  console.log(`[sync] ${name} -> public/`);
}

if (missing) {
  console.warn(
    "[sync] some graph artifacts are missing; the explorer will fail to load.",
  );
}
