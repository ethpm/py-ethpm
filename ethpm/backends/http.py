import base64
import json

import requests

from ethpm.backends.base import BaseURIBackend
from ethpm.constants import GITHUB_API_AUTHORITY
from ethpm.exceptions import CannotHandleURI
from ethpm.typing import URI
from ethpm.utils.uri import (
    is_valid_content_addressed_github_uri,
    validate_blob_uri_contents,
)


class GithubOverHTTPSBackend(BaseURIBackend):
    """
    Base class for all URIs pointing to a content-addressed Github URI.
    """

    def can_resolve_uri(self, uri: URI) -> bool:
        return is_valid_content_addressed_github_uri(uri)

    def can_translate_uri(self, uri: URI) -> bool:
        """
        GithubOverHTTPSBackend uri's must resolve to a valid manifest,
        and cannot translate to another content-addressed URI.
        """
        return False

    def fetch_uri_contents(self, uri: URI) -> bytes:
        if not self.can_resolve_uri(uri):
            raise CannotHandleURI(f"GithubOverHTTPSBackend cannot resolve {uri}.")

        response = requests.get(uri)
        response.raise_for_status()
        contents = json.loads(response.content)
        if contents["encoding"] != "base64":
            raise CannotHandleURI(
                "Expected contents returned from Github to be base64 encoded, "
                f"instead received {contents['encoding']}."
            )
        decoded_contents = base64.b64decode(contents["content"])
        validate_blob_uri_contents(decoded_contents, uri)
        return decoded_contents

    @property
    def base_uri(self) -> str:
        return GITHUB_API_AUTHORITY
