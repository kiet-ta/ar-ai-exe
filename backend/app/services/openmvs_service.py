import shutil
from pathlib import Path

from app.core.config import get_settings


class OpenMVSService:
    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        if not self.settings.openmvs_bin_dir:
            return False
        return Path(self.settings.openmvs_bin_dir).exists()

    def densify_command(self, scene_path: Path) -> list[str]:
        binary = shutil.which("DensifyPointCloud") or "DensifyPointCloud"
        return [binary, str(scene_path)]
