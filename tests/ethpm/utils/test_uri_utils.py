import pytest

from ethpm.exceptions import ValidationError
from ethpm.utils.uri import is_valid_github_uri
from ethpm.validation import validate_uri_contents


@pytest.mark.parametrize(
    "uri,expected",
    (
        ({}, False),
        (123, False),
        ("xxx", False),
        # no scheme
        ("raw.githubusercontent.com/any/path#0x123", False),
        # invalid authority
        ("http://github.com/any/path#0x123", False),
        ("https://github.com/any/path#0x123", False),
        # no path
        ("http://raw.githubusercontent.com#0x123", False),
        ("https://raw.githubusercontent.com#0x123", False),
        # no content hash
        ("http://raw.githubusercontent.com/any/path", False),
        ("https://raw.githubusercontent.com/any/path", False),
        (
            "http://raw.githubusercontent.com/ethpm/ethpm-spec/481739f6138907db88602558711e9d3c1301c269/examples/owned/contracts/Owned.sol",  # noqa: E501
            False,
        ),
        # valid github urls
        ("http://raw.githubusercontent.com/any/path#0x123", True),
        ("https://raw.githubusercontent.com/any/path#0x123", True),
        (
            "http://raw.githubusercontent.com/ethpm/ethpm-spec/481739f6138907db88602558711e9d3c1301c269/examples/owned/contracts/Owned.sol#0x123",  # noqa: E501
            True,
        ),
    ),
)
def test_is_valid_github_uri(uri, expected):
    actual = is_valid_github_uri(uri)
    assert actual is expected


@pytest.mark.parametrize(
    "contents,hashed",
    (
        (b"xxx", "bc6bb462e38af7da48e0ae7b5cbae860141c04e5af2cf92328cd6548df111fcb"),
        (b"xxx", "0xbc6bb462e38af7da48e0ae7b5cbae860141c04e5af2cf92328cd6548df111fcb"),
    ),
)
def test_validate_uri_contents(contents, hashed):
    assert validate_uri_contents(contents, hashed) is None


@pytest.mark.parametrize(
    "contents,hashed", ((123, "1234"), (b"xxx", "1234"), (b"123", "0x1234"))
)
def test_validate_uri_contents_invalidates_incorrect_matches(contents, hashed):
    with pytest.raises(ValidationError):
        validate_uri_contents(contents, hashed)
