import pytest

from ethpm import V2_PACKAGES_DIR
from ethpm.backends.ipfs import get_ipfs_backend

OWNED_MANIFEST_PATH = V2_PACKAGES_DIR / "owned" / "1.0.0.json"


def test_local_ipfs_backend_integration_round_trip(monkeypatch):
    """
    To run this integration test requires an running IPFS node.
    If you want to run these tests, first start your IPFS node, and
    then run pytest with the arg `--integration`.
    """
    if not pytest.config.getoption("--integration"):
        pytest.skip("Not asked to run integration tests")

    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.LocalIPFSBackend"
    )
    backend = get_ipfs_backend()
    [asset_data] = backend.pin_assets(OWNED_MANIFEST_PATH)
    assert asset_data["Name"] == "1.0.0.json"
    assert asset_data["Hash"] == "QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW"
    with open(str(OWNED_MANIFEST_PATH), "rb") as f:
        local_manifest = f.read()
    ipfs_manifest = backend.fetch_uri_contents(asset_data["Hash"])
    assert ipfs_manifest == local_manifest
