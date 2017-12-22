import pytest

from ethpm.exceptions import ValidationError

from ethpm.utils.package_validation import (
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


def test_validate_package_validates(valid_lockfile):
    assert validate_package_against_schema(valid_lockfile) is None


def test_validate_package_invalidates(invalid_lockfile):
    with pytest.raises(ValidationError):
        validate_package_against_schema(invalid_lockfile)


def test_validate_deployed_contracts_present_validates(lockfile_with_conflicting_deployments):
    with pytest.raises(ValidationError):
        validate_package_deployments(lockfile_with_conflicting_deployments)


def test_validate_deployments(lockfile_with_matching_deployment):
    validate = validate_package_deployments(lockfile_with_matching_deployment)
    assert validate is None


def test_validate_deployed_contracts_pr(lockfile_with_no_deployments):
    validate = validate_package_deployments(lockfile_with_no_deployments)
    assert validate is None
