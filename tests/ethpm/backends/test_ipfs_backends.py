import json

from eth_utils import to_text
import pytest
import requests_mock

from ethpm.backends.ipfs import (
    DummyIPFSBackend,
    InfuraIPFSBackend,
    IPFSGatewayBackend,
    LocalIPFSBackend,
    get_ipfs_backend,
)
from ethpm.constants import INFURA_GATEWAY_PREFIX, IPFS_GATEWAY_PREFIX


@pytest.fixture
def fake_client():
    class FakeClient:
        def cat(self, ipfs_hash):
            return ipfs_hash

    return FakeClient()


@pytest.mark.parametrize(
    "base_uri,backend",
    (
        (IPFS_GATEWAY_PREFIX, IPFSGatewayBackend()),
        (INFURA_GATEWAY_PREFIX, InfuraIPFSBackend()),
    ),
)
def test_ipfs_and_infura_gateway_backends_fetch_uri_contents(
    base_uri, backend, safe_math_manifest
):
    uri = "ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV"
    assert backend.base_uri == base_uri
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text=json.dumps(safe_math_manifest))
        contents = backend.fetch_uri_contents(uri)
        contents_dict = json.loads(to_text(contents))
        assert contents_dict["package_name"] == "safe-math-lib"


def test_local_ipfs_backend(monkeypatch, fake_client):
    uri = "ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV"
    backend = LocalIPFSBackend()
    backend.client = fake_client
    contents = backend.fetch_uri_contents(uri)
    assert contents.startswith("Qm")


@pytest.mark.parametrize(
    "uri,expected",
    (
        ("ipfs:QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u", True),
        ("ipfs:/QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u", True),
        ("ipfs://QmTKB75Y73zhNbD3Y73xeXGjYrZHmaXXNxoZqGCagu7r8u", True),
        ("http://raw.githubusercontent.com/ethpm/py-ethpm#0x123", False),
        ("https://raw.githubusercontent.com/ethpm/py-ethpm#0x123", False),
        (
            "bzz://679bde3ccb6fb911db96a0ea1586c04899c6c0cc6d3426e9ee361137b270a463",
            False,
        ),
        ("ercxxx://packages.eth/owned?version=1.0.0", False),
    ),
)
def test_base_ipfs_gateway_backend_correctly_handle_uri_schemes(uri, expected):
    backend = IPFSGatewayBackend()
    assert backend.can_handle_uri(uri) is expected


def test_dummy_ipfs_backend():
    pkg = DummyIPFSBackend().fetch_uri_contents("safe-math-lib/1.0.0.json")
    mnfst = to_text(pkg)
    manifest = json.loads(mnfst)
    assert manifest["package_name"] == "safe-math-lib"


def test_get_ipfs_backend_default():
    backend = get_ipfs_backend()
    assert isinstance(backend, IPFSGatewayBackend)


def test_get_uri_backend_with_env_variable(monkeypatch):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    backend = get_ipfs_backend()
    assert isinstance(backend, DummyIPFSBackend)
