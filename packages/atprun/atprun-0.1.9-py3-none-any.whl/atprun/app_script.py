import os
import subprocess

from pydantic import BaseModel


class AtpRunScriptConfig(BaseModel):
    run: str  # TODO: validate len(run) > 0
    name: str | None = None
    # description: str | None = None
    env_var: dict[str, str] | None = None
    # env_files: list[str] | None = None
    # dot_env_group: str | None = None
    # uv_group


class AtpRunScript:
    def __init__(self, name: str, script: AtpRunScriptConfig) -> None:
        self.name: str = name
        self.script: AtpRunScriptConfig = script
        return None

    def _export_env_var(self) -> None:
        if self.script.env_var is not None:
            for key, value in self.script.env_var.items():
                os.environ[key] = value
        return None

    def _command_run(self) -> None:
        command: str = self.script.run
        if len(command) <= 0:
            raise ValueError("No 'run' is empty")
        subprocess.run(
            args=command,
            shell=True,
        )
        return None

    def run(self) -> None:
        self._export_env_var()
        self._command_run()

        return None
