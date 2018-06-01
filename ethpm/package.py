import json

from typing import (
    Any,
    Dict,
    IO,
)

from web3.eth import Contract
from web3.main import Web3

from ethpm.deployments import Deployments

from ethpm.exceptions import ValidationError

from ethpm.typing import ContractName

from ethpm.utils.contract import (
    compile_contracts,
    generate_contract_factory_kwargs,
    validate_contract_name,
    validate_minimal_contract_data_present,
    validate_w3_instance,
)
from ethpm.utils.deployment_validation import (
    validate_single_matching_uri,
)
from ethpm.utils.ipfs import (
    extract_ipfs_path_from_uri,
    fetch_ipfs_package,
    is_ipfs_uri,
)
from ethpm.utils.package_validation import (
    check_for_build_dependencies,
    validate_package_against_schema,
    validate_package_deployments,
    validate_deployments_are_present,
)


def _load_package_data_from_file(file_obj: IO[str]) -> Dict[str, str]:
    """
    Utility function to load package objects
    from file objects passed to Package.from_file
    """
    try:
        package_data = json.load(file_obj)
    except json.JSONDecodeError as err:
        raise json.JSONDecodeError(
            "Failed to load package data. File is not a valid JSON document.",
            err.doc,
            err.pos,
        )

    return package_data


class Package(object):

    def __init__(self, package_data: Dict[str, Any], w3: Web3=None) -> None:
        """
        A package must be constructed with
        parsed package JSON.
        """
        self.w3 = w3

        if not isinstance(package_data, dict):
            raise TypeError(
                "Package object must be initialized with a dictionary. "
                "Got {0}".format(type(package_data))
            )

        validate_package_against_schema(package_data)
        validate_package_deployments(package_data)
        check_for_build_dependencies(package_data)

        self.package_data = package_data

    def set_default_w3(self, w3: Web3) -> None:
        """
        Set the default Web3 instance.
        """
        self.w3 = w3

    def get_contract_type(self, name: ContractName, w3: Web3=None) -> Contract:
        """
        API to generate a contract factory class.
        """
        current_w3 = None

        if w3 is not None:
            current_w3 = w3
        else:
            current_w3 = self.w3

        validate_contract_name(name)
        validate_w3_instance(current_w3)

        if name in self.package_data['contract_types']:
            contract_data = self.package_data['contract_types'][name]
            validate_minimal_contract_data_present(contract_data)
            contract_kwargs = generate_contract_factory_kwargs(contract_data)
            # compile contracts to get bin for contract factory
            if 'bytecode' not in contract_kwargs:
                bytecode = compile_contracts(
                    name,
                    self.package_data['package_name'],
                    self.package_data['sources'].keys()
                )
                contract_kwargs['bytecode'] = bytecode
            contract_factory = current_w3.eth.contract(**contract_kwargs)
            return contract_factory
        raise ValidationError("Package does not have contract by name: {}.".format(name))

    def __repr__(self) -> str:
        name = self.name
        version = self.version
        return "<Package {0}=={1}>".format(name, version)

    @classmethod
    def from_file(cls, file_path_or_obj: str, w3: Web3) -> 'Package':
        """
        Allows users to create a Package object
        from a filepath
        """
        if isinstance(file_path_or_obj, str):
            with open(file_path_or_obj) as file_obj:
                package_data = _load_package_data_from_file(file_obj)
        elif hasattr(file_path_or_obj, 'read') and callable(file_path_or_obj.read):
            package_data = _load_package_data_from_file(file_path_or_obj)
        else:
            raise TypeError(
                "The Package.from_file method takes either a filesystem path or a file-like object."
                "Got {0} instead.".format(type(file_path_or_obj))
            )

        return cls(package_data, w3)

    @classmethod
    def from_ipfs(cls, ipfs_uri: str) -> 'Package':
        """
        Allows users to create a Package object from
        an IPFS uri.
        TODO: Defaults to Infura gateway, needs extension
        to support other gateways and local nodes
        """
        if is_ipfs_uri(ipfs_uri):
            ipfs_path = extract_ipfs_path_from_uri(ipfs_uri)
            package_data = fetch_ipfs_package(ipfs_path)
        else:
            raise TypeError(
                "The Package.from_ipfs method only accepts a valid IPFS uri."
                "{0} is not a valid IPFS uri.".format(ipfs_uri)
            )

        return cls(package_data)

    @property
    def name(self) -> str:
        return self.package_data['package_name']

    @property
    def version(self) -> str:
        return self.package_data['version']

    #
    # Deployments
    #

    def get_deployments(self, w3: Web3=None) -> 'Deployments':
        """
        API to retrieve instance of deployed contract dependency.
        """
        if w3 is None:
            w3 = self.w3

        validate_w3_instance(w3)
        validate_deployments_are_present(self.package_data)

        all_blockchain_uris = self.package_data["deployments"].keys()
        matching_uri = validate_single_matching_uri(all_blockchain_uris, w3)

        deployments = self.package_data["deployments"][matching_uri]
        all_contract_factories = {
            deployment_data['contract_type']: self.get_contract_type(
                deployment_data['contract_type'],
                w3
            )
            for deployment_data
            in deployments.values()
        }

        return Deployments(deployments, all_contract_factories, w3)
