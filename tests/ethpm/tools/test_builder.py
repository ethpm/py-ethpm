import json
from pathlib import Path

from eth_utils.toolz import assoc
import pytest

from ethpm import ASSETS_DIR, Package
from ethpm.backends.ipfs import get_ipfs_backend
from ethpm.exceptions import ManifestBuildingError, ValidationError
from ethpm.tools.builder import (
    as_package,
    authors,
    build,
    contract_type,
    description,
    init_manifest,
    inline_source,
    keywords,
    license,
    links,
    manifest_version,
    normalize_contract_type,
    package_name,
    pin_source,
    source_inliner,
    source_pinner,
    to_disk,
    validate,
    version,
)

BASE_MANIFEST = {"package_name": "package", "manifest_version": "2", "version": "1.0.0"}


@pytest.fixture
def owned_package():
    root = ASSETS_DIR / "owned"
    manifest = json.loads(Path(str(root / "1.0.0.json")).read_text())
    compiler = json.loads(Path(str(root / "owned_compiler_output.json")).read_text())[
        "contracts"
    ]
    contracts_dir = root / "contracts"
    return contracts_dir, manifest, compiler


# todo validate no duplicate contracts in package


@pytest.fixture
def standard_token_package():
    root = ASSETS_DIR / "standard-token"
    manifest = json.loads(Path(str(root / "1.0.0.json")).read_text())
    compiler = json.loads(
        Path(str(root / "standard_token_compiler_output.json")).read_text()
    )["contracts"]
    contracts_dir = root / "contracts"
    return contracts_dir, manifest, compiler


@pytest.fixture
def registry_package():
    root = ASSETS_DIR / "registry"
    compiler = json.loads(
        Path(str(root / "registry_compiler_output.json")).read_text()
    )["contracts"]
    contracts_dir = root / "contracts"
    manifest = json.loads(Path(str(root / "1.0.0.json")).read_text())
    return contracts_dir, manifest, compiler


@pytest.fixture
def manifest_dir(tmpdir):
    return Path(str(tmpdir.mkdir("sub")))


def test_builder_simple_with_package(w3):
    package = build(
        {},
        package_name("package"),
        manifest_version("2"),
        version("1.0.0"),
        as_package(w3),
    )
    assert isinstance(package, Package)
    assert package.version == "1.0.0"


PRETTY_MANIFEST = """{
    "manifest_version": "2",
    "package_name": "package",
    "version": "1.0.0"
}"""

MINIFIED_MANIFEST = (
    '{"manifest_version":"2","package_name":"package","version":"1.0.0"}'
)


def test_builder_writes_manifest_to_disk(manifest_dir):
    build(
        {},
        package_name("package"),
        manifest_version("2"),
        version("1.0.0"),
        to_disk(
            manifest_root_dir=manifest_dir, manifest_name="1.0.0.json", prettify=True
        ),
    )
    with open(str(manifest_dir / "1.0.0.json")) as f:
        actual_manifest = f.read()
    assert actual_manifest == PRETTY_MANIFEST


def test_builder_to_disk_uses_default_cwd(manifest_dir, monkeypatch):
    monkeypatch.chdir(str(manifest_dir))
    build(
        {}, package_name("package"), manifest_version("2"), version("1.0.0"), to_disk()
    )
    with open(str(manifest_dir / "1.0.0.json")) as f:
        actual_manifest = f.read()
    assert actual_manifest == MINIFIED_MANIFEST


def test_to_disk_writes_minified_manifest_as_default(manifest_dir):
    build(
        {},
        package_name("package"),
        manifest_version("2"),
        version("1.0.0"),
        to_disk(manifest_root_dir=manifest_dir, manifest_name="1.0.0.json"),
    )
    with open(str(manifest_dir / "1.0.0.json")) as f:
        actual_manifest = f.read()
    assert actual_manifest == MINIFIED_MANIFEST


def test_to_disk_uses_default_manifest_name(manifest_dir):
    build(
        {},
        package_name("package"),
        manifest_version("2"),
        version("1.0.0"),
        to_disk(manifest_root_dir=manifest_dir),
    )
    with open(str(manifest_dir / "1.0.0.json")) as f:
        actual_manifest = f.read()
    assert actual_manifest == MINIFIED_MANIFEST


@pytest.mark.parametrize(
    "to_disk_fn",
    (
        to_disk(manifest_root_dir=Path("not/a/directory")),
        to_disk(manifest_name="invalid_name"),
    ),
)
def test_to_disk_with_invalid_args_raises_exception(manifest_dir, to_disk_fn):
    with pytest.raises(ManifestBuildingError):
        build(
            {},
            package_name("package"),
            manifest_version("2"),
            version("1.0.0"),
            to_disk_fn,
        )


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
            "Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
            """ owner;\n    \n    modifier onlyOwner { require(msg.sender == owner); _; }\n\n    """
            """constructor() public {\n        owner = msg.sender;\n    }\n}\n"""
        },
    )
    assert manifest == expected


def test_builder_with_source_inliner(owned_package, monkeypatch):
    root, _, compiler_output = owned_package

    monkeypatch.chdir(str(root))
    inliner = source_inliner(compiler_output)
    manifest = build(BASE_MANIFEST, inliner("Owned"), validate())

    expected = assoc(
        BASE_MANIFEST,
        "sources",
        {
            "Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
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
            "Owned.sol": """pragma solidity ^0.4.24;\n\ncontract Owned {\n    address"""
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


def test_builder_with_pinner(owned_package, dummy_ipfs_backend):
    root, expected_manifest, compiler_output = owned_package
    ipfs_backend = get_ipfs_backend()
    pinner = source_pinner(compiler_output, ipfs_backend, root)
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
        pinner("Owned"),
        validate(),
    )

    assert manifest == expected_manifest


def test_builder_with_init_manifest(owned_package, dummy_ipfs_backend):
    root, expected_manifest, compiler_output = owned_package
    ipfs_backend = get_ipfs_backend()

    manifest = build(
        init_manifest(package_name="owned", version="1.0.0"),
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

    contract_type_data = normalize_contract_type(compiler_output["Owned.sol"]["Owned"])
    expected = assoc(BASE_MANIFEST, "contract_types", {"Owned": contract_type_data})
    assert manifest == expected


def test_builder_with_single_alias_kwarg(owned_package):
    _, _, compiler_output = owned_package

    manifest = build(
        BASE_MANIFEST,
        contract_type("Owned", compiler_output, alias="OwnedAlias"),
        validate(),
    )

    contract_type_data = normalize_contract_type(compiler_output["Owned.sol"]["Owned"])
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

    contract_type_data = normalize_contract_type(compiler_output["Owned.sol"]["Owned"])
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

    contract_type_data = normalize_contract_type(compiler_output["Owned.sol"]["Owned"])
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
        validate(),
    )
    assert manifest == expected_manifest


def test_builder_with_link_references(
    registry_package, dummy_ipfs_backend, monkeypatch
):
    root, expected_manifest, compiler_output = registry_package
    ipfs_backend = get_ipfs_backend()
    monkeypatch.chdir(str(root))
    pinner = source_pinner(compiler_output, ipfs_backend)
    manifest = build(
        {},
        package_name("registry"),
        manifest_version("2"),
        version("1.0.0"),
        pinner("Authority"),
        pinner("IndexedOrderedSetLib"),
        pinner("PackageDB"),
        pinner("PackageIndex"),
        pinner("PackageIndexInterface"),
        pinner("ReleaseDB"),
        pinner("ReleaseValidator"),
        pinner("SemVersionLib"),
        contract_type("Authorized", compiler_output, abi=True),
        contract_type("IndexedOrderedSetLib", compiler_output, abi=True),
        contract_type("PackageDB", compiler_output, abi=True, deployment_bytecode=True),
        contract_type("PackageIndex", compiler_output, abi=True),
        contract_type("PackageIndexInterface", compiler_output, abi=True),
        contract_type("ReleaseDB", compiler_output, abi=True, deployment_bytecode=True),
        contract_type("ReleaseValidator", compiler_output, abi=True),
        contract_type(
            "SemVersionLib", compiler_output, abi=True, deployment_bytecode=True
        ),
        validate(),
    )
    assert manifest == expected_manifest
