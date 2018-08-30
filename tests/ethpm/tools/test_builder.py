import json
from pathlib import Path

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


@pytest.fixture
def owned_package(PACKAGING_EXAMPLES_DIR):
    root = PACKAGING_EXAMPLES_DIR / "owned"
    manifest = json.loads(Path(str(root / "1.0.0.json")).read_text())
    compiler = json.loads(Path(str(root / "combined.json")).read_text())["contracts"]
    return root, manifest, compiler


@pytest.fixture
def standard_token_package(PACKAGING_EXAMPLES_DIR):
    root = PACKAGING_EXAMPLES_DIR / "standard-token"
    manifest = json.loads(Path(str(root / "1.0.0.json")).read_text())
    compiler = json.loads(Path(str(root / "combined.json")).read_text())["contracts"]
    return root, manifest, compiler


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
    with pytest.raises(ValidationError, match="_invalid_package_name"):
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


def test_builder_with_inline_source(owned_package, monkeypatch):
    root, _, compiler_output = owned_package

    monkeypatch.chdir(str(root))
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


def test_builder_with_inline_source_with_package_root_dir_arg(owned_package):
    root, _, compiler_output = owned_package

    manifest = build(
        BASE_MANIFEST,
        inline_source("Owned", compiler_output, package_root_dir=root),
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


def test_builder_with_pin_source(owned_package, dummy_ipfs_backend):
    root, expected_manifest, compiler_output = owned_package
    ipfs_backend = get_ipfs_backend()

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
        pin_source("Owned", compiler_output, ipfs_backend, root),
        validate(),
    )

    assert manifest == expected_manifest


def test_builder_with_default_contract_types(owned_package):
    _, _, compiler_output = owned_package

    manifest = build(BASE_MANIFEST, contract_type("Owned", compiler_output), validate())

    contract_type_data = normalize_contract_type(tuple(compiler_output.values())[0])
    expected = assoc(BASE_MANIFEST, "contract_types", {"Owned": contract_type_data})
    assert manifest == expected


def test_builder_with_single_alias_kwarg(owned_package):
    _, _, compiler_output = owned_package

    manifest = build(
        BASE_MANIFEST,
        contract_type("Owned", compiler_output, alias="OwnedAlias"),
        validate(),
    )

    contract_type_data = normalize_contract_type(tuple(compiler_output.values())[0])
    expected = assoc(
        BASE_MANIFEST,
        "contract_types",
        {"OwnedAlias": assoc(contract_type_data, "contract_type", "Owned")},
    )
    assert manifest == expected


def test_builder_without_alias_and_with_select_contract_types(owned_package):
    _, _, compiler_output = owned_package

    manifest = build(
        BASE_MANIFEST,
        contract_type("Owned", compiler_output, abi=True, natspec=True),
        validate(),
    )

    contract_type_data = normalize_contract_type(tuple(compiler_output.values())[0])
    selected_data = {
        k: v for k, v in contract_type_data.items() if k != "deployment_bytecode"
    }
    expected = assoc(BASE_MANIFEST, "contract_types", {"Owned": selected_data})
    assert manifest == expected


def test_builder_with_alias_and_select_contract_types(owned_package):
    _, _, compiler_output = owned_package

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

    contract_type_data = normalize_contract_type(tuple(compiler_output.values())[0])
    expected = assoc(
        BASE_MANIFEST,
        "contract_types",
        {"OwnedAlias": assoc(contract_type_data, "contract_type", "Owned")},
    )
    assert manifest == expected


def test_builder_with_standard_token_manifest(
    standard_token_package, dummy_ipfs_backend, monkeypatch
):
    root, expected_manifest, compiler_output = standard_token_package
    ipfs_backend = get_ipfs_backend()

    monkeypatch.chdir(str(root))
    manifest = build(
        {},
        package_name("standard-token"),
        manifest_version("2"),
        version("1.0.0"),
        pin_source("StandardToken", compiler_output, ipfs_backend),
        pin_source("Token", compiler_output, ipfs_backend),
        contract_type("StandardToken", compiler_output, abi=True, natspec=True),
    )

    assert manifest == expected_manifest
