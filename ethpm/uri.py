import json

import requests

from ethpm._utils.backend import (
    get_resolvable_backends_for_uri,
    get_translatable_backends_for_uri,
)
from ethpm.backends.http import (
    is_valid_api_github_uri,
    is_valid_content_addressed_github_uri,
)
from ethpm.backends.registry import RegistryURIBackend
from ethpm.exceptions import CannotHandleURI
from ethpm.typing import URI
from ethpm.utils.ipfs import is_ipfs_uri


def resolve_uri_contents(uri: URI, fingerprint: bool = None) -> bytes:
    resolvable_backends = get_resolvable_backends_for_uri(uri)
    if resolvable_backends:
        for backend in resolvable_backends:
            try:
                # type ignored to handle case if URI is returned
                contents: bytes = backend().fetch_uri_contents(uri)  # type: ignore
            except CannotHandleURI:
                continue
            return contents

    translatable_backends = get_translatable_backends_for_uri(uri)
    if translatable_backends:
        if fingerprint:
            raise CannotHandleURI(
                "Registry URIs must point to a resolvable content-addressed URI."
            )
        package_id = RegistryURIBackend().fetch_uri_contents(uri)
        return resolve_uri_contents(package_id, True)

    raise CannotHandleURI(
        f"URI: {uri} cannot be resolved by any of the available backends."
    )


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
