import re
from urllib import parse

from eth_utils import is_checksum_address

from ethpm.constants import PACKAGE_NAME_REGEX, REGISTRY_URI_SCHEME
from ethpm.exceptions import CannotHandleURI, ValidationError
from ethpm.utils.ipfs import is_ipfs_uri
from ethpm.utils.registry import is_ens_domain


def validate_package_name(pkg_name: str) -> None:
    """
    Raise an exception if the value is not a valid package name
    as defined in the EthPM-Spec.
    """
    if not bool(re.match(PACKAGE_NAME_REGEX, pkg_name)):
        raise ValidationError("{0} is not a valid package name.".format(pkg_name))


def validate_ipfs_uri(uri: str) -> None:
    """
    Raise an exception if the provided URI is not a valid IPFS URI.
    """
    if not is_ipfs_uri(uri):
        raise ValidationError("URI: {0} is not a valid IPFS URI.".format(uri))


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
    except CannotHandleURI:
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
    try:
        validate_registry_uri_scheme(scheme)
        validate_registry_uri_authority(authority)
        if query:
            validate_registry_uri_version(query)
        validate_package_name(pkg_name[1:])
    except ValidationError:
        raise CannotHandleURI("{0} is not a valid registry URI.".format(uri))


def validate_registry_uri_authority(auth: str) -> None:
    """
    Raise an exception if the authority is not a valid ENS domain
    or a valid checksummed contract address.
    """
    if is_ens_domain(auth) is False and not is_checksum_address(auth):
        raise ValidationError("{0} is not a valid registry URI authority.".format(auth))


def validate_registry_uri_scheme(scheme: str) -> None:
    """
    Raise an exception if the scheme is not the valid registry URI scheme ('ercXXX').
    """
    if scheme != REGISTRY_URI_SCHEME:
        raise ValidationError("{0} is not a valid registry URI scheme.".format(scheme))


def validate_registry_uri_version(query: str) -> None:
    """
    Raise an exception if the version param is malformed.
    """
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    if "version" not in query_dict:
        raise ValidationError(
            "{0} is not a correctly formatted version param.".format(query)
        )
