from web3 import Web3

from ethpm.backends.base import BaseURIBackend
from ethpm.backends.ipfs import get_ipfs_backend
from ethpm.exceptions import UriNotSupportedError
from ethpm.utils.registry import lookup_manifest_uri_located_at_registry_uri
from ethpm.validation import is_valid_registry_uri


class RegistryURIBackend(BaseURIBackend):
    """
    Backend class to handle Registry URIs.

    A Registry URI must point towards a valid IPFS URI.

    `RegistryURIBackend` uses IPFS backend set via env variable
    (defaults to InfuraIPFSBackend).
    """

    def can_handle_uri(self, uri: str) -> bool:
        return is_valid_registry_uri(uri)

    def fetch_uri_contents(self, uri: str, w3: Web3) -> bytes:
        """
        Return the contents stored at `uri` assuming `uri`
        is a valid Registry URI pointing towards an IPFS URI.
        Requires a valid web3 instance connected to the chain on which
        the registry lives.
        """
        manifest_uri = lookup_manifest_uri_located_at_registry_uri(uri, w3)
        ipfs_backend = get_ipfs_backend()
        if ipfs_backend.can_handle_uri(manifest_uri):
            manifest_data = ipfs_backend.fetch_uri_contents(manifest_uri, w3)
            return manifest_data
        raise UriNotSupportedError(
            "URI: {0} found at {1} cannot be served with the current IPFS backend: {2}".format(
                manifest_uri, uri, ipfs_backend
            )
        )
