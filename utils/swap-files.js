#!/usr/bin/env node
// Swaps the names of two files, so each takes the other's name.
//
// Usage:
//   node utils/swap-files.js <file-a> <file-b>
//
// - Bare file names are looked up in images/2048, e.g. "Gordano_Model_Flying_Club_left.jpg".
// - Paths containing a folder are used as given, e.g. "images/other/sky.jpg".
// - Running the same swap twice restores the original names.

const fs = require("fs");
const path = require("path");

const images_dir = path.join(__dirname, "..", "images", "2048");

const [fileA, fileB] = process.argv.slice(2);

if (!fileA || !fileB) {
  console.error("Usage: node utils/swap-files.js <file-a> <file-b>");
  process.exit(1);
}

function resolveFile(file) {
  return path.basename(file) === file ? path.join(images_dir, file) : path.resolve(file);
}

const a = resolveFile(fileA);
const b = resolveFile(fileB);

for (const file of [a, b]) {
  if (!fs.existsSync(file)) {
    console.error(`File not found: ${file}`);
    process.exit(1);
  }
}

// Rename via a temporary name so neither file is overwritten.
const temp = `${a}.swap-tmp`;

try {
  fs.renameSync(a, temp);
  fs.renameSync(b, a);
  fs.renameSync(temp, b);

  console.log(`Swapped ${path.basename(a)} <-> ${path.basename(b)}`);
} catch (err) {
  console.error(`Swap failed: ${err.message}`);
  process.exit(1);
}
