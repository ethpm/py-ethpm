import pytest

from ethpm.backends.ipfs import (
    DummyIPFSBackend,
    InfuraIPFSBackend,
    IPFSGatewayBackend,
)

@pytest.mark.parametrize(
    'uri',
    (
        'ipfs:Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
        'ipfs:/Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
        'ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
    )
)
def test_ipfs_gateway_backend(uri):
    base_uri = 'https://gateway.ipfs.io/ipfs/'
    backend = IPFSGatewayBackend()
    assert backend.base_uri == base_uri
    assert backend.can_handle_uri(uri) is True
    assert backend.fetch_ipfs_uri(uri).startswith(b'pragma')


@pytest.mark.parametrize(
    'uri',
    (
        'ipfs:Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
        'ipfs:/Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
        'ipfs://Qme4otpS88NV8yQi8TfTP89EsQC5bko3F5N1yhRoi6cwGV',
    )
)
def test_infura_ipfs_gateway_backend(uri):
    base_uri = 'https://ipfs.infura.io/ipfs/'
    backend = InfuraIPFSBackend()
    assert backend.base_uri == base_uri
    assert backend.can_handle_uri(uri) is True
    assert backend.fetch_ipfs_uri(uri).startswith(b'pragma')


def test_dummy_ipfs_backend():
    backend = DummyIPFSBackend()
    pkg = backend.fetch_ipfs_uri()
    assert pkg['package_name'] == 'owned'
