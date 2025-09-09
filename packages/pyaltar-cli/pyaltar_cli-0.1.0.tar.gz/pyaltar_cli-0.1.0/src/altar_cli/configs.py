from pathlib import Path

from pydantic import BaseModel

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[import]


class Config(BaseModel):
    components_dir: Path


def load_configs() -> Config:
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        raise FileNotFoundError("Unable to locate configuration file.")

    with open(pyproject_file, "rb") as file:
        raw_aether_config: dict = tomllib.load(file).get("tool", {}).get("altar", {})

        raw_components_dir_config: dict = raw_aether_config.get(
            "components_dir", "ui/components/"
        )

    # Decompose raw 'components_dir' configurations.
    parsed_components_dir_config = Path(raw_components_dir_config)

    return Config(components_dir=parsed_components_dir_config)


configs = load_configs()
