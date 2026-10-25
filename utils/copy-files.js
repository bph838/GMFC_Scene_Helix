#!/usr/bin/env node
// Copies a file or folder to another location on this PC.
//
// Usage:
//   node utils/copy-files.js [source] [destination]
//
// - source defaults to src/Gordano-Model-Flying-Club.xml, destination defaults to helix_path.
// - The source (file or folder) is copied into <destination> keeping its name;
//   folders are copied with all their contents.
// - The destination folder is created if it does not exist; existing files are overwritten.

const fs = require("fs");
const path = require("path");

const helix_path = "C:\\ProgramData\\HELI-X11\\resources\\environments\\SkyBox\\Gordano_Model_Flying_Club\\";

const default_source = path.join(__dirname, "..", "src", "Gordano_Model_Flying_Club.xml");

// With no arguments, copies the Gordano XML into the HeliX SkyBox folder.
const [source = default_source, destination = helix_path] = process.argv.slice(2);

const src = path.resolve(source);
const dest = path.resolve(destination);

if (!fs.existsSync(src)) {
  console.error(`Source not found: ${src}`);
  process.exit(1);
}

try {
  fs.mkdirSync(dest, { recursive: true });

  const target = path.join(dest, path.basename(src));
  fs.cpSync(src, target, { recursive: true, force: true });

  console.log(`Copied ${src} -> ${target}`);
 } catch (err) {
  console.error(`Copy failed: ${err.message}`);
  process.exit(1);
}
