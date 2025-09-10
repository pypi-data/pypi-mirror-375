from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dellin")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .api import DellinOrdersClient

__all__ = ["DellinOrdersClient", "__version__"]
