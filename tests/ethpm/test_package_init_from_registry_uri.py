import pytest
from solc import compile_source

from ethpm import ASSETS_DIR, Package
from ethpm.exceptions import CannotHandleURI


@pytest.fixture()
def w3_with_registry(w3):
    # compile registry contract
    registry_source = ASSETS_DIR / "Registry.sol"
    reg_text = registry_source.read_text()
    compiled_sol = compile_source(reg_text)
    contract_interface = compiled_sol["<stdin>:Registry"]
    # deploy registry contract
    Registry = w3.eth.contract(
        abi=contract_interface["abi"], bytecode=contract_interface["bin"]
    )
    tx_hash = Registry.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    address = tx_receipt["contractAddress"]
    registry = w3.eth.contract(address=address, abi=contract_interface["abi"])
    # register package on deployed registry
    registry.functions.registerPackage(
        b"owned",  # pkg-name
        "1.0.0",  # version
        "ipfs://QmbeVyFLSuEUxiXKwSsEjef6icpdTdA4kGG9BcrJXKNKUW",  # content-addressed URI
    ).transact()
    w3.eth.waitForTransactionReceipt(tx_hash)
    return w3, address, registry


def test_package_init_from_registry_uri(w3_with_registry, dummy_ipfs_backend):
    w3, address, registry = w3_with_registry
    valid_registry_uri = "ercXXX://%s/owned?version=1.0.0" % address
    pkg = Package.from_uri(valid_registry_uri, w3)
    assert isinstance(pkg, Package)
    assert pkg.name == "owned"


@pytest.mark.parametrize("uri", ("erc111://packages.zeppelin.os/owned",))
def test_package_init_with_invalid_registry_uri_raises_exception(uri, w3):
    with pytest.raises(CannotHandleURI):
        Package.from_uri(uri, w3)
