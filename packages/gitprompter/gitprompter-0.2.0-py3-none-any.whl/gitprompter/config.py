from dataclasses import dataclass, fields
from typing import Literal, Self
from pathlib import Path
import tomllib

class PyprojectTomlConfig:
    name: str

    @classmethod
    def load_config(cls) -> None:

        current_dir = Path.cwd()
        config_file = None

        for path in [current_dir] + list(current_dir.parents):
            potential_file = path / "pyproject.toml"
            if potential_file.exists():
                config_file = potential_file
                break

        if config_file:
            try:
                with open(config_file, 'rb') as f:
                    data = tomllib.load(f)
                tool_config = data.get('tool', {}).get(cls.name, {})

                # Программно установим значения атрибутов, если они есть в tool_config
                for field in fields(cls):
                    if field.name in tool_config:
                        setattr(cls, field.name, tool_config[field.name])

            except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError):
                pass


@dataclass
class GitPrompterConfig(PyprojectTomlConfig):
    def __init__(self):
        self.load_config()

    name ='gitprompter'

    style: Literal["feature", "conventional"] = "conventional"
    to_file: bool = False
    language: str = "ru"
    default_branch: str = "main"

