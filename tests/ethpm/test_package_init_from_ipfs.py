import pytest

import ethpm

from ethpm import Package

VALID_IPFS_PKG = 'ipfs://QmeD2s7KaBUoGYTP1eutHBmBkMMMoycdfiyGMx2DKrWXyV'


# mock out http req to IPFS gateway
# `fetch_ipfs_package` returns local 'safe-math-lib` pkg
@pytest.fixture(autouse=True)
def mock_request(monkeypatch, safe_math_manifest):
    def mock_fetch(x):
        return safe_math_manifest
    monkeypatch.setattr(ethpm.package, 'fetch_ipfs_package', mock_fetch)


def test_package_from_ipfs_with_valid_uri():
    package = Package.from_ipfs(VALID_IPFS_PKG)
    assert package.name == 'safe-math-lib'
    assert isinstance(package, Package)


@pytest.mark.parametrize(
    "invalid",
    (
        '123',
        b'123',
        {},
        'ipfs://',
        'http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme',
        'ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/',
    )
)
def test_package_from_ipfs_rejects_invalid_ipfs_uri(invalid):
    with pytest.raises(TypeError):
        Package.from_ipfs(invalid)
