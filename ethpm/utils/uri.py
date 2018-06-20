from typing import (
    Any,
    Dict,
)

from urllib import parse

from ethpm.exceptions import UriNotSupportedError

from ethpm.utils.ipfs import (
    fetch_ipfs_package,
)


INTERNET_PREFIXES = ['http', 'https']

SWARM_PREFIXES = ['bzz', 'bzz-immutable', 'bzz-raw']


def get_manifest_from_content_addressed_uri(uri: str) -> Dict[str, Any]:
    parse_result = parse.urlparse(uri)
    scheme = parse_result.scheme

    if scheme == 'ipfs':
        ipfs_hash = parse_result.netloc
        manifest_data = fetch_ipfs_package(ipfs_hash)
        return manifest_data

    if scheme in INTERNET_PREFIXES:
        raise UriNotSupportedError('Internet URIs are not yet supported.')

    if scheme in SWARM_PREFIXES:
        raise UriNotSupportedError('Swarm URIs are not yet supported.')

    raise UriNotSupportedError('The URI scheme:{0} is not supported.'.format(scheme))
