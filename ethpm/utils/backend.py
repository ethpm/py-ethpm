from typing import Generator, Type

from eth_utils import to_tuple

from ethpm.backends.base import BaseURIBackend
from ethpm.backends.http import GithubOverHTTPSBackend
from ethpm.backends.ipfs import (
    DummyIPFSBackend,
    InfuraIPFSBackend,
    LocalIPFSBackend,
    get_ipfs_backend_class,
)
from ethpm.backends.registry import RegistryURIBackend
from ethpm.exceptions import CannotHandleURI

URI_BACKENDS = [
    InfuraIPFSBackend,
    DummyIPFSBackend,
    LocalIPFSBackend,
    GithubOverHTTPSBackend,
    RegistryURIBackend,
]


def resolve_uri_contents(uri: str, fingerprint: bool = None) -> bytes:
    resolvable_backends = get_resolvable_backends_for_uri(uri)
    if resolvable_backends:
        for backend in resolvable_backends:
            try:
                contents = backend().fetch_uri_contents(uri)
            except CannotHandleURI:
                continue
            return contents

    translatable_backends = get_translatable_backends_for_uri(uri)
    if translatable_backends:
        if fingerprint:
            raise CannotHandleURI(
                "Registry URIs must point to a resolvable content-addressed URI."
            )
        for backend in translatable_backends:
            package_id = backend().fetch_uri_contents(uri)
            return resolve_uri_contents(package_id, True)

    raise CannotHandleURI(
        f"URI: {uri} cannot be resolved by any of the available backends."
    )


@to_tuple
def get_translatable_backends_for_uri(
    uri: str
) -> Generator[Type[BaseURIBackend], None, None]:
    # type ignored because of conflict with instantiating BaseURIBackend
    for backend in URI_BACKENDS:
        if backend().can_translate_uri(uri):  # type: ignore
            yield backend


@to_tuple
def get_resolvable_backends_for_uri(
    uri: str
) -> Generator[Type[BaseURIBackend], None, None]:
    # special case the default IPFS backend to the first slot.
    default_ipfs = get_ipfs_backend_class()
    if default_ipfs in URI_BACKENDS and default_ipfs().can_resolve_uri(uri):
        yield default_ipfs
    for backend_class in URI_BACKENDS:
        if backend_class is default_ipfs:
            continue
        # type ignored because of conflict with instantiating BaseURIBackend
        elif backend_class().can_resolve_uri(uri):  # type: ignore
            yield backend_class
