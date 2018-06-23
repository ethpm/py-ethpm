import pytest

from ethpm.package import Package

from ethpm.exceptions import (
    InsufficientAssetsError,
)


@pytest.fixture()
def safe_math_package(safe_math_manifest):
    return Package(safe_math_manifest)


def test_package_object_instantiates_with_a_web3_object(all_standalone_manifests, w3):
    for manifest in all_standalone_manifests:
        current_package = Package(manifest, w3)
        assert current_package.w3 is w3


def test_set_default_web3(all_standalone_manifests, w3):
    for manifest in all_standalone_manifests:
        current_package = Package(manifest)
        current_package.set_default_w3(w3)
        assert current_package.w3 is w3


def test_get_contract_type_with_unique_web3(safe_math_package, w3):
    contract_factory = safe_math_package.get_contract_type("SafeMathLib", w3)
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


def test_get_contract_type_with_default_web3(safe_math_package, w3):
    safe_math_package.set_default_w3(w3)
    contract_factory = safe_math_package.get_contract_type("SafeMathLib")
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


@pytest.mark.parametrize("invalid_w3", ({"invalid": "w3"}))
def test_get_contract_type_throws_with_invalid_web3(safe_math_package, invalid_w3):
    with pytest.raises(ValueError):
        safe_math_package.get_contract_type("SafeMathLib", invalid_w3)


def test_get_contract_type_without_default_web3(safe_math_package):
    with pytest.raises(ValueError):
        assert safe_math_package.get_contract_type("SafeMathLib")


def test_get_contract_type_with_missing_contract_types(safe_math_package, w3):
    safe_math_package.set_default_w3(w3)
    safe_math_package.package_data.pop('contract_types', None)
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_type("SafeMathLib")


def test_get_contract_type_throws_if_name_isnt_present(safe_math_package, w3):
    with pytest.raises(InsufficientAssetsError):
        assert safe_math_package.get_contract_type("DoesNotExist", w3)


def test_package_object_properties(safe_math_package):
    assert safe_math_package.name == "safe-math-lib"
    assert safe_math_package.version == "1.0.0"
    assert safe_math_package.__repr__() == "<Package safe-math-lib==1.0.0>"
