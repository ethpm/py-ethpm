from typing import (
    Any,
    Dict,
)

from urllib import parse

from ethpm.exceptions import UriNotSupportedError

from ethpm.utils.ipfs import (
    fetch_ipfs_package,
)

IPFS_SCHEME = 'ipfs'

INTERNET_SCHEMES = ['http', 'https']

SWARM_SCHEMES = ['bzz', 'bzz-immutable', 'bzz-raw']


def get_manifest_from_content_addressed_uri(uri: str) -> Dict[str, Any]:
    """
    Return manifest data stored at a content addressed URI.
    """
    parse_result = parse.urlparse(uri)
    scheme = parse_result.scheme

    if scheme == IPFS_SCHEME:
        ipfs_hash = parse_result.netloc
        manifest_data = fetch_ipfs_package(ipfs_hash)
        return manifest_data

    if scheme in INTERNET_SCHEMES:
        raise UriNotSupportedError('Internet URIs are not yet supported.')

    if scheme in SWARM_SCHEMES:
        raise UriNotSupportedError('Swarm URIs are not yet supported.')

    raise UriNotSupportedError('The URI scheme:{0} is not supported.'.format(scheme))
