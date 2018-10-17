from urllib import parse

import requests

from ethpm.backends.base import BaseURIBackend
from ethpm.constants import RAW_GITHUB_AUTHORITY
from ethpm.utils.uri import is_valid_github_uri
from ethpm.validation import validate_uri_contents


class GithubOverHTTPSBackend(BaseURIBackend):
    """
    Base class for all URIs pointing to a content-addressed Github URI.
    """

    def can_resolve_uri(self, uri: str) -> bool:
        return is_valid_github_uri(uri)

    def can_translate_uri(self, uri: str) -> bool:
        """
        GithubOverHTTPSBackend uri's must resolve to a valid manifest,
        and cannot translate to another content-addressed URI.
        """
        return False

    def fetch_uri_contents(self, uri: str) -> bytes:
        parsed_uri = parse.urlparse(uri)
        validation_hash = parsed_uri.fragment
        http_uri = f"{parsed_uri.scheme}://{parsed_uri.netloc}{parsed_uri.path}"
        response = requests.get(http_uri)
        response.raise_for_status()
        validate_uri_contents(response.content, validation_hash)
        return response.content

    @property
    def base_uri(self) -> str:
        return RAW_GITHUB_AUTHORITY
