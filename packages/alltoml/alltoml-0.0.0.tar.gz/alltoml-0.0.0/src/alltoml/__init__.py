__all__ = ["load", "load_from_argv", "load_from_environ", "load_from_file"]


from ._argv import load_from_argv
from ._environ import load_from_environ
from ._file import load_from_file
from ._load import load
