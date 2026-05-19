import shutil
from pathlib import Path

from app.core.config import get_settings


class ColmapService:
    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return shutil.which(self.settings.colmap_bin) is not None

    def require_available(self) -> str:
        binary = shutil.which(self.settings.colmap_bin)
        if not binary:
            raise RuntimeError(
                f"COLMAP binary '{self.settings.colmap_bin}' was not found. "
                "Install COLMAP or set COLMAP_BIN."
            )
        return binary

    def feature_extraction_command(self, image_path: Path, database_path: Path) -> list[str]:
        binary = self.require_available()
        threads = str(max(1, self.settings.reconstruction_max_threads))
        return [
            binary,
            "feature_extractor",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_path),
            "--ImageReader.single_camera",
            "1",
            "--SiftExtraction.use_gpu",
            "0",
            "--SiftExtraction.num_threads",
            threads,
        ]

    def matching_command(self, database_path: Path) -> list[str]:
        binary = self.require_available()
        threads = str(max(1, self.settings.reconstruction_max_threads))
        return [
            binary,
            "exhaustive_matcher",
            "--database_path",
            str(database_path),
            "--SiftMatching.use_gpu",
            "0",
            "--SiftMatching.num_threads",
            threads,
        ]

    def mapper_command(self, image_path: Path, database_path: Path, sparse_path: Path) -> list[str]:
        binary = self.require_available()
        threads = str(max(1, self.settings.reconstruction_max_threads))
        return [
            binary,
            "mapper",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_path),
            "--output_path",
            str(sparse_path),
            "--Mapper.num_threads",
            threads,
        ]

    def model_converter_command(self, input_path: Path, output_path: Path, output_type: str) -> list[str]:
        binary = self.require_available()
        return [
            binary,
            "model_converter",
            "--input_path",
            str(input_path),
            "--output_path",
            str(output_path),
            "--output_type",
            output_type,
        ]
