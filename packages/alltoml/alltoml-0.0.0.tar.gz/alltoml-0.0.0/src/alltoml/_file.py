__all__ = ["load_from_file"]

import tomllib
from pathlib import Path
from typing import Any
from typing import Callable


def load_from_file(
    base_path: Path,
    *,
    name: Path = Path("config.toml"),
    on_failure: Callable[[Path], None] = lambda p: None,
) -> dict[str, Any]:
    file_path = base_path / name
    try:
        with open(file_path, "rb") as file:
            return tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        on_failure(file_path)
    return {}
