from abc import abstractmethod

from eth_utils import to_bytes
import requests

from ethpm import V2_PACKAGES_DIR
from ethpm.backends.base import BaseURIBackend
from ethpm.constants import INFURA_GATEWAY_PREFIX, IPFS_GATEWAY_PREFIX
from ethpm.utils.ipfs import extract_ipfs_path_from_uri, is_ipfs_uri


class BaseIPFSBackend(BaseURIBackend):
    """
    Base class for all URIs with an IPFS scheme.
    """

    def can_handle_uri(self, uri: str) -> bool:
        """
        Return a bool indicating whether or not this backend
        is capable of serving the content at the URI.
        """
        return is_ipfs_uri(uri)


class IPFSOverHTTPBackend(BaseIPFSBackend):
    """
    Base class for all IPFS URIs served over an http connection.

    All subclasses must implement: base_uri
    """

    def fetch_uri_contents(self, uri: str) -> bytes:
        ipfs_hash = extract_ipfs_path_from_uri(uri)
        gateway_uri = self.base_uri + ipfs_hash
        response = requests.get(gateway_uri)
        response.raise_for_status()
        return response.content

    @property
    @abstractmethod
    def base_uri(self) -> str:
        pass


class IPFSGatewayBackend(IPFSOverHTTPBackend):
    """
    Backend class for all IPFS URIs served over the IPFS gateway.
    """

    @property
    def base_uri(self) -> str:
        return IPFS_GATEWAY_PREFIX


class InfuraIPFSBackend(IPFSOverHTTPBackend):
    """
    Backend class for all IPFS URIs served over the Infura IFPS gateway.
    """

    @property
    def base_uri(self) -> str:
        return INFURA_GATEWAY_PREFIX


class DummyIPFSBackend(BaseIPFSBackend):
    """
    Backend class to serve IPFS URIs without having to make an HTTP request.
    Used primarily for testing purposes, returns a locally stored manifest or contract.
    ---
    `ipfs_uri` can either be:
    - Valid IPFS URI -> safe-math-lib manifest (ALWAYS)
    - Path to manifest/contract in V2_PACKAGES_DIR -> defined manifest/contract
    """

    def fetch_uri_contents(self, ipfs_uri: str) -> bytes:
        if is_ipfs_uri(ipfs_uri):
            with open(
                str(V2_PACKAGES_DIR / "safe-math-lib" / "1.0.0.json")
            ) as file_obj:
                contents = file_obj.read()
        else:
            with open(str(V2_PACKAGES_DIR / ipfs_uri)) as file_obj:
                contents = file_obj.read()
        return to_bytes(text=contents)

    def can_handle_uri(self, uri: str) -> bool:
        if is_ipfs_uri(uri):
            return True
        path = V2_PACKAGES_DIR / uri
        return path.exists()


class LocalIPFSBackend(BaseIPFSBackend):
    """
    Backend class for all IPFS URIs served through a direct connection to an IPFS node.
    TODO - implement
    """

    def can_handle_uri(self, ipfs_uri: str) -> bool:
        return False

    def fetch_uri_contents(self, ipfs_uri: str) -> bytes:
        pass
