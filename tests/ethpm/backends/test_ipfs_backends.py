import json

from eth_utils import (
    to_text,
)
import pytest

from ethpm.backends.ipfs import (
    DummyIPFSBackend,
    InfuraIPFSBackend,
    IPFSGatewayBackend,
)


@pytest.mark.parametrize(
    'base_uri,backend',
    (
        ('https://gateway.ipfs.io/ipfs/', IPFSGatewayBackend()),
        ('https://ipfs.infura.io/ipfs/', InfuraIPFSBackend()),
    )
)
def test_ipfs_gateway_backend(base_uri, backend):
    uri = 'ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV'
    assert backend.base_uri == base_uri
    assert backend.can_handle_uri(uri) is True
    assert backend.fetch_uri_contents(uri).startswith(b'pragma')


def test_dummy_ipfs_backend():
    backend = DummyIPFSBackend()
    pkg = backend.fetch_uri_contents('safe-math-lib/1.0.0.json')
    mnfst = to_text(pkg)
    manifest = json.loads(mnfst)
    assert manifest['package_name'] == 'safe-math-lib'
