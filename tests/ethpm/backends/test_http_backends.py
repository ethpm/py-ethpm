import pytest
import requests_mock

from ethpm.backends.http import GithubOverHTTPSBackend
from ethpm.constants import GITHUB_AUTHORITY


@pytest.mark.parametrize(
    "uri",
    (
        "https://raw.githubusercontent.com/ethpm/ethpm-spec/481739f6138907db88602558711e9d3c1301c269/examples/owned/contracts/Owned.sol#bfdea1fa5f33c30fee8443c5ffa1020027f8813e0007bb6f82aaa2843a7fdd60",  # noqa: E501
    ),
)
def test_github_over_https_backend_fetch_uri_contents(uri, owned_contract):
    backend = GithubOverHTTPSBackend()
    assert backend.base_uri == GITHUB_AUTHORITY
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text=owned_contract)
        response = backend.fetch_uri_contents(uri)
        assert response.startswith(b"pragma")
