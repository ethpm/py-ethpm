import json

from typing import (
    Any,
    Dict,
)

from urllib import parse

from eth_utils import to_bytes

from web3.main import Web3

from ethpm import ASSETS_DIR


def is_ens_domain(authority: str) -> bool:
    """
    Return false if authority is not a valid ENS domain.
    """
    # check that authority ends with the tld '.eth'
    # check that there are either 2 or 3 subdomains in the authority
    # i.e. zeppelinos.eth or packages.zeppelinos.eth
    if authority[-4:] != '.eth' or len(authority.split('.')) not in [2, 3]:
        return False
    return True


def fetch_standard_registry_abi() -> Dict[str, Any]:
    """
    Return the standard Registry ABI to interact with a deployed Registry.
    TODO: Update once the standard is finalized via ERC process.
    """
    with open(str(ASSETS_DIR / 'registry_abi.json')) as file_obj:
        return json.load(file_obj)


REGISTRY_ABI = fetch_standard_registry_abi()


def lookup_manifest_uri_located_at_registry_uri(registry_uri: str, w3: Web3) -> str:
    """
    Return a manifest URI associated with a package identified by a valid registry URI.
    """
    parsed_uri = parse.urlparse(registry_uri)
    authority = parsed_uri.netloc
    pkg_name = to_bytes(text=parsed_uri.path.strip('/'))
    registry = w3.eth.contract(
        address=authority,
        abi=REGISTRY_ABI,
    )
    manifest_uri = registry.functions.lookupPackage(pkg_name).call()
    return manifest_uri
