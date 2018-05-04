import pytest

from ethpm.package import Package

from ethpm.exceptions import ValidationError


@pytest.fixture()
def package(valid_package):
    return Package(valid_package)


def test_package_object_instantiates_with_a_web3_object(valid_package, w3):
    current_package = Package(valid_package, w3)
    assert current_package.w3 is w3


def test_set_default_web3(valid_package, w3):
    current_package = Package(valid_package)
    current_package.set_default_w3(w3)
    assert current_package.w3 is w3


def test_get_contract_type_with_unique_web3(package, w3):
    contract_factory = package.get_contract_type("SafeMathLib", w3)
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


def test_get_contract_type_with_default_web3(package, w3):
    package.set_default_w3(w3)
    contract_factory = package.get_contract_type("SafeMathLib")
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


@pytest.mark.parametrize("invalid_w3", ({"invalid": "w3"}))
def test_get_contract_type_throws_with_invalid_web3(package, invalid_w3):
    with pytest.raises(ValueError):
        package.get_contract_type("SafeMathLib", invalid_w3)


def test_get_contract_type_without_default_web3(package):
    with pytest.raises(ValueError):
        assert package.get_contract_type("SafeMathLib")


def test_get_contract_type_throws_if_name_isnt_present(package, w3):
    with pytest.raises(ValidationError):
        assert package.get_contract_type("DoesNotExist", w3)


def test_package_object_has_name_property(valid_package):
    current_package = Package(valid_package)
    assert current_package.name == "safe-math-lib"


def test_package_object_has_version_property(valid_package):
    current_package = Package(valid_package)
    assert current_package.version == "1.0.0"


def test_package_has_custom_str_repr(valid_package):
    current_package = Package(valid_package)
    assert current_package.__repr__() == "<Package safe-math-lib==1.0.0>"
