import pytest
from erc190.package import Package
from erc190.exceptions import ValidationError


def test_ethpm_exists():
    assert Package


@pytest.fixture()
def valid_package():
    return "./tests/erc190/validLockfile.json"


@pytest.fixture()
def invalid_package():
    return "./tests/erc190/invalidLockfile.json"


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
