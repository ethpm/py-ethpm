import pytest

from ethpm import Package

VALID_IPFS_PKG = "ipfs://QmeD2s7KaBUoGYTP1eutHBmBkMMMoycdfiyGMx2DKrWXyV"


def test_package_from_ipfs_with_valid_uri(monkeypatch):
    monkeypatch.setenv(
        "ETHPM_URI_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    package = Package.from_ipfs(VALID_IPFS_PKG)
    assert package.name == "safe-math-lib"
    assert isinstance(package, Package)


@pytest.mark.parametrize(
    "invalid",
    (
        "123",
        b"123",
        {},
        "ipfs://",
        "http://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme",
        "ipfsQmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u/readme/",
    ),
)
def test_package_from_ipfs_rejects_invalid_ipfs_uri(invalid):
    with pytest.raises(TypeError):
        Package.from_ipfs(invalid)
