import os

from typing import Type

from ethpm.backends.base import BaseURIBackend
from ethpm.utils.module_loading import import_string


DEFAULT_URI_BACKEND = "ethpm.backends.ipfs.IPFSGatewayBackend"


def get_uri_backend(import_path: str = None) -> BaseURIBackend:
    """
    Return the `BaseURIBackend` class specified by import_path, default, or env variable.
    """
    backend_class = get_uri_backend_class(import_path)
    return backend_class()


def get_uri_backend_class(import_path: str = None) -> Type[BaseURIBackend]:
    if import_path is None:
        import_path = os.environ.get("ETHPM_URI_BACKEND_CLASS", DEFAULT_URI_BACKEND)
    return import_string(import_path)
