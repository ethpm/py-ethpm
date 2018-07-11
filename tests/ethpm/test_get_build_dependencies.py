import pytest

from ethpm import Package
from ethpm.dependencies import Dependencies
from ethpm.exceptions import ValidationError


def test_get_build_dependencies(monkeypatch, piper_coin_manifest, w3):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    pkg = Package(piper_coin_manifest, w3)
    build_deps = pkg.get_build_dependencies()
    assert isinstance(build_deps, Dependencies)


def test_get_build_dependencies_without_dependencies_raises_exception(
    piper_coin_manifest
):
    piper_coin_manifest.pop("build_dependencies", None)
    pkg = Package(piper_coin_manifest)
    with pytest.raises(ValidationError):
        pkg.get_build_dependencies()


def test_get_build_dependencies_with_empty_dependencies_raises_exception(
    monkeypatch, piper_coin_manifest
):
    monkeypatch.setenv(
        "ETHPM_IPFS_BACKEND_CLASS", "ethpm.backends.ipfs.DummyIPFSBackend"
    )
    piper_coin_manifest["build_dependencies"] = {}
    pkg = Package(piper_coin_manifest)
    with pytest.raises(ValidationError):
        pkg.get_build_dependencies()
