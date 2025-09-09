__all__ = ["store_settings"]

from itertools import islice
from tomllib import TOMLDecodeError
from tomllib import loads as toml_loads
from typing import Any
from typing import Callable
from typing import Generator


def store_settings(
    settings: dict[str, Any], raw_key: str, raw_value: str, fail: Callable[[], None]
) -> None:
    try:
        key = tuple(_convert_key(raw_key))
        value = _convert_value(raw_value)
    except ValueError:
        fail()
        return

    target = settings
    for name in islice(key, len(key) - 1):
        try:
            target = target[name]
            if not isinstance(target, dict):
                fail()
                return
        except KeyError:
            target[name] = target = {}
    if key[-1] in target:
        fail()
        return
    target[key[-1]] = value


def _convert_value(raw_value: str) -> Any:
    try:
        result = toml_loads(f"value = {raw_value}")
    except TOMLDecodeError:
        raise ValueError(raw_value)
    if set(result.keys()) != {"value"}:
        raise ValueError(raw_value)
    return result["value"]


def _convert_key(raw_key: str) -> Generator[str, None, None]:
    try:
        result = toml_loads(f"{raw_key} = 0")
    except TOMLDecodeError:
        raise ValueError(raw_key)
    while True:
        if len(result) > 1:
            raise ValueError(raw_key)
        for key, value in result.items():
            yield key
            result = value
        if not isinstance(result, dict):
            if result == 0:
                return
            raise ValueError(raw_key)
