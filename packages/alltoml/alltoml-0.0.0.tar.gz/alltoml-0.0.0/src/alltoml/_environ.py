__all__ = ["load_from_environ"]

import os
from itertools import islice
from os import environ
from re import sub as re_sub
from types import NoneType
from types import UnionType
from typing import Any
from typing import Callable
from typing import Final
from typing import Mapping
from typing import Sequence
from typing import Union
from typing import get_args as get_typing_args
from typing import get_origin as get_typing_origin

from ._parse import store_settings


def load_from_environ(
    environ: Mapping[str, str] | None = None,
    *,
    prefix: str = "CONFIG.",
    on_failure: Callable[[str, str], None] = lambda n, v: None,
) -> dict[str, Any]:
    settings: dict[str, Any] = {}

    if environ is None:
        environ = os.environ

    for key, raw_value in environ.items():
        if key.startswith(prefix):
            raw_key = key[len(prefix) :]
            store_settings(settings, raw_key, raw_value, lambda: on_failure(key, raw_value))

    return settings
