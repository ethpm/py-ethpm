import re

from urllib import parse

from eth_utils import is_checksum_address

from ethpm.constants import (
    PACKAGE_NAME_REGEX,
    REGISTRY_URI_SCHEME,
)

from ethpm.exceptions import UriNotSupportedError

from ethpm.utils.registry import (
    is_ens_domain,
)


def validate_package_name(pkg_name: str) -> None:
    """
    Raise an exception if the value is not a valid package name
    as defined in the EthPM-Spec.
    """
    if not bool(re.match(PACKAGE_NAME_REGEX, pkg_name)):
        raise UriNotSupportedError('{0} is not a valid package name.'.format(pkg_name))


def validate_registry_uri(uri: str) -> None:
    """
    Raise an exception if the URI does not conform to the registry URI scheme.
    """
    parsed = parse.urlparse(uri)
    scheme, authority, pkg_name, query = parsed.scheme, parsed.netloc, parsed.path, parsed.query
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
        raise UriNotSupportedError('{0} is not a valid registry URI authority.'.format(auth))


def validate_registry_uri_scheme(scheme: str) -> None:
    """
    Raise an exception if the scheme is not the valid registry URI scheme ('ercXXX').
    """
    if scheme != REGISTRY_URI_SCHEME:
        raise UriNotSupportedError('{0} is not a valid registry URI scheme.'.format(scheme))


def validate_registry_uri_version(query: str) -> None:
    """
    Raise an exception if the version param is malformed.
    """
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    if 'version' not in query_dict:
        raise UriNotSupportedError('{0} is not a correctly formatted version param.'.format(query))
