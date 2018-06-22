import pytest

from solc import compile_source

import ethpm

from ethpm import (
    ASSETS_DIR,
    Package,
)

from ethpm.exceptions import UriNotSupportedError


# mock out http req to IPFS gateway
# `fetch_ipfs_package` returns local 'owned' pkg
@pytest.fixture(autouse=True)
def mock_request(monkeypatch, owned_manifest):
    def mock_fetch(x):
        return owned_manifest
    monkeypatch.setattr(ethpm.utils.uri, 'fetch_ipfs_package', mock_fetch)


@pytest.fixture()
def w3_with_registry(w3):
    # compile registry contract
    registry_source = ASSETS_DIR / 'Registry.sol'
    reg_text = registry_source.read_text()
    compiled_sol = compile_source(reg_text)
    contract_interface = compiled_sol['<stdin>:Registry']
    # deploy registry contract
    Registry = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = Registry.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    address = tx_receipt['contractAddress']
    registry = w3.eth.contract(
        address=address,
        abi=contract_interface['abi'],
    )
    # register package on deployed registry
    registry.functions.registerPackage(
        b'owned',  # pkg-name
        '1.0.0',  # version
        'ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW'  # content-addressed URI
    ).transact()
    w3.eth.waitForTransactionReceipt(tx_hash)
    return w3, address, registry


def test_package_init_from_registry(w3_with_registry):
    w3, address, registry = w3_with_registry
    valid_registry_uri = 'ercXXX://%s/owned?version=1.0.0' % address
    pkg = Package.from_registry(valid_registry_uri, w3)
    assert isinstance(pkg, Package)
    assert pkg.name == 'owned'


@pytest.mark.parametrize(
    'uri',
    (
        'erc111://packages.zeppelin.os/owned',
        'ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW',
        'bzz://da6adeeb4589d8652bbe5679aae6b6409ec85a20e92a8823c7c99e25dba9493d'
    )
)
def test_package_init_with_invalid_registry_uri_raises_exception(uri, w3):
    with pytest.raises(UriNotSupportedError):
        Package.from_registry(uri, w3)
