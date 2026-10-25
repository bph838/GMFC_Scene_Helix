#!/usr/bin/env node
// Copies the scenery XML, only the topography files it lists, and preview.jpg into the HeliX SkyBox folder.
//
// Usage:
//   node utils/copy-scene.js [scene.xml] [destination]
//
// - scene.xml defaults to src/Gordano_Model_Flying_Club.xml, destination defaults to helix_path.
// - Every <TopographyFile> named in the XML, and preview.jpg, is copied from the same folder as the XML.
// - Fails without copying anything if any of these files is missing.
// - The destination folder is created if it does not exist; existing files are overwritten.

const fs = require("fs");
const path = require("path");

const helix_path = "C:\\ProgramData\\HELI-X11\\resources\\environments\\SkyBox\\Gordano_Model_Flying_Club\\";

const default_scene = path.join(__dirname, "..", "src", "Gordano_Model_Flying_Club.xml");

const [scene_arg = default_scene, destination = helix_path] = process.argv.slice(2);

const scene = path.resolve(scene_arg);
const dest = path.resolve(destination);

if (!fs.existsSync(scene)) {
  console.error(`Scene not found: ${scene}`);
  process.exit(1);
}

// Skip commented-out entries so <!-- <TopographyFile>x.xml</TopographyFile> --> is not copied.
const xml = fs.readFileSync(scene, "utf8").replace(/<!--[\s\S]*?-->/g, "");
const topography = [...xml.matchAll(/<TopographyFile>\s*([^<]+?)\s*<\/TopographyFile>/g)].map((m) => m[1]);

const files = [scene, ...[...topography, "preview.jpg"].map((name) => path.join(path.dirname(scene), name))];

const missing = files.filter((file) => !fs.existsSync(file));
if (missing.length > 0) {
  missing.forEach((file) => console.error(`File not found: ${file}`));
  process.exit(1);
}

try {
  fs.mkdirSync(dest, { recursive: true });

  for (const file of files) {
    const target = path.join(dest, path.basename(file));
    fs.copyFileSync(file, target);
    console.log(`Copied ${path.basename(file)} -> ${target}`);
  }
} catch (err) {
  console.error(`Copy failed: ${err.message}`);
  process.exit(1);
}
