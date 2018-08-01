import json

import pytest
from tests import PACKAGING_EXAMPLES_DIR

from ethpm import V2_PACKAGES_DIR
from ethpm.manifest import Manifest

MANIFEST_VERSION = "2"

PACKAGE_VERSION = "1.0.0"

PRETTY_MANIFEST = """{
    "manifest_version": "2",
    "package_name": "package",
    "version": "1.0.0"
}"""

MINIFIED_MANIFEST = (
    '{"manifest_version":"2","package_name":"package","version":"1.0.0"}'
)

STANDARD_TOKEN_DIR = PACKAGING_EXAMPLES_DIR / "standard-token"

STANDARD_TOKEN_SOLC_OUTPUT = STANDARD_TOKEN_DIR / "combined.json"

OWNED_DIR = PACKAGING_EXAMPLES_DIR / "owned"


def test_manifest_generates_pretty_and_minified_versions():
    manifest = Manifest(MANIFEST_VERSION, "package", PACKAGE_VERSION)
    assert isinstance(manifest, Manifest)
    assert manifest.minified() == MINIFIED_MANIFEST
    assert manifest.pretty() == PRETTY_MANIFEST


def test_create_owned_manifest_with_meta(dummy_ipfs_backend):
    package_name = "owned"
    with open(str(V2_PACKAGES_DIR / package_name / "1.0.0.json")) as f:
        expected_json = json.load(f)
    expected_minified = json.dumps(expected_json, separators=(",", ":"), sort_keys=True)
    owned_solc_output = OWNED_DIR / "combined.json"
    manifest = Manifest(MANIFEST_VERSION, package_name, PACKAGE_VERSION)
    manifest.add_meta(
        license="MIT",
        authors=["Piper Merriam <pipermerriam@gmail.com>"],
        description="""Reusable contracts which implement a privileged 'owner' model for authorization.""",  # noqa: E501
        keywords=["authorization"],
        links={
            "documentation": "ipfs://QmUYcVzTfSwJoigggMxeo2g5STWAgJdisQsqcXHws7b1FW"
        },
    )
    manifest.link_solc_output(owned_solc_output)
    actual_minified = manifest.minified()
    assert isinstance(manifest, Manifest)
    assert manifest.manifest_version == MANIFEST_VERSION
    assert manifest.package_name == package_name
    assert manifest.version == PACKAGE_VERSION
    assert actual_minified == expected_minified


def test_create_standard_token_manifest(dummy_ipfs_backend):
    package_name = "standard-token"
    # Cannot compare to ethpm-spec manifest b/c changes to AbstractToken.sol
    # to remove compilation warnings
    with open(str(STANDARD_TOKEN_DIR / "1.0.0.json")) as f:
        expected_json = json.load(f)
    expected_minified = json.dumps(expected_json, separators=(",", ":"), sort_keys=True)
    manifest = Manifest(MANIFEST_VERSION, package_name, PACKAGE_VERSION)
    manifest.link_solc_output(STANDARD_TOKEN_SOLC_OUTPUT, ["StandardToken"])
    actual_minified = manifest.minified()
    assert isinstance(manifest, Manifest)
    assert manifest.manifest_version == MANIFEST_VERSION
    assert manifest.package_name == package_name
    assert manifest.version == PACKAGE_VERSION
    assert actual_minified == expected_minified


def test_linking_solc_output_twice_raises_exception(dummy_ipfs_backend):
    manifest = Manifest(MANIFEST_VERSION, "package", PACKAGE_VERSION)
    manifest.link_solc_output(OWNED_DIR / "combined.json")
    with pytest.raises(AttributeError):
        manifest.link_solc_output(OWNED_DIR / "combined.json")


def test_write_minified_manifest_to_disk(dummy_ipfs_backend):
    package_name = "standard-token"
    manifest = Manifest(MANIFEST_VERSION, package_name, PACKAGE_VERSION)
    manifest.link_solc_output(STANDARD_TOKEN_SOLC_OUTPUT, ["StandardToken"])
    minified_path = manifest.write_minified_to_disk()
    with open(str(STANDARD_TOKEN_DIR / "1.0.0.json")) as f:
        expected_minified_contents = f.read().strip("\n")
    with open(str(minified_path)) as f:
        actual_minified_contents = f.read()
    assert actual_minified_contents == expected_minified_contents
