import pytest
from ethpm.package import Package
from ethpm.exceptions import ValidationError


def test_ethpm_exists():
    assert Package


@pytest.fixture()
def valid_package():
    return "./tests/ethpm/validLockfile.json"


@pytest.fixture()
def invalid_package():
    return "./tests/ethpm/invalidLockfile.json"


def test_ethpm_instantiates_with_valid_package(valid_package):
    current_package = Package(valid_package)
    assert current_package.package_identifier == valid_package
    assert current_package.package_data['build_dependencies']
    assert current_package.package_data['lockfile_version']
    assert current_package.package_data['deployments']
    assert current_package.package_data['contract_types']


def test_ethpm_doesnt_instantiate_with_invalid_package(invalid_package):
    with pytest.raises(ValidationError):
        Package(invalid_package)


@pytest.mark.parametrize(
    "invalid_path",
    (
        "./tests/ethpm/doesntExist.json",
        12345,
        "abcd",
    )
)
def test_ethpm_doesnt_instantiate_with_invalid_path(invalid_path):
    with pytest.raises(ValidationError):
        Package(invalid_path)


def test_package_object_has_name_property(valid_package):
    current_package = Package(valid_package)
    assert current_package.name == "wallet"


def test_package_object_has_version_property(valid_package):
    current_package = Package(valid_package)
    assert current_package.version == "1.0.0"


def test_package_has_custom_str_repr(valid_package):
    current_package = Package(valid_package)
    assert current_package.__repr__() == "<Package wallet==1.0.0>"
