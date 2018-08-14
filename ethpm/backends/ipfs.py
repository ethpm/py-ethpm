from abc import abstractmethod
import os
from pathlib import Path
from typing import Dict, List, Type

from eth_utils import to_bytes
import ipfsapi
import requests

from ethpm import V2_PACKAGES_DIR
from ethpm.backends.base import BaseURIBackend
from ethpm.constants import (
    DEFAULT_IPFS_BACKEND,
    INFURA_GATEWAY_PREFIX,
    IPFS_GATEWAY_PREFIX,
)
from ethpm.exceptions import CannotHandleURI
from ethpm.utils.ipfs import dummy_ipfs_pin, extract_ipfs_path_from_uri, is_ipfs_uri
from ethpm.utils.module_loading import import_string


class BaseIPFSBackend(BaseURIBackend):
    """
    Base class for all URIs with an IPFS scheme.
    """

    def can_resolve_uri(self, uri: str) -> bool:
        """
        Return a bool indicating whether or not this backend
        is capable of serving the content located at the URI.
        """
        return is_ipfs_uri(uri)

    def can_translate_uri(self, uri: str) -> bool:
        """
        Return False. IPFS URIs cannot be used to point
        to another content-addressed URI.
        """
        return False

    @abstractmethod
    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        """
        Pin assets found at `file_or_dir_path` and return a
        list containing pinned asset data.
        """
        pass


class IPFSOverHTTPBackend(BaseIPFSBackend):
    """
    Base class for all IPFS URIs served over an http connection.
    All subclasses must implement: base_uri
    """

    # TODO change to use ipfsapi.Client
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

    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        pass


class IPFSGatewayBackend(IPFSOverHTTPBackend):
    """
    Backend class for all IPFS URIs served over the IPFS gateway.
    """

    @property
    def base_uri(self) -> str:
        return IPFS_GATEWAY_PREFIX

    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        raise NotImplementedError(
            "pin_assets has not been implemented yet for IPFSGatewayBackend"
        )


class InfuraIPFSBackend(IPFSOverHTTPBackend):
    """
    Backend class for all IPFS URIs served over the Infura IFPS gateway.
    """

    def __init__(self) -> None:
        self.client = ipfsapi.Client(self.base_uri, 5001)

    @property
    def base_uri(self) -> str:
        return INFURA_GATEWAY_PREFIX

    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        if file_or_dir_path.is_dir():
            dir_data = self.client.add(str(file_or_dir_path), recursive=True)
            return dir_data
        elif file_or_dir_path.is_file():
            file_data = self.client.add(str(file_or_dir_path), recursive=False)
            return [file_data]
        else:
            raise TypeError(
                "{0} is not a valid file or directory path.".format(file_or_dir_path)
            )


MANIFEST_URIS = {
    "ipfs://QmVu9zuza5mkJwwcFdh2SXBugm1oSgZVuEKkph9XLsbUwg": "standard-token",
    "ipfs://QmeD2s7KaBUoGYTP1eutHBmBkMMMoycdfiyGMx2DKrWXyV": "safe-math-lib",
    "ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW": "owned",
}


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
        pkg_name = MANIFEST_URIS[ipfs_uri]
        with open(str(V2_PACKAGES_DIR / pkg_name / "1.0.0.json")) as file_obj:
            contents = file_obj.read()
        return to_bytes(text=contents)

    def can_resolve_uri(self, uri: str) -> bool:
        return uri in MANIFEST_URIS

    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        """
        Return a dict containing the IPFS hash, file name, and size of a file.
        """
        if file_or_dir_path.is_dir():
            asset_data = [dummy_ipfs_pin(path) for path in file_or_dir_path.glob("*")]
        elif file_or_dir_path.is_file():
            asset_data = [dummy_ipfs_pin(file_or_dir_path)]
        else:
            raise FileNotFoundError(
                "{0} is not a valid file or directory path.".format(file_or_dir_path)
            )
        return asset_data


class LocalIPFSBackend(BaseIPFSBackend):
    """
    Backend class for all IPFS URIs served through a direct connection to an IPFS node.
    Default IPFS port = 5001
    """

    def __init__(self) -> None:
        self.client = ipfsapi.Client("localhost", "5001")

    def fetch_uri_contents(self, ipfs_uri: str) -> bytes:
        ipfs_hash = extract_ipfs_path_from_uri(ipfs_uri)
        try:
            contents = self.client.cat(ipfs_hash)
        except ipfsapi.exceptions.ConnectionError:
            raise CannotHandleURI(
                "Cannot connect to local IPFS node to serve URI: {0}".format(ipfs_uri)
            )
        return contents

    def pin_assets(self, file_or_dir_path: Path) -> List[Dict[str, str]]:
        if file_or_dir_path.is_dir():
            dir_data = self.client.add(str(file_or_dir_path), recursive=True)
            return dir_data
        elif file_or_dir_path.is_file():
            file_data = self.client.add(str(file_or_dir_path))
            return [file_data]
        else:
            raise TypeError(
                "{0} is not a valid file or directory path.".format(file_or_dir_path)
            )


def get_ipfs_backend(import_path: str = None) -> BaseIPFSBackend:
    """
    Return the `BaseIPFSBackend` class specified by import_path, default, or env variable.
    """
    backend_class = get_ipfs_backend_class(import_path)
    return backend_class()


def get_ipfs_backend_class(import_path: str = None) -> Type[BaseIPFSBackend]:
    if import_path is None:
        import_path = os.environ.get("ETHPM_IPFS_BACKEND_CLASS", DEFAULT_IPFS_BACKEND)
    return import_string(import_path)
