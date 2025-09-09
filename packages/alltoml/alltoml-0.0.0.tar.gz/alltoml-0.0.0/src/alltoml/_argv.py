__all__ = ["load_from_argv"]

import sys
from itertools import islice
from typing import Any
from typing import Callable
from typing import Iterable

from ._parse import store_settings


def load_from_argv(
    argv: Iterable[str] | None = None,
    *,
    on_extra: Callable[[str], None] = lambda n: None,
    on_failure: Callable[[str, str | None], None] = lambda n, v: None,
    prefix: str = "--config.",
) -> dict[str, Any]:
    settings: dict[str, Any] = {}

    if argv is None:
        argv = sys.argv[1:]

    argv_i = iter(argv)
    while True:
        try:
            arg = next(argv_i)
        except StopIteration:
            break
        if arg.startswith(prefix):
            raw_key = arg[len(prefix) :]
            try:
                raw_value = next(argv_i)
            except StopIteration:
                on_failure(arg, None)
                continue
            store_settings(settings, raw_key, raw_value, lambda: on_failure(arg, raw_value))
        else:
            on_extra(arg)

    return settings
