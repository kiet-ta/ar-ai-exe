import shutil
from pathlib import Path

from app.core.config import get_settings


class OpenMVSService:
    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return all(self.binary(name) for name in self.required_binaries())

    def required_binaries(self) -> list[str]:
        return [
            "InterfaceCOLMAP",
            "DensifyPointCloud",
            "ReconstructMesh",
            "RefineMesh",
            "TextureMesh",
        ]

    def binary(self, name: str) -> str | None:
        if self.settings.openmvs_bin_dir:
            candidate = Path(self.settings.openmvs_bin_dir) / name
            if candidate.exists():
                return str(candidate)
        return shutil.which(name)

    def require_binary(self, name: str) -> str:
        binary = self.binary(name)
        if not binary:
            raise RuntimeError(
                f"OpenMVS binary '{name}' was not found. Install OpenMVS or set OPENMVS_BIN_DIR."
            )
        return binary

    def interface_colmap_command(
        self,
        sparse_model_path: Path,
        image_path: Path,
        scene_path: Path,
    ) -> list[str]:
        return [
            self.require_binary("InterfaceCOLMAP"),
            "-i",
            str(sparse_model_path),
            "-o",
            str(scene_path),
            "--image-folder",
            str(image_path),
        ]

    def densify_command(self, scene_path: Path, dense_scene_path: Path) -> list[str]:
        return [
            self.require_binary("DensifyPointCloud"),
            str(scene_path),
            "-o",
            str(dense_scene_path),
        ]

    def reconstruct_mesh_command(self, dense_scene_path: Path, mesh_scene_path: Path) -> list[str]:
        return [
            self.require_binary("ReconstructMesh"),
            str(dense_scene_path),
            "-o",
            str(mesh_scene_path),
        ]

    def refine_mesh_command(self, mesh_scene_path: Path, refined_scene_path: Path) -> list[str]:
        return [
            self.require_binary("RefineMesh"),
            str(mesh_scene_path),
            "-o",
            str(refined_scene_path),
        ]

    def texture_mesh_command(self, refined_scene_path: Path, textured_scene_path: Path) -> list[str]:
        return [
            self.require_binary("TextureMesh"),
            str(refined_scene_path),
            "-o",
            str(textured_scene_path),
            "--export-type",
            "obj",
        ]
