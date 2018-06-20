from urllib import parse

from eth_utils import to_bytes

from web3.main import Web3

from ethpm.constants import REGISTRY_ABI


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


def lookup_manifest_uri_located_at_registry_uri(registry_uri: str, w3: Web3) -> str:
    """
    Registry must conform to the ERCXXX.
    """
    parsed = parse.urlparse(registry_uri)
    authority = parsed.netloc
    pkg_name = to_bytes(text=parsed.path[1:])
    registry = w3.eth.contract(
        address=authority,
        abi=REGISTRY_ABI,
    )
    manifest_uri = registry.functions.lookupPackage(pkg_name).call()
    return manifest_uri
