from collections import namedtuple
import hashlib
import json
from typing import Tuple
from urllib import parse

from eth_utils import is_text, to_bytes, to_text
import requests

from ethpm.constants import GITHUB_API_AUTHORITY
from ethpm.exceptions import CannotHandleURI, ValidationError
from ethpm.typing import URI
from ethpm.utils.ipfs import is_ipfs_uri
from ethpm.validation import validate_registry_uri

RegistryURI = namedtuple("RegistryURI", ["auth", "name", "version"])


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

    if any(term for term in expected_path_terms if term not in path):
        return False

    if scheme != "https":
        return False

    if authority != GITHUB_API_AUTHORITY:
        return False
    return True


def validate_blob_uri_contents(contents: bytes, blob_uri: str) -> None:
    """
    Raises an exception if the sha1 hash of the contents does not match the hash found in te
    blob_uri. Formula for how git calculates the hash found here:
    http://alblue.bandlem.com/2011/08/git-tip-of-week-objects.html
    """
    blob_path = parse.urlparse(blob_uri).path
    blob_hash = blob_path.split("/")[-1]
    contents_str = to_text(contents)
    content_length = len(contents_str)
    hashable_contents = "blob " + str(content_length) + "\0" + contents_str
    hash_object = hashlib.sha1(to_bytes(text=hashable_contents))
    if hash_object.hexdigest() != blob_hash:
        raise ValidationError(
            f"Hash of contents fetched from {blob_uri} do not match its hash: {blob_hash}."
        )


def parse_registry_uri(uri: str) -> RegistryURI:
    """
    Validate and return (authority, pkg name, version) from a valid registry URI
    """
    validate_registry_uri(uri)
    parsed_uri = parse.urlparse(uri)
    authority = parsed_uri.netloc
    pkg_name = parsed_uri.path.strip("/")
    pkg_version = parsed_uri.query.lstrip("version=").strip("/")
    return RegistryURI(authority, pkg_name, pkg_version)


def is_supported_content_addressed_uri(uri: URI) -> bool:
    """
    Returns a bool indicating whether provided uri is currently supported.
    Currently Py-EthPM only supports IPFS and Github blob content-addressed uris.
    """
    if not is_ipfs_uri(uri) and not is_valid_content_addressed_github_uri(uri):
        return False
    return True
