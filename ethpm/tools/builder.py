import functools
import json
import operator
import os
from pathlib import Path
from typing import Any, Dict, Generator, NewType

from eth_utils import add_0x_prefix, to_dict
from eth_utils.toolz import assoc, assoc_in, curry, pipe
from web3 import Web3

from ethpm import Package
from ethpm.backends.ipfs import BaseIPFSBackend
from ethpm.exceptions import ManifestBuildingError
from ethpm.utils.manifest_validation import validate_manifest_against_schema

Manifest = NewType("Manifest", Dict[str, Any])


def build(obj, *fns):
    return pipe(obj, *fns)


#
# Required Fields
#


@curry
def package_name(name: str, manifest: Manifest) -> Manifest:
    return assoc(manifest, "package_name", name)


@curry
def manifest_version(manifest_version: str, manifest: Manifest) -> Manifest:
    return assoc(manifest, "manifest_version", manifest_version)


@curry
def version(version: str, manifest: Manifest) -> Manifest:
    return assoc(manifest, "version", version)


#
# Meta
#


def authors(*author_list):
    return _authors(author_list)


@curry
@functools.wraps(authors)
def _authors(authors: set, manifest: Manifest) -> Manifest:
    return assoc_in(manifest, ("meta", "authors"), list(authors))


@curry
def license(license: str, manifest: Manifest) -> Manifest:
    return assoc_in(manifest, ("meta", "license"), license)


@curry
def description(description: str, manifest: Manifest) -> Manifest:
    return assoc_in(manifest, ("meta", "description"), description)


def keywords(*keyword_list):
    return _keywords(keyword_list)


@curry
@functools.wraps(keywords)
def _keywords(keywords: set, manifest: Manifest) -> Manifest:
    return assoc_in(manifest, ("meta", "keywords"), list(keywords))


def links(**link_dict):
    return _links(link_dict)


@curry
def _links(link_dict: Dict[str, str], manifest: Manifest) -> Manifest:
    return assoc_in(manifest, ("meta", "links"), link_dict)


#
# Sources
#


def get_names_and_paths(compiler_output: Dict[str, Any]) -> Dict[str, str]:
    return {
        name: path
        for path, sep, name in map(
            operator.methodcaller("partition", ":"), compiler_output
        )
    }


def inline_source(
    name: str, compiler_output: Dict[str, Any], package_root_dir: str = None
) -> Manifest:
    return _inline_source(name, compiler_output, package_root_dir)


@curry
def _inline_source(
    name: str,
    compiler_output: Dict[str, Any],
    package_root_dir: str,
    manifest: Manifest,
) -> Manifest:
    names_and_paths = get_names_and_paths(compiler_output)
    cwd = Path(os.getcwd())
    source_path_suffix = names_and_paths[name]

    if (cwd / source_path_suffix).is_file():
        source_data = (cwd / source_path_suffix).read_text()
    elif package_root_dir and (package_root_dir / source_path_suffix).is_file():
        source_data = (package_root_dir / source_path_suffix).read_text()
    else:
        raise ManifestBuildingError("package_root_dir is wrong, plz fix")

    if "sources" not in manifest:
        manifest["sources"] = {}

    return assoc(
        manifest,
        "sources",
        assoc(manifest["sources"], "./{0}".format(source_path_suffix), source_data),
    )


def pin_source(
    name: str,
    compiler_output: Dict[str, Any],
    ipfs_backend: BaseIPFSBackend,
    package_root_dir: str = None,
) -> Manifest:
    return _pin_source(name, compiler_output, ipfs_backend, package_root_dir)


@curry
def _pin_source(
    name: str,
    compiler_output: Dict[str, Any],
    ipfs_backend: BaseIPFSBackend,
    package_root_dir: str,
    manifest: Manifest,
) -> Manifest:
    names_and_paths = get_names_and_paths(compiler_output)
    source_path = names_and_paths[name]
    if package_root_dir:
        (ipfs_data,) = ipfs_backend.pin_assets(package_root_dir / source_path)
    else:
        cwd = Path(os.getcwd())
        (ipfs_data,) = ipfs_backend.pin_assets(cwd / source_path)

    if "sources" not in manifest:
        manifest["sources"] = {}

    return assoc(
        manifest,
        "sources",
        assoc(
            manifest["sources"],
            "./{0}".format(source_path),
            "ipfs://{0}".format(ipfs_data["Hash"]),
        ),
    )


#
# Contract Types
#


def contract_type(name: str, compiler_output: Dict[str, Any], **kwargs) -> Manifest:
    return _contract_type(name, compiler_output, kwargs)


@curry
def _contract_type(
    name: str, compiler_output: Dict[str, Any], kwargs, manifest: Manifest
) -> Manifest:
    contracts_by_name = normalize_compiler_output(compiler_output)
    if name not in contracts_by_name:
        raise ManifestBuildingError(
            "Contract by name of {0} was not found in the provided compiler output.".format(
                name
            )
        )

    contract_type_data = contracts_by_name[name]
    if kwargs:
        contract_type_data = {
            k: v for k, v in contracts_by_name[name].items() if k in kwargs
        }

    if "alias" in kwargs:
        # require 'contract_type' in kwargs?
        contract_type_field = assoc(contract_type_data, "contract_type", name)
        return assoc_in(
            manifest, ["contract_types", kwargs["alias"]], contract_type_field
        )

    return assoc_in(manifest, ["contract_types", name], contract_type_data)


@to_dict
def normalize_compiler_output(compiler_output: Dict[str, Any]) -> Dict[str, str]:
    paths_and_names = [
        (path, name)
        for path, sep, name in map(
            operator.methodcaller("partition", ":"), compiler_output
        )
    ]
    paths, names = zip(*paths_and_names)
    if len(names) != len(set(names)):
        raise ManifestBuildingError("duplicate names!")
    return {
        name: normalize_contract_type(compiler_output[":".join((path, name))])
        for path, name in paths_and_names
    }


@to_dict
def normalize_contract_type(
    contract_type_data: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    yield "abi", json.loads(contract_type_data["abi"])
    yield "deployment_bytecode", {"bytecode": add_0x_prefix(contract_type_data["bin"])}
    yield "natspec", json.loads(contract_type_data["devdoc"])


#
# Formatting
#


@curry
def validate(manifest: Manifest) -> Manifest:
    validate_manifest_against_schema(manifest)
    return manifest


@curry
def return_package(w3: Web3, manifest: Manifest) -> Package:
    return Package(manifest, w3)
