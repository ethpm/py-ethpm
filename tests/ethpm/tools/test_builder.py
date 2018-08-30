import json

from eth_utils.toolz import assoc
import pytest

from ethpm import Package
from ethpm.backends.ipfs import get_ipfs_backend
from ethpm.exceptions import ValidationError
from ethpm.tools.builder import (
    authors,
    build,
    contract_type,
    description,
    inline_source,
    keywords,
    license,
    links,
    manifest_version,
    normalize_contract_type,
    package_name,
    pin_source,
    return_package,
    validate,
    version,
)

BASE_MANIFEST = {"package_name": "package", "manifest_version": "2", "version": "1.0.0"}


def test_builder_simple():
    manifest = build(
        {}, package_name("package"), manifest_version("2"), version("1.0.0"), validate()
    )
    assert manifest == BASE_MANIFEST


def test_builder_simple_with_package(w3):
    package = build(
        {},
        package_name("package"),
        manifest_version("2"),
        version("1.0.0"),
        return_package(w3),
    )
    assert isinstance(package, Package)
    assert package.version == "1.0.0"


def test_builder_with_manifest_validation():
    with pytest.raises(ValidationError):
        build(
            {},
            package_name("_invalid_package_name"),
            manifest_version("2"),
            version("1.0.0"),
            validate(),
        )


@pytest.mark.parametrize(
    "fn,value",
    (
        (authors("some", "guy"), {"authors": ["some", "guy"]}),
        (license("MIT"), {"license": "MIT"}),
        (description("This is a package."), {"description": "This is a package."}),
        (keywords("awesome", "package"), {"keywords": ["awesome", "package"]}),
        (
            links(documentation="ipfs..", website="www"),
            {"links": {"documentation": "ipfs..", "website": "www"}},
        ),
    ),
)
def test_builder_with_simple_meta_fields(fn, value):
    manifest = build(BASE_MANIFEST, fn, validate())
    expected = assoc(BASE_MANIFEST, "meta", value)
    assert manifest == expected


def test_builder_simple_with_multi_meta_field():
    manifest = build(
        BASE_MANIFEST,
        authors("some", "guy"),
        license("MIT"),
        description("description"),
        keywords("awesome", "package"),
        links(website="www", repository="github"),
        validate(),
    )
    expected = assoc(
        BASE_MANIFEST,
        "meta",
        {
            "license": "MIT",
            "authors": ["some", "guy"],
            "description": "description",
            "keywords": ["awesome", "package"],
            "links": {"website": "www", "repository": "github"},
        },
    )
    assert manifest == expected


def test_builder_with_inline_source(PACKAGING_EXAMPLES_DIR, monkeypatch):
    package_root_dir = PACKAGING_EXAMPLES_DIR / "owned"
    owned_output = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    compiler_output = json.loads(owned_output.read_text())["contracts"]

    monkeypatch.chdir(package_root_dir)
    manifest = build(BASE_MANIFEST, inline_source("Owned", compiler_output), validate())

    expected = assoc(
        BASE_MANIFEST,
        "sources",
        {
            "./contracts/Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
            """ owner;\n    \n    modifier onlyOwner { require(msg.sender == owner); _; }\n\n    """
            """constructor() public {\n        owner = msg.sender;\n    }\n}\n"""
        },
    )
    assert manifest == expected


def test_builder_with_inline_source_with_package_root_dir_arg(PACKAGING_EXAMPLES_DIR):
    package_root_dir = PACKAGING_EXAMPLES_DIR / "owned"
    owned_output = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    compiler_output = json.loads(owned_output.read_text())["contracts"]
    manifest = build(
        BASE_MANIFEST,
        inline_source("Owned", compiler_output, package_root_dir=package_root_dir),
        validate(),
    )
    expected = assoc(
        BASE_MANIFEST,
        "sources",
        {
            "./contracts/Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
            """ owner;\n    \n    modifier onlyOwner { require(msg.sender == owner); _; }\n\n    """
            """constructor() public {\n        owner = msg.sender;\n    }\n}\n"""
        },
    )
    assert manifest == expected


def test_builder_with_pin_source(PACKAGING_EXAMPLES_DIR, dummy_ipfs_backend):
    package_root_dir = PACKAGING_EXAMPLES_DIR / "owned"
    expected_manifest = package_root_dir / "1.0.0.json"
    owned_output = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    ipfs_backend = get_ipfs_backend()
    compiler_output = json.loads(owned_output.read_text())["contracts"]

    manifest = build(
        {},
        package_name("owned"),
        manifest_version("2"),
        version("1.0.0"),
        authors("Piper Merriam <pipermerriam@gmail.com>"),
        description(
            "Reusable contracts which implement a privileged 'owner' model for authorization."
        ),
        keywords("authorization"),
        license("MIT"),
        links(documentation="ipfs://QmUYcVzTfSwJoigggMxeo2g5STWAgJdisQsqcXHws7b1FW"),
        pin_source("Owned", compiler_output, ipfs_backend, package_root_dir),
        validate(),
    )

    assert manifest == json.loads(expected_manifest.read_text())


def test_builder_with_default_contract_types(PACKAGING_EXAMPLES_DIR):
    owned_output = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    compiler_output = json.loads(owned_output.read_text())["contracts"]

    manifest = build(BASE_MANIFEST, contract_type("Owned", compiler_output), validate())

    xx = normalize_contract_type(tuple(compiler_output.values())[0])
    expected = assoc(BASE_MANIFEST, "contract_types", {"Owned": xx})
    assert manifest == expected


def test_builder_with_aliased_contract_types(PACKAGING_EXAMPLES_DIR):
    owned_output = PACKAGING_EXAMPLES_DIR / "owned" / "combined.json"
    compiler_output = json.loads(owned_output.read_text())["contracts"]

    manifest = build(
        BASE_MANIFEST,
        contract_type(
            "Owned",
            compiler_output,
            alias="OwnedAlias",
            abi=True,
            natspec=True,
            deployment_bytecode=True,
        ),
        validate(),
    )

    xx = normalize_contract_type(tuple(compiler_output.values())[0])
    expected = assoc(
        BASE_MANIFEST,
        "contract_types",
        {"OwnedAlias": assoc(xx, "contract_type", "Owned")},
    )
    assert manifest == expected


def test_builder_with_standard_token_manifest(
    PACKAGING_EXAMPLES_DIR, dummy_ipfs_backend, monkeypatch
):
    standard_token_output = PACKAGING_EXAMPLES_DIR / "standard-token" / "combined.json"
    expected_manifest = PACKAGING_EXAMPLES_DIR / "standard-token" / "1.0.0.json"
    compiler_output = json.loads(standard_token_output.read_text())["contracts"]
    ipfs_backend = get_ipfs_backend()

    monkeypatch.chdir(PACKAGING_EXAMPLES_DIR / "standard-token")
    manifest = build(
        {},
        package_name("standard-token"),
        manifest_version("2"),
        version("1.0.0"),
        pin_source("StandardToken", compiler_output, ipfs_backend),
        pin_source("Token", compiler_output, ipfs_backend),
        contract_type("StandardToken", compiler_output, abi=True, natspec=True),
    )

    expected = json.loads(expected_manifest.read_text())
    assert manifest == expected
