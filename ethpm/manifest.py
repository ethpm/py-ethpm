import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple  # ignore: F401

import cytoolz
from eth_utils import to_dict

from ethpm.backends.ipfs import BaseIPFSBackend, get_ipfs_backend
from ethpm.exceptions import ValidationError
from ethpm.utils.filesystem import load_json_from_file_path
from ethpm.utils.ipfs import create_ipfs_uri
from ethpm.validation import validate_manifest_version, validate_package_name

MANIFEST_FIELDS = [
    "manifest_version",
    "version",
    "package_name",
    "meta",
    "sources",
    "contract_types",
]

META_FIELDS = {
    "license": str,
    "authors": list,
    "description": str,
    "keywords": list,
    "links": dict,
}


def generate_manifest(
    manifest_version: str,
    package_name: str,
    version: str,
    meta: Dict[str, Any] = None,
    compiled_json_output_path: Path = None,
    contract_types: List[str] = None,
    build_dependencies: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Returns JSON manifest representing the input args.

    :manifest_version:  [required]
        "2"

    :package_name:      [required]
        string of the package name

    :version:           [required]
        string of the package version - semver is recommended

    :meta:              [optional]
        Dict containing any custom metadata for the package.
        Accepted fields:
        - `authors`         List[str]
        - `license`         str
        - `description`     str
        - `keywords`        List[str]
        - `links`           Dict[str,str]
            Recommended keys for `links`
            - `website`
            - `documentation`
            - `repository`

    :compiled_json_output_path:         [optional]
        string of the path to standard-json compiler output
        compiler output *must* be generated with `abi` & `devdoc` flags enabled

            i.e.
            `solc --output-dir ./ --combined-json
            abi,bin,bin-runtime,devdoc,interface,userdoc contracts/Owned.sol`

    :contract_types:    [optional]
        List[str] containing the contract types to be included in this manifest.
            * Packages should only include contract types that can be
              found in the source files for this package.
            * Packages should not include abstract contracts in the contract types section.
            * Packages should not include contract types from dependencies.

    :build_dependencies:[optional]
        Dict[str, str] with the package name pointing to a content-
        addressable URI which resolves to the package's manifest.
    """
    validate_manifest_version(manifest_version)
    validate_package_name(package_name)
    manifest = {
        "manifest_version": manifest_version,
        "package_name": package_name,
        "version": version,
    }
    build_fns = (
        build_meta(meta),
        build_sources(compiled_json_output_path),
        build_contract_types(compiled_json_output_path, contract_types),
        build_build_dependencies(build_dependencies),
    )
    cytoolz.pipe(manifest, *build_fns)
    return manifest


#
# Meta
#


@cytoolz.curry
def build_meta(meta: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate meta object keys and values, and attach object to manifest if valid.
    """
    if meta:
        validate_meta_object(meta)
        manifest["meta"] = meta
    return manifest


def validate_meta_object(meta: Dict[str, Any]) -> None:
    """
    Validates that every key is one of `META_FIELDS` and has a value of the expected type.
    """
    for key, value in meta.items():
        if key not in META_FIELDS:
            raise ValidationError("{0} is not a permitted meta field.".format(key))
        if type(value) is not META_FIELDS[key]:
            raise ValidationError(
                "Values for {0} are expected to have the type {1}, instead got {2}.".format(
                    key, META_FIELDS[key], type(value)
                )
            )


#
# Sources
#


@cytoolz.curry
def build_sources(
    compiled_json_output_path: Path, manifest: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate all source keys/values found in the linked compiled json output, and
    attach them to the manifest.
    """
    if compiled_json_output_path:
        manifest["sources"] = generate_all_sources(compiled_json_output_path)
    return manifest


@to_dict
def generate_all_sources(
    compiled_json_output_path: Path
) -> Generator[Tuple[str, str], None, None]:
    """
    Return a dict containing all of a Manifest's "sources" data.
    """
    compiled_json_output = load_json_from_file_path(compiled_json_output_path)
    ipfs_backend = get_ipfs_backend()
    for contract in compiled_json_output["contracts"]:
        contract_path, _ = contract.split(":")
        source_data = pin_single_source(
            contract_path, compiled_json_output_path, ipfs_backend
        )
        yield "./{0}".format(contract_path), source_data


def pin_single_source(
    contract_path: str, compiled_json_output_path: Path, ipfs_backend: BaseIPFSBackend
) -> str:
    """
    Return an IPFS URI, after pinning a source file to IPFS via `ipfs_backend`.
    """
    (ipfs_return_data,) = ipfs_backend.pin_assets(
        Path(compiled_json_output_path).parent / contract_path
    )
    ipfs_hash = ipfs_return_data["Hash"]
    return create_ipfs_uri(ipfs_hash)


#
# Contract Types
#


@cytoolz.curry
def build_contract_types(
    compiled_json_output_path: Path, contract_types: List[str], manifest: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a contract_type field for each contract_type listed in `contract_types`,
    and attach them to the manifest.
    """
    if compiled_json_output_path and contract_types:
        compiled_json_output = load_json_from_file_path(compiled_json_output_path)
        contract_types = generate_all_contract_types(
            compiled_json_output, contract_types
        )
        manifest["contract_types"] = contract_types
    return manifest


@to_dict
def generate_all_contract_types(
    compiled_json_output: Dict[str, Any], contract_types: List[str]
) -> Generator[Tuple[str, Any], None, None]:
    """
    Return a dict representing all of a Manifest's "contract_types" data.
    """
    for contract in compiled_json_output["contracts"]:
        _, contract_name = contract.split(":")
        if contract_name in contract_types:
            yield contract_name, generate_single_contract_type(
                contract, compiled_json_output
            )


@to_dict
def generate_single_contract_type(
    contract: str, compiled_json_output: Dict[str, Any]
) -> Generator[Tuple[str, Any], None, None]:
    """
    Return a dict represnting a single contract type.
    """
    yield "abi", json.loads(compiled_json_output["contracts"][contract]["abi"])
    yield "natspec", json.loads(compiled_json_output["contracts"][contract]["devdoc"])


#
# Build Dependencies
#


@cytoolz.curry
def build_build_dependencies(
    build_dependencies: Dict[str, str], manifest: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Will attach the build dependencies object, if specified in `generate_manifest` kwargs,
    and attach it to the manifest.
    """
    if build_dependencies:
        manifest["build_dependencies"] = build_dependencies
    return manifest
