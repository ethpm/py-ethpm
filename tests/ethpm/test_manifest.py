import json

from ethpm import V2_PACKAGES_DIR
from ethpm.manifest import generate_manifest

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

OWNED_META = {
    "license": "MIT",
    "authors": ["Piper Merriam <pipermerriam@gmail.com>"],
    "description": """Reusable contracts which implement a """
    """privileged 'owner' model for authorization.""",
    "keywords": ["authorization"],
    "links": {"documentation": "ipfs://QmUYcVzTfSwJoigggMxeo2g5STWAgJdisQsqcXHws7b1FW"},
}


def test_manifest_generates_pretty_and_minified_versions():
    manifest = generate_manifest(MANIFEST_VERSION, "package", PACKAGE_VERSION)
    assert manifest == json.loads(MINIFIED_MANIFEST)


def test_create_owned_manifest_with_meta(dummy_ipfs_backend, PACKAGING_EXAMPLES_DIR):
    package_name = "owned"
    OWNED_SOLC_OUTPUT = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    with open(str(V2_PACKAGES_DIR / package_name / "1.0.0.json")) as f:
        expected_json = json.load(f)
    manifest = generate_manifest(
        MANIFEST_VERSION,
        package_name,
        PACKAGE_VERSION,
        meta=OWNED_META,
        compiled_json_output_path=OWNED_SOLC_OUTPUT,
    )
    # Test that "sources" keys are equivalent, since expected_sources contains
    # ipfs hashes rather than inlined source code
    actual_sources = manifest.pop("sources")
    expected_sources = expected_json.pop("sources")
    assert manifest == expected_json
    assert actual_sources.keys() == expected_sources.keys()


def test_create_standard_token_manifest(dummy_ipfs_backend, PACKAGING_EXAMPLES_DIR):
    STANDARD_TOKEN_DIR = PACKAGING_EXAMPLES_DIR / "standard-token"
    STANDARD_TOKEN_SOLC_OUTPUT = STANDARD_TOKEN_DIR / "combined.json"
    package_name = "standard-token"
    # Cannot compare to ethpm-spec manifest b/c changes to AbstractToken.sol
    # to remove compilation warnings
    with open(str(STANDARD_TOKEN_DIR / "1.0.0.json")) as f:
        expected_json = json.load(f)
    manifest = generate_manifest(
        MANIFEST_VERSION,
        package_name,
        PACKAGE_VERSION,
        compiled_json_output_path=STANDARD_TOKEN_SOLC_OUTPUT,
        contract_types=["StandardToken"],
    )
    actual_sources = manifest.pop("sources")
    expected_sources = expected_json.pop("sources")
    assert manifest == expected_json
    assert actual_sources.keys() == expected_sources.keys()
