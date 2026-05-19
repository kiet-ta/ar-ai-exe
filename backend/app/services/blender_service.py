import shutil
from pathlib import Path

from app.core.config import get_settings


class BlenderService:
    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return shutil.which(self.settings.blender_bin) is not None

    def require_available(self) -> str:
        binary = shutil.which(self.settings.blender_bin)
        if not binary:
            raise RuntimeError(
                f"Blender binary '{self.settings.blender_bin}' was not found. "
                "Install Blender or set BLENDER_BIN."
            )
        return binary

    def cleanup_export_command(self, script_path: Path, input_mesh_path: Path, output_dir: Path) -> list[str]:
        return [
            self.require_available(),
            "--background",
            "--python",
            str(script_path),
            "--",
            str(input_mesh_path),
            str(output_dir),
        ]
