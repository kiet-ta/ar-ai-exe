import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.return_code == 0


class CommandRunner:
    def run(
        self,
        command: list[str],
        log_path: Path | None = None,
        cwd: Path | None = None,
        timeout: int | None = None,
        env: dict[str, str] | None = None,
    ) -> CommandResult:
        try:
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)
            result = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                cwd=cwd,
                timeout=timeout,
                env=merged_env,
            )
            command_result = CommandResult(
                command=command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except subprocess.TimeoutExpired as exc:
            command_result = CommandResult(
                command=command,
                return_code=124,
                stdout=exc.stdout or "",
                stderr=f"Command timed out after {timeout} seconds.",
            )
        if log_path:
            self.append_log(log_path, command_result)
        return command_result

    def append_log(self, log_path: Path, result: CommandResult) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"$ {' '.join(result.command)}\n")
            log_file.write(f"return_code={result.return_code}\n")
            if result.stdout:
                log_file.write(result.stdout)
                log_file.write("\n")
            if result.stderr:
                log_file.write(result.stderr)
                log_file.write("\n")
