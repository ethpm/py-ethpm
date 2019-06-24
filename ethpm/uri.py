from collections import namedtuple
import hashlib
import json
from typing import Tuple
from urllib import parse

from eth_utils import is_text, to_bytes, to_text
import requests

from ethpm.backends.http import (
    is_valid_content_addressed_github_uri,
    is_valid_api_github_uri,
)
from ethpm.constants import GITHUB_API_AUTHORITY
from ethpm.exceptions import CannotHandleURI, ValidationError
from ethpm.typing import URI
from ethpm.utils.ipfs import is_ipfs_uri
from ethpm.validation import validate_registry_uri


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


def is_supported_content_addressed_uri(uri: URI) -> bool:
    """
    Returns a bool indicating whether provided uri is currently supported.
    Currently Py-EthPM only supports IPFS and Github blob content-addressed uris.
    """
    if not is_ipfs_uri(uri) and not is_valid_content_addressed_github_uri(uri):
        return False
    return True
