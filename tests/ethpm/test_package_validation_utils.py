import pytest

from ethpm.exceptions import ValidationError

from ethpm.utils.package_validation import (
    validate_package_exists,
    load_and_validate_package
)


@pytest.mark.parametrize("id", ("invalidLockfile.json", "validLockfile.json"))
def test_validate_package_exists_validates(id):
    assert validate_package_exists(id) is None


def test_validate_package_exists_invalidates():
    with pytest.raises(ValidationError):
        validate_package_exists("DNE")


def test_load_and_validate_package_validates():
    package_data = load_and_validate_package("validLockfile.json")
    assert package_data['build_dependencies']
    assert package_data['lockfile_version']
    assert package_data['deployments']
    assert package_data['contract_types']


def test_load_and_validate_package_invalidates():
    with pytest.raises(ValidationError):
        load_and_validate_package("invalidLockfile.json")
