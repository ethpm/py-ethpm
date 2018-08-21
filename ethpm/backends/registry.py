import os
from urllib import parse

from eth_utils import to_bytes
from web3.auto.infura import w3

from ethpm.backends.base import BaseURIBackend
from ethpm.constants import INFURA_API_KEY
from ethpm.utils.registry import fetch_standard_registry_abi
from ethpm.validation import is_valid_registry_uri

# TODO: Update registry ABI once ERC is finalized.
REGISTRY_ABI = fetch_standard_registry_abi()


class RegistryURIBackend(BaseURIBackend):
    """
    Backend class to handle Registry URIs.

    A Registry URI must resolve to a resolvable content-addressed URI.
    """

    def __init__(self) -> None:
        os.environ.setdefault("INFUFA_API_KEY", INFURA_API_KEY)
        self.w3 = w3

    def can_translate_uri(self, uri: str) -> bool:
        return is_valid_registry_uri(uri)

    def can_resolve_uri(self, uri: str) -> bool:
        return False

    def fetch_uri_contents(self, uri: str) -> bytes:
        """
        Return content-addressed URI stored at registry URI.
        """
        parsed_uri = parse.urlparse(uri)
        authority = parsed_uri.netloc
        pkg_name = to_bytes(text=parsed_uri.path.strip("/"))
        registry = self.w3.eth.contract(address=authority, abi=REGISTRY_ABI)
        manifest_uri = registry.functions.lookupPackage(pkg_name).call()
        return manifest_uri
