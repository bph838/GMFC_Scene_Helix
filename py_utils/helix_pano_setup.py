"""
Heli-X pano viewer for Blender  -  Gordano MFC
==============================================

Puts your 360 photo around the Blender scene and adds a camera at the spot
(and height) the photo was taken from. Look through that camera and you see
your field exactly as Heli-X will show it, with the terrain grid from
helix_terrain.py drawn over the top so you can check it lines up.

Use the ORIGINAL 360 photo from the drone (one wide image, twice as wide as
it is tall, e.g. 8192 x 4096) - not the six cube pictures.

How to run
----------
Scripting tab > Open > this file > edit SETTINGS > Run (play button).
Run it again any time you change a setting.
"""

import bpy
import math
import os

# --------------------------------------------------------------------------
# SETTINGS - edit these
# --------------------------------------------------------------------------

# Full path to the 360 photo. Keep the r before the quote on Windows.
PANO_FILE = r"C:\Users\YourName\Pictures\Gordano_360.jpg"

# Height of the camera above the ground when the photo was taken (metres).
# Must be the same number as <HeightOfEyes> in your Heli-X airport XML.
CAMERA_HEIGHT_M = 1.7

# Spin the photo if the camera's view doesn't match your *_front.jpg picture.
# Try 90, 180 or 270 first; small values (e.g. 5) for fine adjustment.
TURN_DEG = 0.0

# Camera field of view (degrees). 90 matches one cube face.
FIELD_OF_VIEW_DEG = 90.0

# --------------------------------------------------------------------------


def setup_world(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Can't find the photo: {path}")

    world = bpy.data.worlds.get("HeliX Pano") or bpy.data.worlds.new("HeliX Pano")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    for i, n in enumerate((coord, mapping, env, bg, out)):
        n.location = (i * 250 - 500, 0)

    env.image = bpy.data.images.load(path, check_existing=True)
    env.projection = "EQUIRECTANGULAR"
    # Centre of the photo -> Blender +Y ("front", same as helix_terrain.py)
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(-90.0 - TURN_DEG))

    nt.links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Strength"].default_value = 1.0


def setup_camera():
    scene = bpy.context.scene
    cam = bpy.data.objects.get("Pano Camera")
    if cam is None:
        cam = bpy.data.objects.new("Pano Camera", bpy.data.cameras.new("Pano Camera"))
        scene.collection.objects.link(cam)
    cam.location = (0.0, 0.0, CAMERA_HEIGHT_M)
    cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)  # level, looking at front (+Y)
    cam.data.lens_unit = "FOV"
    cam.data.angle = math.radians(FIELD_OF_VIEW_DEG)
    cam.data.clip_start = 0.1
    cam.data.clip_end = 5000.0
    scene.camera = cam
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


def setup_views():
    # Terrain as a see-through grid so the photo shows behind it
    terrain = bpy.data.objects.get("Terrain")
    if terrain is not None:
        terrain.display_type = "WIRE"
        terrain.show_in_front = True

    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "MATERIAL"
                    space.shading.use_scene_world = True
                    space.clip_end = 5000.0
                    space.region_3d.view_perspective = "CAMERA"


setup_world(PANO_FILE)
setup_camera()
setup_views()
print("[HeliX] Pano loaded - look through 'Pano Camera' (Numpad 0)")
