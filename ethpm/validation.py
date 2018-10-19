import re
from typing import Any, List
from urllib import parse

from eth_utils import (
    decode_hex,
    is_address,
    is_canonical_address,
    is_checksum_address,
    is_text,
    keccak,
    to_hex,
)
from web3 import Web3

from ethpm.constants import PACKAGE_NAME_REGEX, REGISTRY_URI_SCHEME
from ethpm.exceptions import ValidationError
from ethpm.utils.chains import check_if_chain_matches_chain_uri
from ethpm.utils.ipfs import is_ipfs_uri
from ethpm.utils.registry import is_ens_domain


def validate_address(address: Any) -> None:
    """
    Raise a ValidationError if an address is not canonicalized.
    """
    if not is_address(address):
        raise ValidationError(f"Expected an address, got: {address}")
    if not is_canonical_address(address):
        raise ValidationError(
            "Py-EthPM library only accepts canonicalized addresses. "
            f"{address} is not in the accepted format."
        )


def validate_package_version(version: Any) -> None:
    """
    Validates that a package version is of text type.
    """
    if not is_text(version):
        raise ValidationError(
            f"Expected a version of text type, instead received {type(version)}."
        )


def validate_empty_bytes(offset: int, length: int, bytecode: bytes) -> None:
    """
    Validates that segment [`offset`:`offset`+`length`] of
    `bytecode` is comprised of empty bytes (b'\00').
    """
    slot_length = offset + length
    slot = bytecode[offset:slot_length]
    if slot != bytearray(length):
        raise ValidationError(
            f"Bytecode segment: [{offset}:{slot_length}] is not comprised of empty bytes, "
            f"rather: {slot}."
        )


def validate_package_name(pkg_name: str) -> None:
    """
    Raise an exception if the value is not a valid package name
    as defined in the EthPM-Spec.
    """
    if not bool(re.match(PACKAGE_NAME_REGEX, pkg_name)):
        raise ValidationError(f"{pkg_name} is not a valid package name.")


def validate_manifest_version(version: str) -> None:
    """
    Raise an exception if the version is not "2".
    """
    if not version == "2":
        raise ValidationError(
            f"Py-EthPM does not support the provided specification version: {version}"
        )


def validate_ipfs_uri(uri: str) -> None:
    """
    Raise an exception if the provided URI is not a valid IPFS URI.
    """
    if not is_ipfs_uri(uri):
        raise ValidationError(f"URI: {uri} is not a valid IPFS URI.")


def validate_build_dependency(key: str, uri: str) -> None:
    """
    Raise an exception if the key in dependencies is not a valid package name,
    or if the value is not a valid IPFS URI.
    """
    validate_package_name(key)
    validate_ipfs_uri(uri)


def is_valid_registry_uri(uri: str) -> bool:
    """
    Return a boolean indicating whether `uri` argument
    conforms to the Registry URI scheme.
    """
    try:
        validate_registry_uri(uri)
    except ValidationError:
        return False
    else:
        return True


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


def validate_uri_contents(contents: bytes, validation_hash: str) -> None:
    """
    Validate that the keccak(contents) matches the validation_hash.
    """
    hashed_contents = keccak(contents)
    decoded_validation = decode_hex(validation_hash)
    if hashed_contents != decoded_validation:
        raise ValidationError(
            "Invalid content-addressed URI. "
            f"Validation hash:{to_hex(decoded_validation)} does not match the "
            f"hash of URI contents: {to_hex(hashed_contents)}."
        )
