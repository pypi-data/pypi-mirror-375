from pynetbox.core.query import RequestError, AllocationError, ContentError
from pypeeringmanager.core.api import Api as api

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # For Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"

