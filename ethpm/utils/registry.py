from urllib import parse

from typing import List

from ethpm.exceptions import UriNotSupportedError

from ethpm.validation import (
    validate_package_name,
    validate_registry_uri_authority,
    validate_registry_uri_scheme,
    validate_registry_uri_version,
)


def is_ens_domain(auth: str) -> bool:
    """
    Returns false if URI authority is not a valid ENS domain.
    """
    if auth[-4:] != '.eth' or len(auth.split('.')) not in [2, 3]:
        return False
    return True


def is_registry_uri(uri: str) -> bool:
    """
    Returns True if URI is a valid registry URI.
    Raises UriNotSupportedError if URI is an invalid URI.
    """
    parsed_uri = parse.urlparse(uri)
    scheme, authority, path = parsed_uri.scheme, parsed_uri.netloc, parsed_uri.path

    validate_registry_uri_scheme(scheme)
    pkg_name, pkg_version = parse_path(path)
    validate_registry_uri_authority(authority)
    validate_registry_uri_version(pkg_version)
    validate_package_name(pkg_name)

    return True


def parse_path(path: str) -> List[str]:
    """
    Raises exception if path is empty string.
    If path is valid, return the name and version
    """
    if len(path.split('/')) not in [2, 3, 4]:
        raise UriNotSupportedError('{0} is not a valid registry URI path.'.format(path))
    return path.split('/')[1:3]
