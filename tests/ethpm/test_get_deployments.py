import pytest

from ethpm import Package

from ethpm.deployments import Deployments

from ethpm.exceptions import ValidationError


@pytest.mark.parametrize("notw3", ("notW3", 123, set()))
def test_get_deployments_with_invalid_w3_raise_exception(notw3, lockfile_with_matching_deployment):
    package = Package(lockfile_with_matching_deployment)
    with pytest.raises(ValueError):
        package.get_deployments(notw3)


def test_get_deployments_with_empty_deployment_raise_exception(w3, lockfile_with_empty_deployments):
    package = Package(lockfile_with_empty_deployments)
    with pytest.raises(ValidationError):
        package.get_deployments(w3)


def test_get_deployments_with_no_deployments_raises_exception(w3, lockfile_with_no_deployments):
    package = Package(lockfile_with_no_deployments)
    with pytest.raises(ValidationError):
        package.get_deployments(w3)


def test_get_deployments_with_no_match_raises_exception(w3, lockfile_with_no_matching_deployments):
    package = Package(lockfile_with_no_matching_deployments)
    with pytest.raises(ValidationError):
        package.get_deployments(w3)


def test_get_deployments_with_multiple_matches_raises_exception(w3, lockfile_with_multiple_matches):
    package = Package(lockfile_with_multiple_matches)
    with pytest.raises(ValidationError):
        package.get_deployments(w3)


def test_get_deployments_with_a_match_returns_deployments(w3, lockfile_with_matching_deployment):
    package = Package(lockfile_with_matching_deployment)
    deployment = package.get_deployments(w3)
    assert isinstance(deployment, Deployments)
