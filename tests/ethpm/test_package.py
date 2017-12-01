import pytest

from ethpm.package import Package

from ethpm.exceptions import ValidationError


def test_ethpm_exists():
    assert Package


@pytest.fixture()
def valid_package_id():
    return "validLockfile.json"


@pytest.fixture()
def invalid_package_id():
    return "invalidLockfile.json"


@pytest.fixture()
def package(valid_package_id):
    return Package(valid_package_id)


def test_package_object_instantiates_with_valid_package_id(valid_package_id):
    current_package = Package(valid_package_id)
    assert current_package.package_id is valid_package_id
    assert current_package.w3 is None
    assert current_package.package_data['build_dependencies']
    assert current_package.package_data['lockfile_version']
    assert current_package.package_data['deployments']
    assert current_package.package_data['contract_types']


def test_package_object_fails_instantiation_with_invalid_package_id(invalid_package_id):
    with pytest.raises(ValidationError):
        Package(invalid_package_id)


@pytest.mark.parametrize(
    "invalid_path",
    (
        "./tests/ethpm/doesntExist.json",
        "abcd",
    )
)
def test_package_object_doesnt_instantiate_with_invalid_path(invalid_path):
    with pytest.raises(ValidationError):
        Package(invalid_path)


def test_package_object_instantiates_with_a_web3_object(valid_package_id, w3):
    current_package = Package(valid_package_id, w3)
    assert current_package.w3 is w3


def test_set_default_web3(valid_package_id, w3):
    current_package = Package(valid_package_id)
    current_package.set_default_w3(w3)
    assert current_package.w3 is w3


def test_get_contract_type_with_unique_web3(package, w3):
    contract_factory = package.get_contract_type("Wallet", w3)
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


def test_get_contract_type_with_default_web3(package, w3):
    package.set_default_w3(w3)
    contract_factory = package.get_contract_type("Wallet")
    assert hasattr(contract_factory, 'address')
    assert hasattr(contract_factory, 'abi')
    assert hasattr(contract_factory, 'bytecode')
    assert hasattr(contract_factory, 'bytecode_runtime')


@pytest.mark.parametrize("invalid_w3", ({"invalid": "w3"}))
def test_get_contract_type_throws_with_invalid_web3(package, invalid_w3):
    with pytest.raises(ValueError):
        package.get_contract_type("Wallet", invalid_w3)


def test_get_contract_type_without_default_web3(package):
    with pytest.raises(ValueError):
        assert package.get_contract_type("Wallet")


def test_get_contract_type_throws_if_name_isnt_present(package, w3):
    with pytest.raises(ValidationError):
        assert package.get_contract_type("DoesNotExist", w3)


def test_package_object_has_name_property(valid_package_id):
    current_package = Package(valid_package_id)
    assert current_package.name == "wallet"


def test_package_object_has_version_property(valid_package_id):
    current_package = Package(valid_package_id)
    assert current_package.version == "1.0.0"


def test_package_has_custom_str_repr(valid_package_id):
    current_package = Package(valid_package_id)
    assert current_package.__repr__() == "<Package wallet==1.0.0>"
