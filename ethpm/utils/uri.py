import json
from typing import Any, Dict
from urllib import parse

from eth_utils import is_text, to_text

from ethpm.backends.ipfs import get_ipfs_backend
from ethpm.exceptions import CannotHandleURI

IPFS_SCHEME = "ipfs"

INTERNET_SCHEMES = ["http", "https"]

SWARM_SCHEMES = ["bzz", "bzz-immutable", "bzz-raw"]

RAW_GITHUB_AUTHORITY = "raw.githubusercontent.com"


def is_valid_github_uri(uri: str) -> bool:
    """
    Return a bool indicating whether or not the URI is a valid Github URI.
    Valid Github URIs *must*:
    - Have 'http' or 'https' scheme
    - Have 'raw.githubusercontent.com' authority
    - Have any path (*should* include a commit hash in path)
    - Have ending fragment containing any content hash
    i.e. 'https://raw.githubusercontent.com/any/path#content_hash
    """
    if not is_text(uri):
        return False
    parse_result = parse.urlparse(uri)
    path = parse_result.path
    scheme = parse_result.scheme
    authority = parse_result.netloc
    content_hash = parse_result.fragment

    if not path or not scheme or not content_hash:
        return False

    if scheme not in INTERNET_SCHEMES:
        return False

    if authority != RAW_GITHUB_AUTHORITY:
        return False
    return True


def get_manifest_from_content_addressed_uri(uri: str) -> Dict[str, Any]:
    """
    Return manifest data stored at a content addressed URI.
    """
    parse_result = parse.urlparse(uri)
    scheme = parse_result.scheme

    if scheme == IPFS_SCHEME:
        ipfs_backend = get_ipfs_backend()
        if ipfs_backend.can_resolve_uri(uri):
            raw_manifest_data = ipfs_backend.fetch_uri_contents(uri)
            manifest_data = to_text(raw_manifest_data)
            return json.loads(manifest_data)
        else:
            raise TypeError(
                "The IPFS Backend: {0} cannot handle the given URI: {1}.".format(
                    type(ipfs_backend).__name__, uri
                )
            )

    if scheme in INTERNET_SCHEMES:
        raise CannotHandleURI("Internet URIs are not yet supported.")

    if scheme in SWARM_SCHEMES:
        raise CannotHandleURI("Swarm URIs are not yet supported.")

    raise CannotHandleURI("The URI scheme:{0} is not supported.".format(scheme))
