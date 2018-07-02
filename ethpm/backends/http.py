import requests

from ethpm.backends.base import BaseURIBackend
from ethpm.constants import GITHUB_AUTHORITY
from ethpm.utils.uri import is_valid_github_uri
from ethpm.validation import validate_github_uri_contents


class GithubOverHTTPSBackend(BaseURIBackend):
    """
    Base class for all URIs pointing to a content-addressed Github URI.
    """

    def can_resolve_uri(self, uri: str) -> bool:
        return is_valid_github_uri(uri)

    def can_translate_uri(self, uri: str) -> bool:
        """
        GithubOverHTTPSBackend uri's must resolve to a valid manifest.
        """
        return False

    def fetch_uri_contents(self, uri: str) -> bytes:
        http_uri, validation_hash = uri.split("#")
        response = requests.get(http_uri)
        response.raise_for_status()
        validate_github_uri_contents(response.content, validation_hash)
        return response.content

    @property
    def base_uri(self) -> str:
        return GITHUB_AUTHORITY
