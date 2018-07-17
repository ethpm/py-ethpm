from eth_utils import is_same_address
import pytest

from ethpm.exceptions import InsufficientAssetsError
from ethpm.package import Package


@pytest.fixture()
def safe_math_package(get_manifest):
    safe_math_manifest = get_manifest("safe-math-lib")
    return Package(safe_math_manifest)


@pytest.fixture()
def deployed_safe_math(safe_math_package, w3):
    safe_math_package.set_default_w3(w3)
    SafeMath = safe_math_package.get_contract_factory("SafeMathLib")
    tx_hash = SafeMath.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return safe_math_package, tx_receipt.contractAddress


def test_package_object_instantiates_with_a_web3_object(all_standalone_manifests, w3):
    for manifest in all_standalone_manifests:
        current_package = Package(manifest, w3)
        assert current_package.w3 is w3


def test_set_default_web3(all_standalone_manifests, w3):
    for manifest in all_standalone_manifests:
        current_package = Package(manifest)
        current_package.set_default_w3(w3)
        assert current_package.w3 is w3


def test_get_contract_factory_with_unique_web3(safe_math_package, w3):
    contract_factory = safe_math_package.get_contract_factory("SafeMathLib", w3)
    assert hasattr(contract_factory, "address")
    assert hasattr(contract_factory, "abi")
    assert hasattr(contract_factory, "bytecode")
    assert hasattr(contract_factory, "bytecode_runtime")


def test_get_contract_factory_with_default_web3(safe_math_package, w3):
    safe_math_package.set_default_w3(w3)
    contract_factory = safe_math_package.get_contract_factory("SafeMathLib")
    assert hasattr(contract_factory, "address")
    assert hasattr(contract_factory, "abi")
    assert hasattr(contract_factory, "bytecode")
    assert hasattr(contract_factory, "bytecode_runtime")


@pytest.mark.parametrize("invalid_w3", ({"invalid": "w3"}))
def test_get_contract_factory_throws_with_invalid_web3(safe_math_package, invalid_w3):
    with pytest.raises(ValueError):
        safe_math_package.get_contract_factory("SafeMathLib", invalid_w3)


def test_get_contract_factory_without_default_web3(safe_math_package):
    with pytest.raises(ValueError):
        assert safe_math_package.get_contract_factory("SafeMathLib")


def test_get_contract_factory_with_missing_contract_types(safe_math_package, w3):
    safe_math_package.set_default_w3(w3)
    safe_math_package.package_data.pop("contract_types", None)
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_factory("SafeMathLib")


def test_get_contract_factory_throws_if_name_isnt_present(safe_math_package, w3):
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_factory("DoesNotExist", w3)


def test_get_contract_instance(deployed_safe_math):
    safe_math_package, address = deployed_safe_math
    contract_instance = safe_math_package.get_contract_instance("SafeMathLib", address)
    assert contract_instance.abi is not False
    assert is_same_address(contract_instance.address, address)


def test_get_contract_instance_throws_with_insufficient_assets(deployed_safe_math):
    safe_math_package, address = deployed_safe_math
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_instance("IncorrectLib", address)
    safe_math_package.package_data["contract_types"]["SafeMathLib"].pop("abi")
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_instance("SafeMathLib", address)


def test_package_object_properties(safe_math_package):
    assert safe_math_package.name == "safe-math-lib"
    assert safe_math_package.version == "1.0.0"
    assert safe_math_package.__repr__() == "<Package safe-math-lib==1.0.0>"
