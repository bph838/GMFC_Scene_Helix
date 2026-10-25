#!/usr/bin/env node
// Flips images horizontally (mirror left <-> right), overwriting them in place.
//
// Usage:
//   node utils/flip-images.js <image> [image...]
//
// - Bare file names are looked up in images/2048, e.g. "gmfc_left.png".
// - Paths containing a folder are used as given, e.g. "images/other/sky.png".
// - Flipping the same image twice restores the original.

const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const images_dir = path.join(__dirname, "..", "images", "2048");

const files = process.argv.slice(2);

if (files.length === 0) {
  console.error("Usage: node utils/flip-images.js <image> [image...]");
  process.exit(1);
}

function resolveImage(file) {
  return path.basename(file) === file ? path.join(images_dir, file) : path.resolve(file);
}

async function flip(file) {
  const src = resolveImage(file);

  if (!fs.existsSync(src)) {
    throw new Error(`Image not found: ${src}`);
  }

  // Read fully into memory first so the same file can be overwritten.
  const input = fs.readFileSync(src);
  const output = await sharp(input).flop().toBuffer();
  fs.writeFileSync(src, output);

  console.log(`Flipped ${src}`);
}

(async () => {
  let failed = false;

  for (const file of files) {
    try {
      await flip(file);
    } catch (err) {
      console.error(`Flip failed: ${err.message}`);
      failed = true;
    }
  }

  process.exit(failed ? 1 : 0);
})();
