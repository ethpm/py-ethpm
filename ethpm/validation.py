import re

from eth_utils import is_checksum_address

from ethpm.constants import (
    PACKAGE_NAME_REGEX,
    REGISTRY_URI_SCHEME,
)

from ethpm.exceptions import UriNotSupportedError


def validate_package_name(pkg_name: str) -> None:
    """
    Raises exception if the value is not a valid package name.
    """
    if not bool(re.match(PACKAGE_NAME_REGEX, pkg_name)):
        raise UriNotSupportedError('{0} is not a valid package name.'.format(pkg_name))


def validate_registry_uri_authority(auth: str) -> None:
    """
    Raises exception if authority is not a valid ENS domain or valid checksummed contract address.
    """
    from ethpm.utils.registry import is_ens_domain
    if is_ens_domain(auth) is False and not is_checksum_address(auth):
        raise UriNotSupportedError('{0} is not a valid registry URI authority.'.format(auth))


def validate_registry_uri_scheme(scheme: str) -> None:
    """
    Raises exception if package scheme is not a valid registry URI scheme.
    """
    if scheme != REGISTRY_URI_SCHEME:
        raise UriNotSupportedError('{0} is not a valid registry URI scheme.'.format(scheme))


def validate_registry_uri_version(pkg_version: str) -> None:
    """
    Raises exception if package version is an empty string.
    """
    if not pkg_version:
        raise UriNotSupportedError('{0} is not a valid registry URI version.'.format(pkg_version))
