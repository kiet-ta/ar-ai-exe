from __future__ import annotations

import base64
import json
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import unquote_to_bytes

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.services.blender_service import BlenderService
from app.services.command_runner import CommandRunner


DATA_URI_RE = re.compile(r"^data:(?P<mime>image/(?:png|jpe?g|svg\+xml))(?P<meta>[^,]*),(?P<data>.*)$", re.I | re.S)
MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/svg+xml": ".svg",
}
MAX_STICKERS = 50
MAX_STICKER_BYTES = 5 * 1024 * 1024


class DecalBakeService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.blender = BlenderService()
        self.runner = CommandRunner()

    def bake(self, source_glb: Path, output_dir: Path, design_config: dict[str, Any]) -> bool:
        stickers = self._prepare_stickers(output_dir, design_config)
        if not stickers:
            return False

        work_dir = output_dir / "_work"
        work_dir.mkdir(parents=True, exist_ok=True)
        source_copy = work_dir / "source.glb"
        shutil.copyfile(source_glb, source_copy)

        manifest_path = work_dir / "decal_manifest.json"
        manifest_path.write_text(json.dumps({"stickers": stickers}, indent=2), encoding="utf-8")

        script_path = work_dir / "apply_decals.py"
        self._write_blender_script(script_path)

        try:
            blender_bin = self.blender.require_available()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        command = [
            blender_bin,
            "--background",
            "--python",
            str(script_path),
            "--",
            str(source_copy),
            str(output_dir),
            str(manifest_path),
        ]
        result = self.runner.run(
            command,
            log_path=work_dir / "decal_bake.log",
            cwd=output_dir,
            timeout=self.settings.reconstruction_command_timeout_seconds,
        )
        if not result.ok:
            message = result.stderr.strip() or result.stdout.strip() or "Blender decal bake failed."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Blender decal bake failed: {message[-1200:]}",
            )

        for name in ["final_shoe.glb", "final_shoe.obj", "final_shoe.mtl"]:
            if not (output_dir / name).is_file():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Blender decal bake did not create {name}.",
                )
        return True

    def _prepare_stickers(self, output_dir: Path, design_config: dict[str, Any]) -> list[dict[str, Any]]:
        raw_stickers = design_config.get("stickers", [])
        if not isinstance(raw_stickers, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Design stickers must be an array.",
            )
        if len(raw_stickers) > MAX_STICKERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Design cannot export more than {MAX_STICKERS} stickers.",
            )

        stickers_dir = output_dir / "stickers"
        prepared: list[dict[str, Any]] = []
        for index, sticker in enumerate(raw_stickers, start=1):
            if not isinstance(sticker, dict):
                continue
            image_url = sticker.get("imageUrl")
            if not isinstance(image_url, str) or not image_url.strip():
                continue

            sticker_id = self._safe_name(str(sticker.get("id") or f"sticker_{index:03d}"))
            image_path, mime_type = self._write_sticker_image(
                image_url,
                stickers_dir,
                f"{index:03d}_{sticker_id}",
            )
            scale = self._number(sticker.get("scale"), 0.2, minimum=0.01, maximum=10.0)
            width = self._number(sticker.get("width"), scale, minimum=0.01, maximum=10.0)
            height = self._number(sticker.get("height"), scale, minimum=0.01, maximum=10.0)
            prepared.append(
                {
                    "id": sticker_id,
                    "imagePath": str(image_path),
                    "mimeType": mime_type,
                    "position": self._vec3(sticker.get("position"), [0.0, 0.0, 0.0]),
                    "rotation": self._vec3(sticker.get("rotation"), [0.0, 0.0, 0.0]),
                    "targetMeshName": sticker.get("targetMeshName") or "",
                    "width": width,
                    "height": height,
                    "offset": self._number(sticker.get("offset"), 0.004, minimum=0.0, maximum=0.1),
                    "projectionDepth": self._number(
                        sticker.get("projectionDepth"),
                        max(scale * 1.5, 0.05),
                        minimum=0.01,
                        maximum=10.0,
                    ),
                    "subdivisions": int(
                        self._number(sticker.get("subdivisions"), 32, minimum=4, maximum=128)
                    ),
                }
            )
        return prepared

    def _write_sticker_image(self, image_url: str, output_dir: Path, basename: str) -> tuple[Path, str]:
        match = DATA_URI_RE.match(image_url.strip())
        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sticker images must be embedded PNG, JPEG, or SVG data URIs.",
            )

        mime_type = match.group("mime").lower()
        extension = MIME_EXTENSIONS[mime_type]
        meta = match.group("meta").lower()
        payload = match.group("data")
        try:
            data = (
                base64.b64decode(payload, validate=True)
                if ";base64" in meta
                else unquote_to_bytes(payload)
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sticker data URI could not be decoded.",
            ) from exc

        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sticker image is empty.",
            )
        if len(data) > MAX_STICKER_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Sticker image exceeds the 5 MB export limit.",
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = output_dir / f"{basename}{extension}"
        image_path.write_bytes(data)
        return image_path, mime_type

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")[:80] or "sticker"

    def _number(self, value: Any, default: float, minimum: float, maximum: float) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return min(maximum, max(minimum, number))

    def _vec3(self, value: Any, default: list[float]) -> list[float]:
        if not isinstance(value, list | tuple) or len(value) != 3:
            return default
        return [self._number(item, fallback, minimum=-100.0, maximum=100.0) for item, fallback in zip(value, default)]

    def _write_blender_script(self, path: Path) -> None:
        path.write_text(
            r'''
import json
import pathlib
import sys
import traceback

import bpy
import mathutils


def patch_numpy_compat():
    try:
        import numpy as np
    except Exception:
        return

    aliases = {
        "bool": bool,
        "int": int,
        "float": float,
        "complex": complex,
        "object": object,
        "str": str,
    }
    for name, value in aliases.items():
        if name not in np.__dict__:
            setattr(np, name, value)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_model(path):
    patch_numpy_compat()
    bpy.ops.import_scene.gltf(filepath=str(path))


def export_obj(path):
    if hasattr(bpy.ops.wm, "obj_export"):
        try:
            bpy.ops.wm.obj_export(
                filepath=str(path),
                export_materials=True,
                path_mode="COPY",
            )
        except TypeError:
            bpy.ops.wm.obj_export(filepath=str(path), export_materials=True)
    else:
        bpy.ops.export_scene.obj(
            filepath=str(path),
            use_materials=True,
            path_mode="COPY",
        )


def mesh_objects():
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]


def find_target_mesh(target_name):
    candidates = [
        obj for obj in mesh_objects()
        if not obj.name.startswith("decal_") and not obj.name.startswith("svg_decal_")
    ]
    if not candidates:
        raise RuntimeError("Imported model contains no target mesh.")
    if target_name:
        for obj in candidates:
            if obj.name == target_name or obj.data.name == target_name:
                return obj
            if obj.name.startswith(target_name):
                return obj
    return max(candidates, key=lambda item: len(item.data.vertices))


def set_optional(obj, name, value):
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def create_image_material(decal):
    image = bpy.data.images.load(decal["imagePath"], check_existing=True)
    material = bpy.data.materials.new(f"decal_{decal['id']}_material")
    material.use_nodes = True
    material.blend_method = "BLEND"
    material.diffuse_color = (1, 1, 1, 1)
    set_optional(material, "show_transparent_back", True)

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texture_node = nodes.new("ShaderNodeTexImage")
    texture_node.image = image
    if bsdf:
        links.new(texture_node.outputs["Color"], bsdf.inputs["Base Color"])
        if "Alpha" in bsdf.inputs:
            links.new(texture_node.outputs["Alpha"], bsdf.inputs["Alpha"])
            bsdf.inputs["Alpha"].default_value = 1.0
    return material


def create_grid_object(decal):
    cuts = max(4, min(128, int(decal["subdivisions"])))
    width = float(decal["width"])
    height = float(decal["height"])
    vertices = []
    faces = []
    uvs = []

    for row in range(cuts + 1):
        v = row / cuts
        y = (v - 0.5) * height
        for col in range(cuts + 1):
            u = col / cuts
            x = (u - 0.5) * width
            vertices.append((x, y, 0.0))
            uvs.append((u, v))

    row_width = cuts + 1
    for row in range(cuts):
        for col in range(cuts):
            a = row * row_width + col
            b = a + 1
            c = a + row_width
            d = c + 1
            faces.append((a, b, d, c))

    mesh = bpy.data.meshes.new(f"decal_{decal['id']}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = uvs[vertex_index]

    obj = bpy.data.objects.new(f"decal_{decal['id']}", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(create_image_material(decal))
    return obj


def import_svg_object(decal):
    try:
        bpy.ops.preferences.addon_enable(module="io_curve_svg")
    except Exception:
        pass

    before = set(bpy.context.scene.objects)
    bpy.ops.import_curve.svg(filepath=decal["imagePath"])
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    if not imported:
        raise RuntimeError(f"SVG decal {decal['id']} imported no objects.")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in imported:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = imported[0]
    bpy.ops.object.convert(target="MESH")
    converted = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not converted:
        raise RuntimeError(f"SVG decal {decal['id']} converted no mesh.")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in converted:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = converted[0]
    if len(converted) > 1:
        bpy.ops.object.join()

    obj = bpy.context.view_layer.objects.active
    obj.name = f"svg_decal_{decal['id']}"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    normalize_svg_mesh(obj, float(decal["width"]), float(decal["height"]))
    return obj


def normalize_svg_mesh(obj, width, height):
    vertices = obj.data.vertices
    if not vertices:
        return

    xs = [vertex.co.x for vertex in vertices]
    ys = [vertex.co.y for vertex in vertices]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    current_width = max(max_x - min_x, 0.0001)
    current_height = max(max_y - min_y, 0.0001)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    scale = min(width / current_width, height / current_height)

    for vertex in vertices:
        vertex.co.x = (vertex.co.x - center_x) * scale
        vertex.co.y = (vertex.co.y - center_y) * scale
        vertex.co.z = 0.0
    obj.data.update()


def subdivide_mesh(obj, subdivisions):
    cuts = max(1, min(8, int(subdivisions) // 16))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=cuts)
    bpy.ops.object.mode_set(mode="OBJECT")


def set_decal_transform(obj, decal):
    obj.location = mathutils.Vector(decal["position"])
    obj.rotation_euler = mathutils.Euler(decal["rotation"], "XYZ")


def apply_shrinkwrap(obj, target, decal):
    modifier = obj.modifiers.new("surface_project", "SHRINKWRAP")
    modifier.target = target
    modifier.wrap_method = "PROJECT"
    modifier.offset = float(decal["offset"])
    set_optional(modifier, "wrap_mode", "ABOVE_SURFACE")
    set_optional(modifier, "project_limit", float(decal["projectionDepth"]))
    set_optional(modifier, "use_project_x", False)
    set_optional(modifier, "use_project_y", False)
    set_optional(modifier, "use_project_z", True)
    set_optional(modifier, "use_negative_direction", True)
    set_optional(modifier, "use_positive_direction", True)
    set_optional(modifier, "use_invert_cull", False)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def create_decal(decal):
    target = find_target_mesh(decal.get("targetMeshName", ""))
    if decal["mimeType"] == "image/svg+xml":
        obj = import_svg_object(decal)
        subdivide_mesh(obj, decal["subdivisions"])
    else:
        obj = create_grid_object(decal)
    set_decal_transform(obj, decal)
    apply_shrinkwrap(obj, target, decal)


try:
    argv = sys.argv[sys.argv.index("--") + 1:]
    source_glb = pathlib.Path(argv[0])
    output_dir = pathlib.Path(argv[1])
    manifest_path = pathlib.Path(argv[2])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    clear_scene()
    import_model(source_glb)
    for decal in manifest["stickers"]:
        create_decal(decal)

    bpy.ops.export_scene.gltf(
        filepath=str(output_dir / "final_shoe.glb"),
        export_format="GLB",
    )
    export_obj(output_dir / "final_shoe.obj")
except Exception:
    traceback.print_exc()
    sys.exit(1)
'''.lstrip(),
            encoding="utf-8",
        )
