import re
import semver

from urllib import parse

from typing import List

from eth_utils import (
    is_hex_address,
)

from ethpm.exceptions import UriNotSupportedError


# TODO: update with correct scheme once ERC is completed
REGISTRY_URI_SCHEME = 'ercxxx'
PACKAGE_NAME_REGEX = '[a-zA-Z][-_a-zA-Z0-9]{0,255}'


def is_valid_authority(auth: str) -> None:
    """
    Raises exception if authority is not a valid ENS domain or contract address.
    """
    if is_ens_domain(auth) is False and not is_hex_address(auth):
        raise UriNotSupportedError('{0} is not a valid registry URI authority.'.format(auth))


def is_ens_domain(auth: str) -> bool:
    """
    Returns false if URI authority is not a valid ENS domain.
    """
    if auth[-4:] != '.eth' or len(auth.split('.')) not in [2, 3]:
        return False
    return True


def is_valid_semver(pkg_version: str) -> None:
    """
    Raises exception if package version is not valid semver.
    """
    try:
        semver.parse(pkg_version)
    except ValueError as exc:
        raise UriNotSupportedError('{0} is not a valid registry URI version.'.format(pkg_version))


def is_valid_package_name(pkg_name: str) -> None:
    """
    Returns boolean if the value is a valid package name.
    """
    if not bool(re.match(PACKAGE_NAME_REGEX, pkg_name)):
        raise UriNotSupportedError('{0} is not a valid package name.'.format(pkg_name))


def is_valid_scheme(scheme: str) -> None:
    """
    Raises exception is package scheme is not a valid scheme.
    """
    if scheme != REGISTRY_URI_SCHEME:
        raise UriNotSupportedError('{0} is not a valid registry URI scheme.'.format(scheme))


def parse_path(path: str) -> List[str]:
    """
    Raises exception if path is not a valid path.
    If path is valid, return the name and version
    """
    if not path:
        raise UriNotSupportedError('{0} is not a valid registry URI path.'.format(path))
    return path.split('/')[1:3]


def is_registry_uri(uri: str) -> bool:
    """
    Returns True if URI is a valid registry URI.
    Raises UriNotSupportedError if URI is an invalid URI.
    """
    parsed_uri = parse.urlparse(uri)
    scheme, authority, path = parsed_uri.scheme, parsed_uri.netloc, parsed_uri.path

    is_valid_scheme(scheme)
    pkg_name, pkg_version = parse_path(path)
    is_valid_authority(authority)
    is_valid_package_name(pkg_name)
    is_valid_semver(pkg_version)

    return True
