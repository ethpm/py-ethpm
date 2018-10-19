import json
from typing import Any, Dict, Generator, Tuple, Union

from eth_utils import to_canonical_address, to_text, to_tuple
from web3 import Web3
from web3.eth import Contract

from ethpm.contract import LinkableContract
from ethpm.dependencies import Dependencies
from ethpm.deployments import Deployments
from ethpm.exceptions import (
    BytecodeLinkingError,
    FailureToFetchIPFSAssetsError,
    InsufficientAssetsError,
    PyEthPMError,
)
from ethpm.typing import Address, ContractName
from ethpm.utils.backend import resolve_uri_contents
from ethpm.utils.cache import cached_property
from ethpm.utils.contract import (
    generate_contract_factory_kwargs,
    validate_contract_name,
    validate_minimal_contract_factory_data,
    validate_w3_instance,
)
from ethpm.utils.deployments import (
    get_linked_deployments,
    normalize_linked_references,
    validate_deployments_tx_receipt,
    validate_linked_references,
)
from ethpm.utils.filesystem import load_manifest_from_file
from ethpm.utils.manifest_validation import (
    check_for_deployments,
    validate_build_dependencies_are_present,
    validate_manifest_against_schema,
    validate_manifest_deployments,
)
from ethpm.validation import (
    validate_address,
    validate_build_dependency,
    validate_single_matching_uri,
)


class Package(object):
    def __init__(self, manifest: Dict[str, Any], w3: Web3) -> None:
        """
        A package should be created using one of the available
        classmethods and a valid w3 instance.
        """
        if not isinstance(manifest, dict):
            raise TypeError(
                "Package object must be initialized with a dictionary. "
                f"Got {type(manifest)}"
            )

        validate_manifest_against_schema(manifest)
        validate_manifest_deployments(manifest)
        validate_w3_instance(w3)

        self.w3 = w3
        self.w3.eth.defaultContractFactory = LinkableContract
        self.manifest = manifest

    def set_default_w3(self, w3: Web3) -> None:
        """
        Set the default Web3 instance.
        """
        validate_w3_instance(w3)
        # Mechanism to bust cached properties when switching chains.
        if "deployments" in self.__dict__:
            del self.deployments
        if "build_dependencies" in self.__dict__:
            del self.build_dependencies
        self.w3 = w3
        self.w3.eth.defaultContractFactory = LinkableContract

    def __repr__(self) -> str:
        name = self.name
        version = self.version
        return f"<Package {name}=={version}>"

    @property
    def name(self) -> str:
        return self.manifest["package_name"]

    @property
    def version(self) -> str:
        return self.manifest["version"]

    @property
    def manifest_version(self) -> str:
        return self.manifest["manifest_version"]

    @classmethod
    def from_file(cls, file_path_or_obj: str, w3: Web3) -> "Package":
        """
        Return a Package object instantiated by a manifest located at the provided filepath.
        """
        if isinstance(file_path_or_obj, str):
            with open(file_path_or_obj) as file_obj:
                manifest = load_manifest_from_file(file_obj)
        elif hasattr(file_path_or_obj, "read") and callable(file_path_or_obj.read):
            manifest = load_manifest_from_file(file_path_or_obj)
        else:
            raise TypeError(
                "The Package.from_file method takes either a filesystem path or a file-like object."
                f"Got {type(file_path_or_obj)} instead."
            )

        return cls(manifest, w3)

    @classmethod
    def from_uri(cls, uri: str, w3: Web3) -> "Package":
        """
        Return a Package object instantiated by a manifest located at a content-addressed URI.
        URI schemes supported:
            - IPFS          `ipfs://Qm...`
            - HTTP          `https://raw.githubusercontent.com/repo/path.json#hash`
            - Registry      `ercXXX://registry.eth/greeter?version=1.0.0`
        """
        contents = resolve_uri_contents(uri)
        manifest = json.loads(to_text(contents))
        return cls(manifest, w3)

    def get_contract_factory(self, name: ContractName) -> Contract:
        """
        Return a contract factory for a given contract type.
        """
        validate_contract_name(name)

        if "contract_types" not in self.manifest:
            raise InsufficientAssetsError(
                "This package does not contain any contract type data."
            )

        try:
            contract_data = self.manifest["contract_types"][name]
        except KeyError:
            raise InsufficientAssetsError(
                "This package does not contain any package data to generate "
                f"a contract factory for contract type: {name}. Available contract types include: "
                f"{ list(self.manifest['contract_types'].keys()) }."
            )

        validate_minimal_contract_factory_data(contract_data)
        contract_kwargs = generate_contract_factory_kwargs(contract_data)
        contract_factory = self.w3.eth.contract(**contract_kwargs)
        return contract_factory

    def get_contract_instance(self, name: ContractName, address: Address) -> Contract:
        """
        Return a Contract object representing the contract type at the provided address.
        """
        validate_address(address)
        validate_contract_name(name)
        try:
            self.manifest["contract_types"][name]["abi"]
        except KeyError:
            raise InsufficientAssetsError(
                "Package does not have the ABI required to generate a contract instance "
                f"for contract: {name} at address: {address}."
            )
        contract_kwargs = generate_contract_factory_kwargs(
            self.manifest["contract_types"][name]
        )
        canonical_address = to_canonical_address(address)
        contract_instance = self.w3.eth.contract(
            address=canonical_address, **contract_kwargs
        )
        return contract_instance

    #
    # Build Dependencies
    #

    @cached_property
    def build_dependencies(self) -> "Dependencies":
        """
        Return `Dependencies` instance containing the build dependencies available on this Package.
        Cached property (self.build_dependencies) busted everytime self.set_default_w3() is called.
        """
        validate_build_dependencies_are_present(self.manifest)

        dependencies = self.manifest["build_dependencies"]
        dependency_packages = {}
        for name, uri in dependencies.items():
            try:
                validate_build_dependency(name, uri)
                dependency_package = Package.from_uri(uri, self.w3)
            except PyEthPMError as e:
                raise FailureToFetchIPFSAssetsError(
                    f"Failed to retrieve build dependency: {name} from URI: {uri}.\n"
                    f"Got error: {e}."
                )
            else:
                dependency_packages[name] = dependency_package

        return Dependencies(dependency_packages)

    #
    # Deployments
    #

    @cached_property
    def deployments(self) -> Union["Deployments", Dict[None, None]]:
        """
        API to retrieve package deployments available on the current w3-connected chain.
        Cached property (self.deployments) gets busted everytime self.set_default_w3() is called.
        """
        if not check_for_deployments(self.manifest):
            return {}

        all_blockchain_uris = self.manifest["deployments"].keys()
        matching_uri = validate_single_matching_uri(all_blockchain_uris, self.w3)

        deployments = self.manifest["deployments"][matching_uri]
        all_contract_factories = {
            deployment_data["contract_type"]: self.get_contract_factory(
                deployment_data["contract_type"]
            )
            for deployment_data in deployments.values()
        }
        validate_deployments_tx_receipt(deployments, self.w3)
        linked_deployments = get_linked_deployments(deployments)
        if linked_deployments:
            for deployment_data in linked_deployments.values():
                on_chain_bytecode = self.w3.eth.getCode(
                    to_canonical_address(deployment_data["address"])
                )
                unresolved_linked_refs = normalize_linked_references(
                    deployment_data["runtime_bytecode"]["link_dependencies"]
                )
                resolved_linked_refs = tuple(
                    self._resolve_linked_references(link_ref, deployments)
                    for link_ref in unresolved_linked_refs
                )
                for linked_ref in resolved_linked_refs:
                    validate_linked_references(linked_ref, on_chain_bytecode)

        return Deployments(deployments, all_contract_factories, self.w3)

    @to_tuple
    def _resolve_linked_references(
        self, link_ref: Tuple[int, str, str], deployments: Dict[str, Any]
    ) -> Generator[Tuple[int, bytes], None, None]:
        # No nested deployment: i.e. 'Owned'
        offset, link_type, value = link_ref
        if link_type == "literal":
            yield offset, to_canonical_address(value)
        elif value in deployments:
            yield offset, to_canonical_address(deployments[value]["address"])
        # No nested deployment, but invalid ref
        elif ":" not in value:
            raise BytecodeLinkingError(
                f"Contract instance reference: {value} not found in package's deployment data."
            )
        # Expects child pkg in build_dependencies
        elif value.split(":")[0] not in self.build_dependencies:
            raise BytecodeLinkingError(
                f"Expected build dependency: {value.split(':')[0]} not found "
                "in package's build dependencies."
            )
        # Find and return resolved, nested ref
        else:
            unresolved_linked_ref = value.split(":", 1)[-1]
            build_dependency = self.build_dependencies[value.split(":")[0]]
            yield build_dependency._resolve_link_dependencies(unresolved_linked_ref)
