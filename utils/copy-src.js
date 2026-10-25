#!/usr/bin/env node
// Copies everything inside src/ into the HeliX SkyBox folder.
//
// Usage:
//   node utils/copy-src.js [destination]
//
// - destination defaults to helix_path.
// - The contents of src/ are copied directly into <destination> (no "src" subfolder);
//   subfolders are copied with all their contents.
// - The destination folder is created if it does not exist; existing files are overwritten.

const fs = require("fs");
const path = require("path");

const helix_path = "C:\\ProgramData\\HELI-X11\\resources\\environments\\SkyBox\\Gordano_Model_Flying_Club\\";

const src = path.join(__dirname, "..", "src");
const dest = path.resolve(process.argv[2] || helix_path);

if (!fs.existsSync(src)) {
  console.error(`Source not found: ${src}`);
  process.exit(1);
}

try {
  fs.mkdirSync(dest, { recursive: true });

  for (const name of fs.readdirSync(src)) {
    const target = path.join(dest, name);
    fs.cpSync(path.join(src, name), target, { recursive: true, force: true });
    console.log(`Copied ${name} -> ${target}`);
  }
} catch (err) {
  console.error(`Copy failed: ${err.message}`);
  process.exit(1);
}
