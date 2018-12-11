import pytest

from ethpm.exceptions import ValidationError
from ethpm.utils.uri import (
    create_content_addressed_github_uri,
    is_valid_api_github_uri,
    is_valid_content_addressed_github_uri,
)


@pytest.mark.parametrize(
    "uri,expected",
    (
        ({}, False),
        (123, False),
        ("xxx", False),
        # invalid scheme
        ("api.github.com/repos/contents/path", False),
        ("http://api.github.com/repos/contents/path", False),
        # invalid authority
        ("http://raw.githubusercontent.com/repos/contents/path", False),
        ("https://github.com/repos/contents/path", False),
        # invalid path
        ("https://api.github.com", False),
        ("https://api.github.com/", False),
        ("https://api.github.com/contents/", False),
        ("https://api.github.com/repos/", False),
        # valid github urls
        ("https://api.github.com/repos/contents/path", True),
        (
            "https://api.github.com/repos/ethpm/ethpm-spec/contents/examples/owned/contracts/Owned.sol",
            True,
        ),
    ),
)
def test_is_valid_github_uri(uri, expected):
    actual = is_valid_api_github_uri(uri)
    assert actual is expected


def test_create_github_uri():
    api_uri = "https://api.github.com/repos/ethpm/py-ethpm/contents/ethpm/assets/owned/1.0.1.json"
    expected_blob_uri = "https://api.github.com/repos/ethpm/py-ethpm/git/blobs/a7232a93f1e9e75d606f6c1da18aa16037e03480"
    actual_blob_uri = create_content_addressed_github_uri(api_uri)
    assert actual_blob_uri == expected_blob_uri
