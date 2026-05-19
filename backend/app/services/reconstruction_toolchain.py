import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class ToolStatus:
    name: str
    required: bool
    available: bool
    path: str | None
    configured_value: str
    hint: str


@dataclass(frozen=True)
class ResourceStatus:
    name: str
    ok: bool
    available: float | None
    required: float
    unit: str
    message: str


@dataclass(frozen=True)
class ToolchainReadiness:
    ready: bool
    message: str
    tools: list[ToolStatus]
    resources: list[ResourceStatus]
    settings: dict[str, float | int | bool | str]
    missing_tools: list[str]
    blocking_reasons: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ReconstructionToolchainService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def check(self) -> ToolchainReadiness:
        tools = self._tool_statuses()
        resources = self._resource_statuses()
        missing_tools = [tool.name for tool in tools if tool.required and not tool.available]
        blocking_reasons = []

        if not self.settings.enable_real_reconstruction:
            blocking_reasons.append("Real reconstruction is disabled by ENABLE_REAL_RECONSTRUCTION=false.")
        if missing_tools:
            blocking_reasons.append(f"Missing required tools: {', '.join(missing_tools)}.")
        blocking_reasons.extend(resource.message for resource in resources if not resource.ok)

        ready = not blocking_reasons
        message = (
            "Reconstruction toolchain is ready."
            if ready
            else "Reconstruction is not ready: " + " ".join(blocking_reasons)
        )
        return ToolchainReadiness(
            ready=ready,
            message=message,
            tools=tools,
            resources=resources,
            settings=self._public_settings(),
            missing_tools=missing_tools,
            blocking_reasons=blocking_reasons,
        )

    def assert_ready(self) -> None:
        readiness = self.check()
        if not readiness.ready:
            raise RuntimeError(readiness.message)

    def _tool_statuses(self) -> list[ToolStatus]:
        return [
            self._binary_status(
                name="ffmpeg",
                configured_value=self.settings.ffmpeg_bin,
                hint="Install ffmpeg or set FFMPEG_BIN.",
            ),
            self._binary_status(
                name="colmap",
                configured_value=self.settings.colmap_bin,
                hint="Install COLMAP or set COLMAP_BIN.",
            ),
            *[
                self._openmvs_status(binary)
                for binary in [
                    "InterfaceCOLMAP",
                    "DensifyPointCloud",
                    "ReconstructMesh",
                    "RefineMesh",
                    "TextureMesh",
                ]
            ],
            self._binary_status(
                name="blender",
                configured_value=self.settings.blender_bin,
                hint="Install Blender or set BLENDER_BIN.",
            ),
        ]

    def _binary_status(self, name: str, configured_value: str, hint: str) -> ToolStatus:
        path = shutil.which(configured_value)
        return ToolStatus(
            name=name,
            required=True,
            available=path is not None,
            path=path,
            configured_value=configured_value,
            hint=hint,
        )

    def _openmvs_status(self, binary: str) -> ToolStatus:
        configured_value = binary
        candidate_path = None
        if self.settings.openmvs_bin_dir:
            candidate = Path(self.settings.openmvs_bin_dir) / binary
            configured_value = str(candidate)
            if candidate.exists():
                candidate_path = str(candidate)
        else:
            candidate_path = shutil.which(binary)

        return ToolStatus(
            name=binary,
            required=True,
            available=candidate_path is not None,
            path=candidate_path,
            configured_value=configured_value,
            hint="Install OpenMVS or set OPENMVS_BIN_DIR to the folder containing OpenMVS binaries.",
        )

    def _resource_statuses(self) -> list[ResourceStatus]:
        memory_available_gb = self._available_memory_gb()
        memory_required_gb = self.settings.reconstruction_min_available_memory_gb
        storage_free_gb = self._storage_free_gb(self.settings.resolved_storage_root)
        storage_required_gb = self.settings.reconstruction_min_free_storage_gb

        return [
            self._resource_status(
                name="available_memory",
                available=memory_available_gb,
                required=memory_required_gb,
                unit="GiB",
                low_message="Available RAM is below the configured reconstruction safety threshold.",
            ),
            self._resource_status(
                name="storage_free",
                available=storage_free_gb,
                required=storage_required_gb,
                unit="GiB",
                low_message="Free storage is below the configured reconstruction safety threshold.",
            ),
        ]

    def _resource_status(
        self,
        name: str,
        available: float | None,
        required: float,
        unit: str,
        low_message: str,
    ) -> ResourceStatus:
        if available is None:
            return ResourceStatus(
                name=name,
                ok=True,
                available=None,
                required=required,
                unit=unit,
                message=f"{name} could not be measured; continuing without this guard.",
            )
        ok = available >= required
        message = (
            f"{name} OK: {available:.1f} {unit} available."
            if ok
            else f"{low_message} Required {required:.1f} {unit}, available {available:.1f} {unit}."
        )
        return ResourceStatus(
            name=name,
            ok=ok,
            available=round(available, 2),
            required=required,
            unit=unit,
            message=message,
        )

    def _available_memory_gb(self) -> float | None:
        meminfo = Path("/proc/meminfo")
        if not meminfo.exists():
            return None
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1]) / 1024 / 1024
        return None

    def _storage_free_gb(self, storage_root: Path) -> float | None:
        check_path = storage_root
        while not check_path.exists() and check_path != check_path.parent:
            check_path = check_path.parent
        try:
            usage = shutil.disk_usage(check_path)
        except OSError:
            return None
        return usage.free / 1024 / 1024 / 1024

    def _public_settings(self) -> dict[str, float | int | bool | str]:
        return {
            "enabled": self.settings.enable_real_reconstruction,
            "frameFps": self.settings.reconstruction_frame_fps,
            "maxFramesPerPass": self.settings.reconstruction_max_frames_per_pass,
            "minBrightness": self.settings.reconstruction_min_brightness,
            "minSharpness": self.settings.reconstruction_min_sharpness,
            "duplicateHammingThreshold": self.settings.reconstruction_duplicate_hamming_threshold,
            "commandTimeoutSeconds": self.settings.reconstruction_command_timeout_seconds,
            "maxThreads": self.settings.reconstruction_max_threads,
            "minAvailableMemoryGb": self.settings.reconstruction_min_available_memory_gb,
            "minFreeStorageGb": self.settings.reconstruction_min_free_storage_gb,
        }
