from ethpm.utils.ipfs import is_ipfs_uri
from ethpm.utils.chains import check_if_chain_matches_chain_uri
from ethpm.constants import REGISTRY_URI_SCHEME
from ethpm.exceptions import ValidationError
from ethpm._utils.registry import is_ens_domain
from eth_utils import is_checksum_address
from ethpm.validation.package import validate_package_name
from typing import List

from web3 import Web3
from urllib import parse


def validate_ipfs_uri(uri: str) -> None:
    """
    Raise an exception if the provided URI is not a valid IPFS URI.
    """
    if not is_ipfs_uri(uri):
        raise ValidationError(f"URI: {uri} is not a valid IPFS URI.")


def validate_registry_uri(uri: str) -> None:
    """
    Raise an exception if the URI does not conform to the registry URI scheme.
    """
    parsed = parse.urlparse(uri)
    scheme, authority, pkg_name, query = (
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.query,
    )
    validate_registry_uri_scheme(scheme)
    validate_registry_uri_authority(authority)
    if query:
        validate_registry_uri_version(query)
    validate_package_name(pkg_name[1:])


def validate_registry_uri_authority(auth: str) -> None:
    """
    Raise an exception if the authority is not a valid ENS domain
    or a valid checksummed contract address.
    """
    if is_ens_domain(auth) is False and not is_checksum_address(auth):
        raise ValidationError(f"{auth} is not a valid registry URI authority.")


def validate_registry_uri_scheme(scheme: str) -> None:
    """
    Raise an exception if the scheme is not the valid registry URI scheme ('ercXXX').
    """
    if scheme != REGISTRY_URI_SCHEME:
        raise ValidationError(f"{scheme} is not a valid registry URI scheme.")


def validate_registry_uri_version(query: str) -> None:
    """
    Raise an exception if the version param is malformed.
    """
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    if "version" not in query_dict:
        raise ValidationError(f"{query} is not a correctly formatted version param.")


def validate_single_matching_uri(all_blockchain_uris: List[str], w3: Web3) -> str:
    """
    Return a single block URI after validating that it is the *only* URI in
    all_blockchain_uris that matches the w3 instance.
    """
    matching_uris = [
        uri for uri in all_blockchain_uris if check_if_chain_matches_chain_uri(w3, uri)
    ]

    if not matching_uris:
        raise ValidationError("Package has no matching URIs on chain.")
    elif len(matching_uris) != 1:
        raise ValidationError(
            f"Package has too many ({len(matching_uris)}) matching URIs: {matching_uris}."
        )
    return matching_uris[0]
