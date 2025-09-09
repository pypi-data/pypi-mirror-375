import os
from pprint import pprint

from atptools import DictDefault
from pydantic import BaseModel

from .app_script import AtpRunScript, AtpRunScriptConfig

default_config_path: str = "./atprun.yml"


class AtpRunConfig(BaseModel):
    scripts: dict[str, AtpRunScriptConfig]
    # pipelines: dict[str, list[str]] = {}


class AtpRunMain:
    def __init__(self) -> None:
        self.config_path: str = ""
        self.config_in: DictDefault = DictDefault()
        self.config: AtpRunConfig | None = None
        self.scripts_run: dict[str, AtpRunScript] = {}
        return None

    def _get_configuration_file_path(self, path: str | None) -> str:
        # Load default value
        self.config_path = default_config_path
        # Load environment variable
        if "ATPRUN_CONFIG_PATH" in os.environ:
            self.config_path = os.environ["ATPRUN_CONFIG_PATH"]
        # Load command line argument
        if path is not None and len(path) > 0:
            self.config_path = path

        return self.config_path

    def load_configuration(self, path: str | None) -> None:
        self._get_configuration_file_path(path=path)

        self.config_in.from_file(path=self.config_path)

        self.config = AtpRunConfig.model_validate(
            obj=self.config_in.to_dict(),
            strict=True,
        )

        # prepare scripts run
        if self.config.scripts is not None:
            for name, script in self.config.scripts.items():
                self.scripts_run[name] = AtpRunScript(
                    name=name,
                    script=script,
                )
        return None

    def script_get(self, name) -> AtpRunScript:
        try:
            return self.scripts_run[name]
        except KeyError as err:
            raise ValueError(f"Script '{name}' not found") from err

    def script_run(self, name: str) -> None:
        script: AtpRunScript = self.script_get(name=name)
        script.run()
        return None
