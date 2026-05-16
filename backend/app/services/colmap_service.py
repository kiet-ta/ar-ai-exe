import shutil
from pathlib import Path

from app.core.config import get_settings


class ColmapService:
    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return shutil.which(self.settings.colmap_bin) is not None

    def feature_extraction_command(self, image_path: Path, database_path: Path) -> list[str]:
        return [
            self.settings.colmap_bin,
            "feature_extractor",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_path),
        ]

    def matching_command(self, database_path: Path) -> list[str]:
        return [
            self.settings.colmap_bin,
            "exhaustive_matcher",
            "--database_path",
            str(database_path),
        ]
