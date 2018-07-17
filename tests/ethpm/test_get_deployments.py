import pytest

from ethpm import Package
from ethpm.deployments import Deployments
from ethpm.exceptions import ValidationError


@pytest.fixture
def matching_package(manifest_with_matching_deployment):
    manifest, w3 = manifest_with_matching_deployment
    return Package(manifest, w3)


def test_get_deployments_with_empty_deployment_raise_exception(
    w3, manifest_with_empty_deployments
):
    package = Package(manifest_with_empty_deployments, w3)
    with pytest.raises(ValidationError):
        package.get_deployments()


def test_get_deployments_with_no_deployments_raises_exception(
    w3, manifest_with_no_deployments
):
    package = Package(manifest_with_no_deployments, w3)
    with pytest.raises(ValidationError):
        package.get_deployments()


def test_get_deployments_with_no_match_raises_exception(
    manifest_with_no_matching_deployments
):
    manifest, w3 = manifest_with_no_matching_deployments
    package = Package(manifest, w3)
    with pytest.raises(ValidationError):
        package.get_deployments()


def test_get_deployments_with_multiple_matches_raises_exception(
    manifest_with_multiple_matches
):
    manifest, w3 = manifest_with_multiple_matches
    package = Package(manifest, w3)
    with pytest.raises(ValidationError):
        package.get_deployments()


def test_get_deployments_with_a_match_returns_deployments(w3, matching_package):
    deployment = matching_package.get_deployments()
    assert isinstance(deployment, Deployments)
    assert "SafeMathLib" in deployment
