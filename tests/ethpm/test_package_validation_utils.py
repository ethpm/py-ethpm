import pytest

from ethpm.exceptions import ValidationError

from ethpm.utils.package_validation import (
    load_package_data,
    validate_package_exists,
    validate_package_against_schema,
    validate_package_deployments,
)


@pytest.mark.parametrize("id", ("invalidLockfile.json", "validLockfile.json"))
def test_validate_package_exists_validates(id):
    assert validate_package_exists(id) is None


def test_validate_package_exists_invalidates():
    with pytest.raises(ValidationError):
        validate_package_exists("DNE")


def test_load_package():
    package_data = load_package_data("validLockfile.json")
    assert package_data['build_dependencies']
    assert package_data['lockfile_version']
    assert package_data['deployments']
    assert package_data['contract_types']


def test_validate_package_validates():
    package_data = load_package_data("validLockfile.json")
    assert validate_package_against_schema(package_data) is None


def test_validate_package_invalidates():
    package_data = load_package_data("invalidLockfile.json")
    with pytest.raises(ValidationError):
        validate_package_against_schema(package_data)


def test_validate_deployed_contracts_present_validates(lockfile_with_conflicting_deployments):
    package_data = load_package_data(lockfile_with_conflicting_deployments)
    with pytest.raises(ValidationError):
        validate_package_deployments(package_data)


def test_validate_deployments(lockfile_with_matching_deployments):
    package_data = load_package_data(lockfile_with_matching_deployments)
    validate = validate_package_deployments(package_data)
    assert validate is None


def test_validate_deployed_contracts_pr(lockfile_with_no_deployments):
    package_data = load_package_data(lockfile_with_no_deployments)
    validate = validate_package_deployments(package_data)
    assert validate is None
