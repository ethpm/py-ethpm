from typing import Iterable, Type

from ethpm.backends.base import BaseURIBackend
from ethpm.backends.ipfs import (
    DummyIPFSBackend,
    InfuraIPFSBackend,
    IPFSGatewayBackend,
    LocalIPFSBackend,
    get_ipfs_backend_class,
)
from ethpm.backends.registry import RegistryURIBackend
from ethpm.exceptions import CannotHandleURI

URI_BACKENDS = [
    IPFSGatewayBackend,
    InfuraIPFSBackend,
    DummyIPFSBackend,
    LocalIPFSBackend,
    RegistryURIBackend,
]


def get_backends_for_uri(uri: str) -> Iterable[Type[BaseURIBackend]]:
    default_ipfs = get_ipfs_backend_class()
    good_backends = [
        backend
        for backend in URI_BACKENDS
        # type ignored because of conflict with instantiating BaseURIBackend
        if backend().can_handle_uri(uri)  # type: ignore
    ]
    if default_ipfs in good_backends:
        # Move default to front of the list of good backends.
        good_backends.insert(0, good_backends.pop(good_backends.index(default_ipfs)))
    if not good_backends:
        raise CannotHandleURI(
            "URI: {0} cannot be handled by any of the available backends.".format(uri)
        )
    return good_backends
