__all__ = ["load"]

import os
import re
import sys
from logging import getLogger
from pathlib import Path
from typing import Any
from typing import Mapping

from deep_chainmap import DeepChainMap
from platformdirs import user_data_dir

from ._argv import load_from_argv
from ._environ import load_from_environ
from ._file import load_from_file

_log = getLogger("alltoml")


def load(
    application_name: str,
    application_author: str,
    *,
    default_settings: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    if default_settings is None:
        default_settings = {}
    else:
        default_settings = {**default_settings}
    assert isinstance(default_settings, dict)

    if application_name.strip():
        base_env_prefix = re.sub(r"[\-\s_]+", "_", application_name.strip()).upper()
        environ_prefix = f"{base_env_prefix}_CONFIG."
        file_environ_key = f"{base_env_prefix}_CONFIG"
    else:
        environ_prefix = "CONFIG."
        file_environ_key = "CONFIG"

    file_path: Path | None = None
    # try to find the file path in the environ
    try:
        file_path = Path(os.environ[file_environ_key])
    except KeyError:
        pass
    # try to find the file path in the argv, this will take precedence of the one found in environ
    #
    # we remove the arguments from the argv list that load_from_argv will scan so that we don't get
    # errors about extra arguments
    argv = sys.argv[1:]
    for i in range(len(argv)):
        if argv[i] == "--config":
            try:
                file_path = Path(argv[i + 1])
            except IndexError:
                _log.error("argument %r has no value", "--config")
                sys.exit(1)
            argv = [*argv[:i], *argv[i + 2 :]]
            break
    # try to load file settings from the path specified by either the environ or argv
    if file_path is None:
        file_settings = {}
    else:
        file_base_path = file_path.parent
        file_name = Path(file_path.name)
        file_settings = load_from_file(file_base_path, name=file_name, on_failure=_file_on_failure)

    user_file_settings = load_from_file(
        Path(user_data_dir(application_name, application_author)), on_failure=_file_on_failure
    )
    cwd_file_settings = load_from_file(Path("."), on_failure=_file_on_failure)
    environ_settings = load_from_environ(prefix=environ_prefix, on_failure=_environ_on_failure)
    argv_settings = load_from_argv(argv, on_extra=_argv_on_extra, on_failure=_argv_on_failure)

    return DeepChainMap(
        argv_settings,
        file_settings,
        cwd_file_settings,
        user_file_settings,
        environ_settings,
        default_settings,
    )


def _environ_on_failure(key: str, value: str) -> None:
    _log.warning("ignoring invalid environment variable: %r", key)


def _file_on_failure(file_path: Path) -> None:
    _log.warning("ignoring invalid config file: %r", str(file_path))


def _argv_on_extra(argument: str) -> None:
    _log.error("argument %r was unexpected", argument)
    sys.exit(1)


def _argv_on_failure(argument: str, value: str | None) -> None:
    _log.warning("ignoring invalid argument: %r", argument)
