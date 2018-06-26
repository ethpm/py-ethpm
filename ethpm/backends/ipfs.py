import json
import requests

from abc import abstractmethod

from ethpm import V2_PACKAGES_DIR

from ethpm.backends.base import BaseURIBackend

from ethpm.utils.ipfs import (
    extract_ipfs_path_from_uri,
    is_ipfs_uri,
)


class BaseIPFSBackend(BaseURIBackend):
    @abstractmethod
    def fetch_ipfs_uri(self, uri: str) -> str:  # or maybe bytes?
        """
        Return the file contents stored at the URI.
        """
        pass


    @abstractmethod
    def can_handle_uri(self, uri: str) -> bool: 
        """
        Return a bool indicating whether or not this backend
        is capable of serving the content at the URI.
        """
        return False


class IPFSOverHTTPBackend(BaseIPFSBackend):

    @property
    def base_uri(self):
        raise AttributeError('Base URI needs to be set by subclass')

    def fetch_ipfs_uri(self, uri):  # , uri):
        ipfs_hash = extract_ipfs_path_from_uri(uri)
        gateway_uri = self.base_uri + ipfs_hash
        response = requests.get(gateway_uri)
        return response.content
    
    def can_handle_uri(self, uri: str) -> bool:
        if not is_ipfs_uri(uri):
            return False
        return True


IPFS_GATEWAY_PREFIX = 'https://gateway.ipfs.io/ipfs/'
INFURA_GATEWAY_PREFIX = 'https://ipfs.infura.io/ipfs/'


class IPFSGatewayBackend(IPFSOverHTTPBackend):
    @property
    def base_uri(self):
        return IPFS_GATEWAY_PREFIX


class InfuraIPFSBackend(IPFSOverHTTPBackend):
    @property
    def base_uri(self):
        return INFURA_GATEWAY_PREFIX


# returns locally stored manifes
class DummyIPFSBackend(BaseIPFSBackend):
    def fetch_ipfs_uri(self):
        with open(str(V2_PACKAGES_DIR / 'owned' / '1.0.0.json')) as file_obj:
            return json.load(file_obj)

    def can_handle_uri(self):
        pass


# knows how to connect to a locally running IPFS node
class LocalIPFSBackend(BaseIPFSBackend):
    pass
