import json
from typing import Tuple
from urllib import parse

from eth_utils import is_text
import requests

from ethpm.constants import GITHUB_API_AUTHORITY
from ethpm.exceptions import CannotHandleURI
from ethpm.typing import URI


def create_content_addressed_github_uri(uri: URI) -> URI:
    """
    Returns a content-addressed Github "git_url" that conforms to this scheme.
    https://api.github.com/repos/:owner/:repo/git/blobs/:file_sha

    Accepts Github-defined "url" that conforms to this scheme
    https://api.github.com/repos/:owner/:repo/contents/:path/:to/manifest.json
    """
    if not is_valid_api_github_uri(uri):
        raise CannotHandleURI(f"{uri} does not conform to Github's API 'url' scheme.")
    response = requests.get(uri)
    response.raise_for_status()
    contents = json.loads(response.content)
    if contents["type"] != "file":
        raise CannotHandleURI(
            f"Expected url to point to a 'file' type, instead received {contents['type']}."
        )
    return contents["git_url"]


def is_valid_content_addressed_github_uri(uri: URI) -> bool:
    """
    Returns a bool indicating whether the given uri conforms to this scheme.
    https://api.github.com/repos/:owner/:repo/git/blobs/:file_sha
    """
    return is_valid_github_uri(uri, ("/repos/", "/git/", "/blobs/"))


def is_valid_api_github_uri(uri: URI) -> bool:
    """
    Returns a bool indicating whether the given uri conforms to this scheme.
    https://api.github.com/repos/:owner/:repo/contents/:path/:to/:file
    """
    return is_valid_github_uri(uri, ("/repos/", "/contents/"))


def is_valid_github_uri(uri: URI, expected_path_terms: Tuple[str, ...]) -> bool:
    """
    Return a bool indicating whether or not the URI fulfills the following specs
    Valid Github URIs *must*:
    - Have 'https' scheme
    - Have 'api.github.com' authority
    - Have a path that contains all "expected_path_terms"
    """
    if not is_text(uri):
        return False

    parsed = parse.urlparse(uri)
    path, scheme, authority = parsed.path, parsed.scheme, parsed.netloc
    if not all((path, scheme, authority)):
        return False

    if [term for term in expected_path_terms if term not in path]:
        return False

    if scheme != "https":
        return False

    if authority != GITHUB_API_AUTHORITY:
        return False
    return True
