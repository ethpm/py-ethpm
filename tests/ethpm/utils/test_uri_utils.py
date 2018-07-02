import pytest

from ethpm.exceptions import CannotHandleURI, ValidationError
from ethpm.utils.uri import get_manifest_from_content_addressed_uri, is_valid_github_uri
from ethpm.validation import validate_github_uri_contents


@pytest.mark.parametrize(
    "uri,source", (("ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW", "ipfs"),)
)
def test_get_manifest_from_content_addressed_uris_for_supported_schemes(
    uri, source, dummy_ipfs_backend
):
    manifest = get_manifest_from_content_addressed_uri(uri)
    assert "version" in manifest
    assert "package_name" in manifest
    assert "manifest_version" in manifest


@pytest.mark.parametrize(
    "uri",
    (
        # filesystem
        ("file:///path_to_erc20.json"),
        # registry URI scheme
        ("erc1128://packages.zeppelinos.eth/erc20/v1.0.0"),
        # swarm
        ("bzz://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d"),
        (
            "bzz-immutable:://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d"
        ),
        ("bzz-raw://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d"),
        # internet
        ("http://github.com/ethpm/ethpm-spec/examples/owned/1.0.0.json#content_hash"),
        ("https://github.com/ethpm/ethpm-spec/examples/owned/1.0.0.json#content_hash"),
    ),
)
def test_get_manfifest_from_content_addressed_uri_raises_exception_for_unsupported_schemes(
    uri
):
    with pytest.raises(CannotHandleURI):
        get_manifest_from_content_addressed_uri(uri)


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
def test_validate_github_uri_contents(contents, hashed):
    assert validate_github_uri_contents(contents, hashed) is None


@pytest.mark.parametrize(
    "contents,hashed", ((123, "1234"), (b"xxx", "1234"), (b"123", "0x1234"))
)
def test_validate_github_uri_contents_invalidates_incorrect_matches(contents, hashed):
    with pytest.raises(ValidationError):
        validate_github_uri_contents(contents, hashed)
