"""
Heli-X terrain builder for Blender  -  Gordano MFC (AMARC), Weston Drove
=========================================================================

What it does
------------
1. BUILD : makes a ground mesh ("terrain") centred on the pilot / camera
           position, shaped by the spot heights you type in below.
2. EXPORT: writes every mesh in the "HeliX Terrain" collection to a Heli-X
           topography XML file (GroundType triangles), ready to drop into
           your airport folder.

No Heli-X add-on is needed.

How to run
----------
Blender > "Scripting" workspace (tab along the top) > Open > this file
> edit the SETTINGS block > press the Run (play) button.

Typical workflow:
  MODE = "build"   -> run. Look at the terrain. Sculpt / move vertices if you want.
  MODE = "export"  -> run. The XML is written to OUTPUT_FILE.
  (MODE = "both" does both in one go.)

Coordinates
-----------
Everything is in metres, relative to the ground directly under the camera.
  Blender:  X = right, Y = forward (towards the cube's FRONT image), Z = up
  Heli-X :  X = left, Y = up, Z = forward (so Heli-X x = -Blender x, z = Blender y)
The script converts for you on export.
"""

import bpy
import math
import os

# --------------------------------------------------------------------------
# SETTINGS - edit these
# --------------------------------------------------------------------------

MODE = "both"            # "build", "export" or "both"

# Where to write the topography file. Point this at your airport folder, e.g.
# Windows: r"C:\ProgramData\HELI-X10\resources\environments\SkyBox\Gordano\Terrain.xml"
# macOS  : os.path.expanduser("~/Library/HELI-X10/resources/environments/SkyBox/Gordano/Terrain.xml")
OUTPUT_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "Terrain.xml")

# Compass bearing (degrees, true north) that your *_front.jpg image looks towards.
# 0 = front image faces north, 90 = east, etc. Only matters if you enter
# SPOT_HEIGHTS as east/north offsets (from a map); see below.
FRONT_BEARING_DEG = 0.0

# Size of the terrain square (metres, each side) and grid spacing (metres).
# 300 m x 300 m at 5 m spacing = 7,200 triangles, which Heli-X handles fine.
GRID_SIZE_M = 300.0
GRID_STEP_M = 5.0

# Spot heights relative to the ground under the camera (that point = 0.0).
# Each entry: (east_m, north_m, height_m)  -- offsets from the camera on a map.
# Get them from Environment Agency LIDAR (1 m DTM), a laser level, or a walk
# round with a long tape and a spirit level. Leave the list empty for flat.
# Examples (delete / replace with real values):
SPOT_HEIGHTS = [
    (0.0,    0.0,  0.00),   # camera position - always keep this one at 0
    # (40.0,  -10.0, -0.30),  # e.g. far end of runway 30 cm lower
    # (-60.0,  25.0,  1.20),  # e.g. a bank 60 m west, 25 m north, 1.2 m higher
]

# How far a spot height's influence reaches (m). Beyond this the terrain eases
# back to the nearest measured level rather than inventing slopes.
INFLUENCE_RADIUS_M = 120.0

# Crash-object properties written to every triangle (see Heli-X manual 6.2.1).
TRIANGLE_ATTRS = {
    "FrictionFactor": "1.00",
    "CrashSensitivityFactor": "1.00",
    "Thickness": "1.00",
    "Alpha": "1.0000",          # manual: ground = opaque
    "MakeCrashObject": "True",
    "ShadowReceiver": "True",   # heli shadow falls on the terrain
    "CeilingType": "False",
    "GroundType": "True",       # nothing can be "behind" the ground
}

COLLECTION_NAME = "HeliX Terrain"

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def to_front_right(east, north, bearing_deg):
    """Map (east, north) offsets into the pano frame (right, forward)."""
    b = math.radians(bearing_deg)
    right = east * math.cos(b) - north * math.sin(b)
    front = east * math.sin(b) + north * math.cos(b)
    return right, front


def height_at(x, y, pts):
    """Inverse-distance-weighted height at Blender (x, y) from spot heights."""
    if not pts:
        return 0.0
    num = den = 0.0
    nearest_h, nearest_d = 0.0, float("inf")
    for px, py, h in pts:
        d = math.hypot(x - px, y - py)
        if d < 1e-6:
            return h
        if d < nearest_d:
            nearest_d, nearest_h = d, h
        if d <= INFLUENCE_RADIUS_M:
            w = 1.0 / (d * d)
            num += w * h
            den += w
    return num / den if den else nearest_h


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------


def build():
    pts = [(*to_front_right(e, n, FRONT_BEARING_DEG), h) for e, n, h in SPOT_HEIGHTS]

    n = int(round(GRID_SIZE_M / GRID_STEP_M))
    half = GRID_SIZE_M / 2.0
    verts, faces = [], []
    for j in range(n + 1):
        y = -half + j * GRID_STEP_M
        for i in range(n + 1):
            x = -half + i * GRID_STEP_M
            verts.append((x, y, height_at(x, y, pts)))
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            faces.append((a, a + 1, a + n + 2, a + n + 1))

    col = get_collection()
    old = bpy.data.objects.get("Terrain")
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)

    mesh = bpy.data.meshes.new("Terrain")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Terrain", mesh)
    col.objects.link(obj)

    # Markers so you can see where things are (not exported)
    if bpy.data.objects.get("Pilot") is None:
        pilot = bpy.data.objects.new("Pilot", None)
        pilot.empty_display_type = "SINGLE_ARROW"
        pilot.empty_display_size = 1.7
        bpy.context.scene.collection.objects.link(pilot)
    for name, (e, nn, h) in zip(
        [f"Spot_{k}" for k in range(len(SPOT_HEIGHTS))], SPOT_HEIGHTS
    ):
        if bpy.data.objects.get(name) is None:
            x, y = to_front_right(e, nn, FRONT_BEARING_DEG)
            m = bpy.data.objects.new(name, None)
            m.empty_display_type = "SPHERE"
            m.empty_display_size = 0.5
            m.location = (x, y, h)
            bpy.context.scene.collection.objects.link(m)

    print(f"[HeliX] Built terrain: {len(verts)} vertices, {len(faces) * 2} triangles")


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------


def fmt(v):
    return ",".join(f"{c:.3f}" for c in v)


def export():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        raise RuntimeError(f'No "{COLLECTION_NAME}" collection - run with MODE="build" first')

    attrs = " ".join(f'{k}="{v}"' for k, v in TRIANGLE_ATTRS.items())
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<project>"]
    count = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()

    for obj in col.all_objects:
        if obj.type != "MESH" or obj.hide_get():
            continue
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        mw = obj.matrix_world
        for tri in me.loop_triangles:
            # Blender (x-right, y-forward, z-up) -> Heli-X (x-left, y-up, z-forward)
            p = []
            for vi in tri.vertices:
                w = mw @ me.vertices[vi].co
                p.append((-w.x, w.z, w.y))
            # Normal, forced to point up (+Y in Heli-X)
            ux, uy, uz = (p[1][k] - p[0][k] for k in range(3))
            vx, vy, vz = (p[2][k] - p[0][k] for k in range(3))
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            if ny < 0:
                p[1], p[2] = p[2], p[1]
                nx, ny, nz = -nx, -ny, -nz
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            lines.append(f"  <Triangle {attrs}>")
            for q in p:
                lines.append(f"    <Point>{fmt(q)}</Point>")
            lines.append(f"    <Normal>{fmt((nx / ln, ny / ln, nz / ln))}</Normal>")
            lines.append("  </Triangle>")
            count += 1
        ev.to_mesh_clear()

    lines.append("</project>")
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[HeliX] Exported {count} triangles to {OUTPUT_FILE}")


# --------------------------------------------------------------------------

if MODE in ("build", "both"):
    build()
if MODE in ("export", "both"):
    export()
