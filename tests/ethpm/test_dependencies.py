import pytest

from ethpm import Package
from ethpm.dependencies import Dependencies
from ethpm.exceptions import UriNotSupportedError
from ethpm.validation import validate_build_dependencies


@pytest.fixture
def dependencies(monkeypatch, standard_token_manifest, piper_coin_manifest):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    deps = piper_coin_manifest["build_dependencies"]
    dep_pkgs = {dep: Package.from_ipfs(uri) for dep, uri in deps.items()}
    return Dependencies(dep_pkgs)


@pytest.fixture
def safe_math_lib_package(safe_math_manifest):
    return Package(safe_math_manifest)


@pytest.fixture
def invalid_manifest(piper_coin_manifest):
    piper_coin_manifest["build_dependencies"]["_invalid_package_name"] = []
    return piper_coin_manifest


def test_dependencies_implements_getitem(dependencies, safe_math_lib_package):
    assert isinstance(dependencies, Dependencies)
    # difference in name is a result of using the DummyIPFSBackend class
    # TODO: update backend to return custom ipfs uris
    assert dependencies["standard-token"].name == "safe-math-lib"


def test_dependencies_items(dependencies):
    result = dependencies.items()
    assert "standard-token" in result
    assert isinstance(result["standard-token"], Package)


def test_dependencies_values(dependencies):
    result = dependencies.values()
    assert len(result) is 1
    assert isinstance(result[0], Package)


def test_get_dependency_package(dependencies):
    result = dependencies.get_dependency_package("standard-token")
    assert isinstance(result, Package)
    assert result.name == "safe-math-lib"


def test_validate_build_dependencies(monkeypatch, piper_coin_manifest):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    result = validate_build_dependencies(piper_coin_manifest["build_dependencies"])
    assert result is None


def test_get_build_dependencies_invalidates(invalid_manifest):
    with pytest.raises(UriNotSupportedError):
        validate_build_dependencies(invalid_manifest["build_dependencies"])
