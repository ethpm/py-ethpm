import pytest

from ethpm.exceptions import ValidationError

from ethpm.utils.package_validation import (
    validate_package_exists,
    validate_package_against_schema,
    validate_package_deployments,
)


def test_validate_package_exists_validates():
    assert validate_package_exists("safe-math-lib/1.0.0.json") is None


def test_validate_package_exists_invalidates():
    with pytest.raises(ValidationError):
        validate_package_exists("DNE")


def test_validate_package_validates(valid_package):
    assert validate_package_against_schema(valid_package) is None


def test_validate_package_against_all_packages(all_packages):
    for pkg in all_packages:
        assert validate_package_against_schema(pkg) is None


def test_validate_package_invalidates(invalid_package):
    with pytest.raises(ValidationError):
        validate_package_against_schema(invalid_package)


def test_validate_deployed_contracts_present_validates(package_with_conflicting_deployments):
    with pytest.raises(ValidationError):
        validate_package_deployments(package_with_conflicting_deployments)


def test_validate_deployments(package_with_matching_deployment):
    validate = validate_package_deployments(package_with_matching_deployment)
    assert validate is None


def test_validate_deployed_contracts_pr(package_with_no_deployments):
    validate = validate_package_deployments(package_with_no_deployments)
    assert validate is None
