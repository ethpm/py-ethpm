import pytest

from ethpm import Package
from ethpm.backends.http import GithubOverHTTPSBackend
from ethpm.constants import RAW_GITHUB_AUTHORITY
from ethpm.exceptions import ValidationError


@pytest.mark.parametrize(
    "uri",
    (
        "https://raw.githubusercontent.com/ethpm/ethpm-spec/3945c47dedb04930ee12c0281494a1b5bdd692a0/examples/owned/1.0.0.json#01cbc2a69a9f86e9d9e7b87475e2ba2619404dc8d6ee3cb3a8acf3176c2cace1",  # noqa: E501
        "https://raw.githubusercontent.com/ethpm/ethpm-spec/3945c47dedb04930ee12c0281494a1b5bdd692a0/examples/owned/1.0.0.json#0x01cbc2a69a9f86e9d9e7b87475e2ba2619404dc8d6ee3cb3a8acf3176c2cace1",  # noqa: E501
    ),
)
def test_github_over_https_backend_fetch_uri_contents(uri, owned_contract, w3):
    # these tests may occassionally fail CI as a result of their network requests
    backend = GithubOverHTTPSBackend()
    assert backend.base_uri == RAW_GITHUB_AUTHORITY
    # integration with Package.from_uri
    owned_package = Package.from_uri(uri, w3)
    assert owned_package.name == "owned"


def test_github_over_https_backend_raises_error_with_invalid_content_hash(w3):
    invalid_uri = "https://raw.githubusercontent.com/ethpm/ethpm-spec/3945c47dedb04930ee12c0281494a1b5bdd692a0/examples/owned/1.0.0.json#01cbc2a69a9f86e9d9e7b87475e2ba2619404dc8d6ee3cb3a8acf3176c2ca111"  # noqa: E501
    with pytest.raises(ValidationError):
        Package.from_uri(invalid_uri, w3)
