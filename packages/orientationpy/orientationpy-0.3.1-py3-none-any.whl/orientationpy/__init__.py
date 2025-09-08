try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .analyse import *
from .generate import *
from .main import *
from .plotting import *
