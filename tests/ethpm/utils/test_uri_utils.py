import pytest

from ethpm.exceptions import UriNotSupportedError

from ethpm.utils.uri import get_manifest_from_content_addressed_uri


@pytest.mark.parametrize(
    'uri,source',
    (
        ('ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW', 'ipfs'),
    )
)
def test_get_manifest_from_content_addressed_uris_for_supported_schemes(uri, source):
    manifest = get_manifest_from_content_addressed_uri(uri)
    assert 'version' in manifest
    assert 'package_name' in manifest
    assert 'manifest_version' in manifest


@pytest.mark.parametrize(
    'uri',
    (
        # filesystem
        ('file:///path_to_erc20.json'),
        # registry URI scheme
        ('erc1128://packages.zeppelinos.eth/erc20/v1.0.0'),
        # swarm
        ('bzz://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d'),
        ('bzz-immutable:://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d'),
        ('bzz-raw://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d'),
        # internet
        ('http://github.com/ethpm/ethpm-spec/examples/owned/1.0.0.json#content_hash'),
        ('https://github.com/ethpm/ethpm-spec/examples/owned/1.0.0.json#content_hash'),
    )
)
def test_get_manfifest_from_content_addressed_uri_raises_exception_for_unsupported_schemes(uri):
    with pytest.raises(UriNotSupportedError):
        get_manifest_from_content_addressed_uri(uri)
