from urllib import parse

from eth_utils import is_text

from ethpm.constants import INTERNET_SCHEMES, RAW_GITHUB_AUTHORITY


def is_valid_github_uri(uri: str) -> bool:
    """
    Return a bool indicating whether or not the URI is a valid Github URI.
    Valid Github URIs *must*:
    - Have 'http' or 'https' scheme
    - Have 'raw.githubusercontent.com' authority
    - Have any path (*should* include a commit hash in path)
    - Have ending fragment containing the keccak hash of the uri contents
    ex. 'https://raw.githubusercontent.com/user/repo/commit_hash/path/to/manifest.json#content_hash'
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
